from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class IngestionLog(Base):
    """Journal de chaque ingestion de fichier (succès ou erreur)."""

    __tablename__ = "ingestion_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fichier: Mapped[str] = mapped_column(String(255), nullable=False)
    table_cible: Mapped[str] = mapped_column(String(100), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False)  # success | error
    message_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)
    lignes_ingerees: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class Compteur(Base):
    __tablename__ = "compteurs"
    __table_args__ = (UniqueConstraint("id_pdl", name="uq_compteurs_id_pdl"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingestion_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ingestion_logs.id"), nullable=False
    )

    id_pdl: Mapped[str] = mapped_column(String(20), nullable=False)
    id_client: Mapped[str] = mapped_column(String(20), nullable=False)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)
    type_client: Mapped[str] = mapped_column(String(30), nullable=False)
    puissance_souscrite_kva: Mapped[int | None] = mapped_column(Integer, nullable=True)
    type_chauffage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    type_compteur: Mapped[str] = mapped_column(String(20), nullable=False)
    date_pose: Mapped[date | None] = mapped_column(Date, nullable=True)
    statut: Mapped[str] = mapped_column(String(20), nullable=False)


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (UniqueConstraint("id_client", name="uq_clients_id_client"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingestion_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ingestion_logs.id"), nullable=False
    )

    id_client: Mapped[str] = mapped_column(String(20), nullable=False)
    segment: Mapped[str] = mapped_column(String(30), nullable=False)
    commune: Mapped[str] = mapped_column(String(50), nullable=False)
    code_postal: Mapped[str] = mapped_column(String(10), nullable=False)
    date_entree: Mapped[date | None] = mapped_column(Date, nullable=True)
    nb_personnes_foyer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    surface_m2: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ReleveConsommation(Base):
    __tablename__ = "releves_consommation"
    __table_args__ = (
        UniqueConstraint("id_pdl", "date", name="uq_releves_pdl_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingestion_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ingestion_logs.id"), nullable=False
    )

    id_pdl: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    consommation_kwh: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)


class ReleveHoraire(Base):
    __tablename__ = "releves_horaires"
    __table_args__ = (
        UniqueConstraint("id_pdl", "horodatage", name="uq_releves_horaires_pdl_ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingestion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingestion_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ingestion_logs.id"), nullable=False
    )

    id_pdl: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    horodatage: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consommation_kwh: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
