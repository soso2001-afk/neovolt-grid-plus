"""Validation des colonnes CSV avant ingestion."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Colonnes attendues (dictionnaire Néovolt / modèles SQLAlchemy)
STEP_SCHEMAS: dict[str, dict[str, list[str]]] = {
    "compteurs": {
        "required": [
            "id_pdl",
            "id_client",
            "zone",
            "type_client",
            "type_compteur",
            "statut",
        ],
        "optional": ["puissance_souscrite_kva", "type_chauffage", "date_pose"],
    },
    "clients": {
        "required": [
            "id_client",
            "segment",
            "commune",
            "code_postal",
            "date_entree",
        ],
        "optional": ["nb_personnes_foyer", "surface_m2"],
    },
    "releves": {
        "required": ["id_pdl", "date", "consommation_kwh", "zone"],
        "optional": [],
    },
    "releves_horaires": {
        "required": ["id_pdl", "horodatage", "consommation_kwh"],
        "optional": ["zone"],
    },
}


def _normalize_columns(columns: list[str]) -> list[str]:
    return [str(c).strip().lstrip("\ufeff") for c in columns]


def _count_data_rows(path: Path) -> int:
    """Compte les lignes de données (hors en-tête) sans charger tout le fichier en RAM."""
    with path.open("r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        return sum(1 for _ in f)


def validate_csv_for_step(step_id: str, csv_path: Path) -> dict:
    """
    Vérifie qu'un CSV correspond au schéma de l'étape.
    Retourne un dict avec ok, message, colonnes manquantes, etc.
    """
    if step_id not in STEP_SCHEMAS:
        return {"ok": False, "message": f"Étape inconnue : {step_id}"}

    if not csv_path.exists():
        return {"ok": False, "message": f"Fichier introuvable : {csv_path}"}

    if csv_path.stat().st_size == 0:
        return {"ok": False, "message": "Le fichier est vide"}

    schema = STEP_SCHEMAS[step_id]
    required = schema["required"]
    optional = schema.get("optional", [])

    try:
        header = pd.read_csv(csv_path, nrows=0, encoding="utf-8")
    except Exception as exc:
        return {
            "ok": False,
            "message": f"Impossible de lire le CSV : {exc}",
        }

    found = _normalize_columns(list(header.columns))
    if not found:
        return {"ok": False, "message": "Aucune colonne détectée (en-tête manquant ?)"}

    if len(found) != len(set(found)):
        dupes = [c for c in found if found.count(c) > 1]
        return {
            "ok": False,
            "message": f"Colonnes en double dans l'en-tête : {', '.join(sorted(set(dupes)))}",
            "columns_found": found,
        }

    missing = [c for c in required if c not in found]
    allowed = set(required) | set(optional)
    unexpected = [c for c in found if c not in allowed]

    try:
        row_count = _count_data_rows(csv_path)
    except OSError as exc:
        return {"ok": False, "message": f"Erreur lecture fichier : {exc}"}

    if row_count == 0:
        return {
            "ok": False,
            "message": "Le fichier ne contient aucune ligne de données",
            "columns_found": found,
            "row_count": 0,
        }

    result = {
        "ok": len(missing) == 0,
        "step_id": step_id,
        "file": csv_path.name,
        "columns_found": found,
        "required_columns": required,
        "optional_columns": optional,
        "missing_columns": missing,
        "unexpected_columns": unexpected,
        "row_count": row_count,
    }

    if missing:
        result["message"] = (
            f"Colonnes obligatoires manquantes : {', '.join(missing)}"
        )
    elif unexpected:
        result["message"] = (
            f"Fichier valide ({row_count:,} lignes). "
            f"Colonnes non reconnues (ignorées à l'import) : {', '.join(unexpected)}"
        )
        result["warnings"] = unexpected
    else:
        result["message"] = f"Fichier valide — {row_count:,} lignes, schéma OK"

    return result
