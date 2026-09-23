from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RevisionManual(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    id: UUID
    version_anterior: int = Field(ge=0, strict=True)
    estado: Literal['Pendiente', 'Aprobada', 'Rechazada']
    observaciones: str = Field(min_length=1, max_length=2000)
    responsable: str = Field(min_length=1, max_length=120)
