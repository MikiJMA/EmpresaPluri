from datetime import date, datetime, timezone
from decimal import Decimal
import re
import unicodedata
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator, model_validator


def hoy_utc():
    return datetime.now(timezone.utc).date()


def dinero(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError('Se requiere un importe decimal.')
    if not re.fullmatch(r'\d{1,10}(?:\.\d{1,2})?', str(value)):
        raise ValueError('Usa como máximo dos decimales, sin exponentes ni separadores.')
    return Decimal(str(value)).quantize(Decimal('.01'))


def fecha_iso(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Usa una fecha YYYY-MM-DD.')
    return date.fromisoformat(value)


Monto = Annotated[Decimal, BeforeValidator(dinero), Field(gt=0, le=1_000_000_000)]
Fecha = Annotated[date, BeforeValidator(fecha_iso)]


class CuotaPlan(BaseModel):
    model_config = ConfigDict(extra='forbid')
    vencimiento: Fecha
    importe: Monto


class NuevoCredito(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    id: UUID
    evaluacion_id: UUID
    concepto: str = Field(min_length=1, max_length=100)
    fecha_apertura: Fecha
    monto_total_pactado: Monto
    cuotas: list[CuotaPlan] = Field(min_length=1, max_length=60)

    @field_validator('concepto')
    @classmethod
    def texto(cls, value):
        if not value.strip() or any(unicodedata.category(c).startswith('C') for c in value):
            raise ValueError('Escribe un concepto visible sin caracteres de control.')
        return value

    @model_validator(mode='after')
    def coherencia(self):
        if self.fecha_apertura > hoy_utc():
            raise ValueError('La apertura no puede estar en el futuro.')
        fechas = [c.vencimiento for c in self.cuotas]
        if fechas != sorted(set(fechas)) or fechas[0] < self.fecha_apertura:
            raise ValueError('Las cuotas deben tener fechas únicas, ordenadas y no anteriores a la apertura.')
        if sum((c.importe for c in self.cuotas), Decimal(0)) != self.monto_total_pactado:
            raise ValueError('La suma de cuotas debe coincidir con el monto total pactado.')
        return self


class NuevoPago(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    cuota_id: UUID
    importe: Monto
    fecha_pago: Fecha

    @field_validator('fecha_pago')
    @classmethod
    def no_futuro(cls, value):
        if value > hoy_utc():
            raise ValueError('No se pueden registrar pagos futuros como realizados.')
        return value


class AtenderAlerta(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    id: UUID
    version_anterior: int = Field(ge=1, strict=True)
    observaciones: str = Field(min_length=1, max_length=1000)

    @field_validator('observaciones')
    @classmethod
    def texto(cls, value):
        from backend.app.validacion_datos.revision import RevisionManual
        return RevisionManual.texto_visible(value)
