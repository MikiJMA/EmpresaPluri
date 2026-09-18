"""Validación Pydantic de los datos de entrada de una evaluación crediticia."""
from pydantic import BaseModel, ConfigDict, Field


class SolicitudCredito(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")
    rfc: str = Field(min_length=1)
    ingresos_mensuales: float = Field(gt=0, le=1_000_000_000)
    gastos_mensuales: float = Field(ge=0, le=1_000_000_000)
    score_buro_actual: int = Field(ge=0, le=1000, strict=True)
