from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Compteur, IngestionLog, ReleveConsommation
from api import pipeline_service

app = FastAPI(
    title="Néovolt Grid+ API",
    description="Volet D — exposition des données pour les autres volets",
    version="0.2.0",
)

STATIC_DIR = Path(__file__).parent / "static"


class HealthResponse(BaseModel):
    status: str
    database: str


class CompteurOut(BaseModel):
    id_pdl: str
    id_client: str
    zone: str
    type_client: str
    type_compteur: str
    statut: str

    model_config = {"from_attributes": True}


class ReleveOut(BaseModel):
    id_pdl: str
    date: date
    consommation_kwh: Decimal | None
    zone: str

    model_config = {"from_attributes": True}


class StatsOut(BaseModel):
    compteurs: int
    releves: int


class PipelineRunRequest(BaseModel):
    reset_db: bool = True
    steps: list[str] | None = None


class PipelineRunResponse(BaseModel):
    ok: bool
    message: str | None = None
    error: str | None = None


class StepRunRequest(BaseModel):
    truncate_table: bool = True


class IngestionLogOut(BaseModel):
    id: int
    fichier: str
    table_cible: str
    statut: str
    message_erreur: str | None
    lignes_ingerees: int | None
    ingestion_timestamp: datetime

    model_config = {"from_attributes": True}


@app.get("/")
def root():
    return RedirectResponse(url="/studio")


@app.get("/studio")
def pipeline_studio():
    return FileResponse(STATIC_DIR / "studio.html")


@app.get("/api/v1/pipeline/definition")
def pipeline_definition():
    return pipeline_service.get_definition()


@app.get("/api/v1/pipeline/status")
def pipeline_status():
    return pipeline_service.get_status()


@app.post("/api/v1/pipeline/run", response_model=PipelineRunResponse)
def pipeline_run(body: PipelineRunRequest):
    result = pipeline_service.start_pipeline(
        reset_db=body.reset_db,
        step_ids=body.steps,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=409, detail=result.get("error"))
    return PipelineRunResponse(ok=True, message=result.get("message"))


@app.post("/api/v1/pipeline/steps/{step_id}/upload")
async def upload_step_file(step_id: str, file: UploadFile = File(...)):
    content = await file.read()
    result = pipeline_service.save_upload(step_id, file.filename or "upload.csv", content)
    if not result.get("ok"):
        return JSONResponse(status_code=400, content=result)
    return result


@app.delete("/api/v1/pipeline/steps/{step_id}/upload")
def delete_step_upload(step_id: str):
    result = pipeline_service.clear_upload(step_id)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.get("/api/v1/pipeline/steps/{step_id}/file")
def step_file_info(step_id: str):
    try:
        return pipeline_service.get_step_file_info(step_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/api/v1/pipeline/steps/{step_id}/validate")
def validate_step_csv(step_id: str):
    result = pipeline_service.validate_step_file(step_id)
    if step_id not in pipeline_service.STEP_BY_ID:
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@app.post("/api/v1/pipeline/steps/{step_id}/run", response_model=PipelineRunResponse)
def run_single_step(step_id: str, body: StepRunRequest):
    result = pipeline_service.start_single_step(
        step_id, truncate_table_flag=body.truncate_table
    )
    if not result.get("ok"):
        raise HTTPException(status_code=409, detail=result.get("error"))
    return PipelineRunResponse(ok=True, message=result.get("message"))


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    try:
        db.scalar(select(func.count()).select_from(Compteur))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
    )


@app.get("/api/v1/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    nb_compteurs = db.scalar(select(func.count()).select_from(Compteur)) or 0
    nb_releves = (
        db.scalar(select(func.count()).select_from(ReleveConsommation)) or 0
    )
    return StatsOut(compteurs=nb_compteurs, releves=nb_releves)


@app.get("/api/v1/pdl", response_model=list[CompteurOut])
def list_pdl(
    zone: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = select(Compteur)
    if zone:
        q = q.where(Compteur.zone == zone)
    q = q.offset(offset).limit(limit)
    return list(db.scalars(q).all())


@app.get("/api/v1/ingestion/logs", response_model=list[IngestionLogOut])
def list_ingestion_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = (
        select(IngestionLog)
        .order_by(IngestionLog.ingestion_timestamp.desc())
        .limit(limit)
    )
    return list(db.scalars(q).all())


@app.get("/api/v1/pdl/{id_pdl}", response_model=CompteurOut)
def get_pdl(id_pdl: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Compteur).where(Compteur.id_pdl == id_pdl))
    if not row:
        raise HTTPException(status_code=404, detail="PDL introuvable")
    return row


@app.get("/api/v1/pdl/{id_pdl}/releves", response_model=list[ReleveOut])
def get_releves(
    id_pdl: str,
    date_debut: date | None = None,
    date_fin: date | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if not db.scalar(select(Compteur).where(Compteur.id_pdl == id_pdl)):
        raise HTTPException(status_code=404, detail="PDL introuvable")

    q = select(ReleveConsommation).where(ReleveConsommation.id_pdl == id_pdl)
    if date_debut:
        q = q.where(ReleveConsommation.date >= date_debut)
    if date_fin:
        q = q.where(ReleveConsommation.date <= date_fin)
    q = q.order_by(ReleveConsommation.date).offset(offset).limit(limit)
    return list(db.scalars(q).all())


@app.get("/api/v1/zones/{zone}/aggregats")
def agregats_zone(
    zone: str,
    db: Session = Depends(get_db),
):
    row = db.execute(
        select(
            func.count(ReleveConsommation.id).label("nb_releves"),
            func.avg(ReleveConsommation.consommation_kwh).label("conso_moy_kwh"),
            func.sum(ReleveConsommation.consommation_kwh).label("conso_tot_kwh"),
        ).where(ReleveConsommation.zone == zone)
    ).one()
    return {
        "zone": zone,
        "nb_releves": row.nb_releves or 0,
        "consommation_moyenne_kwh": float(row.conso_moy_kwh or 0),
        "consommation_totale_kwh": float(row.conso_tot_kwh or 0),
    }
