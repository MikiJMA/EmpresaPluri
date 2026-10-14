"""Validación Pydantic de los datos de entrada de una evaluación crediticia."""
import unicodedata
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SolicitudCredito(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")
    rfc: str = Field(min_length=1, max_length=120)
    ingresos_mensuales: float = Field(gt=0, le=1_000_000_000, strict=True)
    gastos_mensuales: float = Field(ge=0, le=1_000_000_000, strict=True)
    score_buro_actual: int = Field(ge=0, le=1000, strict=True)
    # Opcionales en API para conservar solicitudes antiguas; ausencia no significa cero.
    deuda_actual: float | None = Field(default=None, ge=0, le=1_000_000_000, strict=True)
    pagos_mensuales_creditos: float | None = Field(default=None, ge=0, le=1_000_000_000, strict=True)
    dias_atraso_actual: int | None = Field(default=None, ge=0, le=36500, strict=True)

    @field_validator('rfc')
    @classmethod
    def identificador_util(cls, value):
        # No exigir formato fiscal a identificadores demo ni reescribir el historial.
        if not value.strip() or any(unicodedata.category(c).startswith('C') for c in value):
            raise ValueError('El identificador no puede estar en blanco ni contener caracteres de control.')
        return value

    @field_validator('pagos_mensuales_creditos')
    @classmethod
    def pagos_incluidos_en_gastos(cls, value, info):
        gastos = info.data.get('gastos_mensuales')
        if value is not None and gastos is not None and value > gastos:
            raise ValueError('Los pagos de créditos no pueden superar los gastos mensuales, que deben incluirlos.')
        return value

    @field_validator('dias_atraso_actual')
    @classmethod
    def atraso_con_deuda_pendiente(cls, value, info):
        if value is not None and value > 0 and info.data.get('deuda_actual') == 0:
            raise ValueError('Si existe atraso pendiente, la deuda actual debe ser mayor que cero.')
        return value
