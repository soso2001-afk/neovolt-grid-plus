"""Ingestion batch des CSV Néovolt vers PostgreSQL + journal ingestion_logs."""

import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# job(session, log, data_dir, csv_path?) -> int
IngestJob = Callable[..., int]

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.database import SessionLocal, engine
from api.models import Base, IngestionLog


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def resolve_donnees_dir() -> Path:
    raw = os.getenv("DONNEES_PATH", "../donnees")
    path = Path(raw)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    if (path / "releves_consommation.csv").exists():
        return path
    nested = path / "donnees"
    if (nested / "releves_consommation.csv").exists():
        return nested
    raise FileNotFoundError(
        f"CSV introuvables dans {path} ou {nested}. Dézippez donnees.zip."
    )


def wait_for_db(max_attempts: int = 30) -> None:
    import time

    for i in range(max_attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Base de données prête.")
            return
        except Exception:
            if i == max_attempts - 1:
                raise
            print(f"Attente PostgreSQL ({i + 1}/{max_attempts})…")
            time.sleep(2)


def _write_log(
    session: Session,
    fichier: str,
    table_cible: str,
    statut: str,
    lignes: int | None = None,
    erreur: str | None = None,
) -> IngestionLog:
    log = IngestionLog(
        fichier=fichier,
        table_cible=table_cible,
        statut=statut,
        message_erreur=erreur,
        lignes_ingerees=lignes,
        ingestion_timestamp=utc_now(),
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def truncate_table(table_name: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY'))


def _csv_file(data_dir: Path, csv_path: Path | None, default_name: str) -> Path:
    return csv_path if csv_path is not None else data_dir / default_name


def run_ingestion(
    session: Session,
    fichier: str,
    table_cible: str,
    job: IngestJob,
    data_dir: Path,
    csv_path: Path | None = None,
) -> IngestionLog:
    """Exécute une ingestion ; remplit ingestion_logs (success ou error)."""
    log_name = csv_path.name if csv_path else fichier
    print(f"\n--- {log_name} → {table_cible} ---")
    log = IngestionLog(
        fichier=fichier,
        table_cible=table_cible,
        statut="running",
        ingestion_timestamp=utc_now(),
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    try:
        nb_lignes = job(session, log, data_dir, csv_path)
        log.lignes_ingerees = nb_lignes
        log.statut = "success"
        log.message_erreur = None
        session.commit()
        print(f"  OK — {nb_lignes:,} lignes")
        return log
    except Exception as exc:
        session.rollback()
        err_msg = f"{type(exc).__name__}: {exc}"[:500]
        log = session.get(IngestionLog, log.id)
        if log:
            log.statut = "error"
            log.message_erreur = err_msg
            session.commit()
        else:
            log = _write_log(
                session,
                fichier=fichier,
                table_cible=table_cible,
                statut="error",
                erreur=err_msg,
            )
        print(f"  ERREUR — {err_msg}")
        traceback.print_exc()
        return log


def _prepare_df(
    df: pd.DataFrame,
    log: IngestionLog,
    ts: datetime,
) -> pd.DataFrame:
    df = df.copy()
    df["ingestion_timestamp"] = ts
    df["ingestion_log_id"] = log.id
    return df.where(pd.notnull(df), None)


def _ingest_compteurs(
    session: Session, log: IngestionLog, data_dir: Path, csv_path: Path | None = None
) -> int:
    ts = log.ingestion_timestamp
    df = pd.read_csv(_csv_file(data_dir, csv_path, "compteurs.csv"))
    df["date_pose"] = pd.to_datetime(df["date_pose"], errors="coerce").dt.date
    df = _prepare_df(df, log, ts)
    df.to_sql("compteurs", engine, if_exists="append", index=False, method="multi")
    return len(df)


def _ingest_clients(
    session: Session, log: IngestionLog, data_dir: Path, csv_path: Path | None = None
) -> int:
    ts = log.ingestion_timestamp
    df = pd.read_csv(_csv_file(data_dir, csv_path, "clients.csv"))
    df["date_entree"] = pd.to_datetime(df["date_entree"], errors="coerce").dt.date
    df = _prepare_df(df, log, ts)
    df.to_sql("clients", engine, if_exists="append", index=False, method="multi")
    return len(df)


def _ingest_limit() -> int | None:
    raw = os.getenv("INGEST_LIMIT_ROWS", "").strip()
    if not raw:
        return None
    return int(raw)


def _ingest_releves(
    session: Session, log: IngestionLog, data_dir: Path, csv_path: Path | None = None
) -> int:
    ts = log.ingestion_timestamp
    path = _csv_file(data_dir, csv_path, "releves_consommation.csv")
    limit = _ingest_limit()
    if limit:
        print(f"     (mode test : max {limit:,} lignes — retirer INGEST_LIMIT_ROWS pour tout charger)")

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE releves_consommation"))

    total = 0
    for chunk in pd.read_csv(path, chunksize=25_000):
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce").dt.date
        chunk["consommation_kwh"] = pd.to_numeric(
            chunk["consommation_kwh"], errors="coerce"
        )
        chunk = chunk.drop_duplicates(subset=["id_pdl", "date"], keep="first")
        chunk = _prepare_df(chunk, log, ts)
        if limit is not None:
            remaining = limit - total
            if remaining <= 0:
                break
            chunk = chunk.head(remaining)
        chunk.to_sql(
            "releves_consommation",
            engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=2000,
        )
        total += len(chunk)
        print(f"     … {total:,} lignes", flush=True)
    return total


def _ingest_releves_horaires(
    session: Session, log: IngestionLog, data_dir: Path, csv_path: Path | None = None
) -> int:
    path = _csv_file(data_dir, csv_path, "releves_horaires_echantillon.csv")
    if not path.exists():
        return 0
    ts = log.ingestion_timestamp
    df = pd.read_csv(path)
    df["horodatage"] = pd.to_datetime(df["horodatage"], errors="coerce", utc=True)
    df = _prepare_df(df, log, ts)
    df.to_sql("releves_horaires", engine, if_exists="append", index=False, method="multi")
    return len(df)


def print_logs_summary(session: Session) -> None:
    from sqlalchemy import select

    rows = session.scalars(select(IngestionLog).order_by(IngestionLog.id)).all()
    print("\n=== Journal ingestion_logs ===")
    for r in rows:
        err = f" | erreur: {r.message_erreur}" if r.message_erreur else ""
        lignes = r.lignes_ingerees if r.lignes_ingerees is not None else "-"
        print(
            f"  [{r.id}] {r.fichier} → {r.table_cible} | {r.statut} | "
            f"{lignes} lignes | {r.ingestion_timestamp}{err}"
        )


def main() -> None:
    data_dir = resolve_donnees_dir()
    print(f"Dossier données : {data_dir}")

    wait_for_db()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        jobs = [
            ("compteurs.csv", "compteurs", _ingest_compteurs),
            ("clients.csv", "clients", _ingest_clients),
            ("releves_consommation.csv", "releves_consommation", _ingest_releves),
            (
                "releves_horaires_echantillon.csv",
                "releves_horaires",
                _ingest_releves_horaires,
            ),
        ]
        for fichier, table, fn in jobs:
            run_ingestion(session, fichier, table, fn, data_dir)

        print_logs_summary(session)

        with engine.connect() as conn:
            n = conn.execute(text("SELECT COUNT(*) FROM releves_consommation")).scalar()
        print(f"\nTerminé. {n:,} relevés en base.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
