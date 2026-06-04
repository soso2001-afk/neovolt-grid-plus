"""Orchestration du pipeline (lancement, statut, uploads par étape)."""

from __future__ import annotations

import os
import threading
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select

from api.database import SessionLocal, engine
from api.models import Base, IngestionLog
from pipeline.ingest import (
    _ingest_clients,
    _ingest_compteurs,
    _ingest_releves,
    _ingest_releves_horaires,
    resolve_donnees_dir,
    run_ingestion,
    truncate_table,
    wait_for_db,
)
from pipeline.validate import validate_csv_for_step

ROOT = Path(__file__).resolve().parents[1]
STAGING_DIR = Path(os.getenv("UPLOAD_DIR", str(ROOT / "data" / "staging")))

PIPELINE_STEPS: list[dict[str, Any]] = [
    {
        "id": "compteurs",
        "label": "Ingestion compteurs",
        "fichier": "compteurs.csv",
        "table": "compteurs",
        "icon": "📟",
    },
    {
        "id": "clients",
        "label": "Ingestion clients",
        "fichier": "clients.csv",
        "table": "clients",
        "icon": "👥",
    },
    {
        "id": "releves",
        "label": "Ingestion relevés",
        "fichier": "releves_consommation.csv",
        "table": "releves_consommation",
        "icon": "⚡",
    },
    {
        "id": "releves_horaires",
        "label": "Ingestion courbes horaires",
        "fichier": "releves_horaires_echantillon.csv",
        "table": "releves_horaires",
        "icon": "📈",
    },
]

STEP_BY_ID = {s["id"]: s for s in PIPELINE_STEPS}

_STEP_FN = {
    "compteurs": _ingest_compteurs,
    "clients": _ingest_clients,
    "releves": _ingest_releves,
    "releves_horaires": _ingest_releves_horaires,
}


@dataclass
class StepStatus:
    id: str
    label: str
    fichier: str
    table: str
    status: str = "pending"
    lignes: int | None = None
    error: str | None = None
    file_source: str = "default"  # default | custom
    file_name: str = ""


@dataclass
class PipelineStatus:
    state: str = "idle"
    started_at: str | None = None
    finished_at: str | None = None
    message: str | None = None
    steps: list[StepStatus] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "message": self.message,
            "steps": [asdict(s) for s in self.steps],
        }


_lock = threading.Lock()
_status = PipelineStatus()
_thread: threading.Thread | None = None


def _staging_file(step_id: str) -> Path:
    return STAGING_DIR / f"{step_id}__custom.csv"


def _ensure_staging() -> None:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)


def get_step_file_info(step_id: str) -> dict:
    if step_id not in STEP_BY_ID:
        raise ValueError(f"Étape inconnue: {step_id}")
    step = STEP_BY_ID[step_id]
    custom = _staging_file(step_id)
    if custom.exists():
        return {
            "source": "custom",
            "file_name": custom.name,
            "original_default": step["fichier"],
            "size_bytes": custom.stat().st_size,
        }
    return {
        "source": "default",
        "file_name": step["fichier"],
        "original_default": step["fichier"],
        "path_hint": str(resolve_donnees_dir() / step["fichier"]),
    }


def resolve_csv_path(step_id: str, data_dir: Path | None = None) -> Path:
    data_dir = data_dir or resolve_donnees_dir()
    custom, _ = _csv_for_step(step_id, data_dir)
    if custom:
        return custom
    return data_dir / STEP_BY_ID[step_id]["fichier"]


def validate_step_file(step_id: str) -> dict:
    if step_id not in STEP_BY_ID:
        return {"ok": False, "message": f"Étape inconnue: {step_id}"}
    path = resolve_csv_path(step_id)
    return validate_csv_for_step(step_id, path)


def save_upload(step_id: str, filename: str, content: bytes) -> dict:
    if step_id not in STEP_BY_ID:
        return {"ok": False, "error": f"Étape inconnue: {step_id}"}
    if not filename.lower().endswith(".csv"):
        return {"ok": False, "error": "Seuls les fichiers .csv sont acceptés"}
    _ensure_staging()
    dest = _staging_file(step_id)
    dest.write_bytes(content)

    validation = validate_csv_for_step(step_id, dest)
    if not validation["ok"]:
        dest.unlink(missing_ok=True)
        return {
            "ok": False,
            "error": validation["message"],
            "validation": validation,
        }

    return {
        "ok": True,
        "message": validation["message"],
        "file_name": dest.name,
        "size_bytes": len(content),
        "validation": validation,
    }


def clear_upload(step_id: str) -> dict:
    if step_id not in STEP_BY_ID:
        return {"ok": False, "error": f"Étape inconnue: {step_id}"}
    path = _staging_file(step_id)
    if path.exists():
        path.unlink()
    return {"ok": True, "message": "Fichier personnalisé supprimé — retour au CSV par défaut"}


def _csv_for_step(step_id: str, data_dir: Path) -> tuple[Path | None, str]:
    """Retourne (chemin custom ou None, nom pour le log)."""
    step = STEP_BY_ID[step_id]
    custom = _staging_file(step_id)
    if custom.exists():
        return custom, custom.name
    return None, step["fichier"]


def get_status() -> dict:
    with _lock:
        return _status.to_dict()


def get_definition() -> dict:
    nodes = [
        {"id": "source", "type": "source", "label": "Fichiers CSV", "icon": "📂"},
    ]
    for s in PIPELINE_STEPS:
        fi = get_step_file_info(s["id"])
        nodes.append(
            {
                "id": s["id"],
                "type": "activity",
                "label": s["label"],
                "fichier": s["fichier"],
                "table": s["table"],
                "icon": s["icon"],
                "file_source": fi["source"],
                "file_name": fi["file_name"],
            }
        )
    nodes.extend(
        [
            {"id": "postgres", "type": "sink", "label": "PostgreSQL", "icon": "🗄️"},
            {"id": "api", "type": "sink", "label": "API REST", "icon": "🌐"},
        ]
    )
    return {
        "name": "Néovolt Grid+ — Pipeline ingestion",
        "donnees_path": str(resolve_donnees_dir()),
        "staging_path": str(STAGING_DIR),
        "ingest_limit_rows": os.getenv("INGEST_LIMIT_ROWS") or None,
        "nodes": nodes,
        "edges": [
            ["source", "compteurs"],
            ["compteurs", "clients"],
            ["clients", "releves"],
            ["releves", "releves_horaires"],
            ["releves_horaires", "postgres"],
            ["postgres", "api"],
        ],
    }


def _set_status(**kwargs) -> None:
    global _status
    with _lock:
        for k, v in kwargs.items():
            setattr(_status, k, v)


def _update_step(step_id: str, **kwargs) -> None:
    with _lock:
        for s in _status.steps:
            if s.id == step_id:
                for k, v in kwargs.items():
                    setattr(s, k, v)
                break


def _init_steps_status() -> list[StepStatus]:
    steps = []
    for s in PIPELINE_STEPS:
        fi = get_step_file_info(s["id"])
        steps.append(
            StepStatus(
                id=s["id"],
                label=s["label"],
                fichier=fi["file_name"],
                table=s["table"],
                file_source=fi["source"],
                file_name=fi["file_name"],
            )
        )
    return steps


def _run_one_step(
    session,
    data_dir: Path,
    step_id: str,
    truncate: bool,
) -> IngestionLog:
    step_def = STEP_BY_ID[step_id]
    csv_path, log_name = _csv_for_step(step_id, data_dir)
    path = csv_path or (data_dir / step_def["fichier"])
    validation = validate_csv_for_step(step_id, path)
    if not validation["ok"]:
        raise ValueError(validation["message"])

    if truncate:
        truncate_table(step_def["table"])
    return run_ingestion(
        session,
        log_name,
        step_def["table"],
        _STEP_FN[step_id],
        data_dir,
        csv_path,
    )


def _run_pipeline_worker(reset_db: bool, step_ids: list[str] | None) -> None:
    started = datetime.now(timezone.utc).isoformat()
    _set_status(
        state="running",
        started_at=started,
        finished_at=None,
        message=None,
        steps=_init_steps_status(),
    )

    try:
        wait_for_db()
        data_dir = resolve_donnees_dir()
        if reset_db:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)

        session = SessionLocal()
        try:
            for step_def in PIPELINE_STEPS:
                sid = step_def["id"]
                if step_ids and sid not in step_ids:
                    _update_step(sid, status="skipped")
                    continue

                fi = get_step_file_info(sid)
                _update_step(
                    sid,
                    status="running",
                    error=None,
                    fichier=fi["file_name"],
                    file_source=fi["source"],
                    file_name=fi["file_name"],
                )
                log = _run_one_step(session, data_dir, sid, truncate=reset_db)
                if log.statut == "success":
                    _update_step(sid, status="success", lignes=log.lignes_ingerees)
                else:
                    _update_step(
                        sid,
                        status="error",
                        error=(log.message_erreur or "Erreur")[:500],
                    )
                    raise RuntimeError(log.message_erreur or f"Échec {sid}")

            _set_status(
                state="success",
                finished_at=datetime.now(timezone.utc).isoformat(),
                message="Pipeline terminé avec succès",
            )
        finally:
            session.close()
    except Exception as exc:
        _set_status(
            state="error",
            finished_at=datetime.now(timezone.utc).isoformat(),
            message=f"{type(exc).__name__}: {exc}"[:500],
        )
        traceback.print_exc()


def _run_single_step_worker(step_id: str, truncate_table_flag: bool) -> None:
    started = datetime.now(timezone.utc).isoformat()
    steps = _init_steps_status()
    for s in steps:
        if s.id != step_id:
            s.status = "skipped"
    _set_status(state="running", started_at=started, finished_at=None, message=None, steps=steps)

    try:
        wait_for_db()
        data_dir = resolve_donnees_dir()
        fi = get_step_file_info(step_id)
        _update_step(
            step_id,
            status="running",
            fichier=fi["file_name"],
            file_source=fi["source"],
            file_name=fi["file_name"],
        )

        session = SessionLocal()
        try:
            log = _run_one_step(session, data_dir, step_id, truncate_table_flag)
            if log.statut == "success":
                _update_step(step_id, status="success", lignes=log.lignes_ingerees)
                msg = f"Étape {step_id} OK ({log.lignes_ingerees:,} lignes)"
                state = "success"
            else:
                _update_step(
                    step_id,
                    status="error",
                    error=(log.message_erreur or "Erreur")[:500],
                )
                msg = log.message_erreur or "Erreur"
                state = "error"
        finally:
            session.close()

        _set_status(
            state=state,
            finished_at=datetime.now(timezone.utc).isoformat(),
            message=msg[:500],
        )
    except Exception as exc:
        _update_step(step_id, status="error", error=str(exc)[:500])
        _set_status(
            state="error",
            finished_at=datetime.now(timezone.utc).isoformat(),
            message=str(exc)[:500],
        )
        traceback.print_exc()


def _start_worker(target, args: tuple) -> dict:
    global _thread
    with _lock:
        if _status.state == "running":
            return {"ok": False, "error": "Un pipeline est déjà en cours"}
        _thread = threading.Thread(target=target, args=args, daemon=True)
        _thread.start()
    return {"ok": True}


def start_pipeline(reset_db: bool = True, step_ids: list[str] | None = None) -> dict:
    result = _start_worker(_run_pipeline_worker, (reset_db, step_ids))
    if result.get("ok"):
        result["message"] = "Pipeline démarré"
    return result


def start_single_step(step_id: str, truncate_table_flag: bool = True) -> dict:
    if step_id not in STEP_BY_ID:
        return {"ok": False, "error": f"Étape inconnue: {step_id}"}
    result = _start_worker(_run_single_step_worker, (step_id, truncate_table_flag))
    if result.get("ok"):
        result["message"] = f"Ingestion {step_id} démarrée"
    return result
