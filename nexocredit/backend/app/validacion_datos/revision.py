import unicodedata
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RevisionManual(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    id: UUID
    version_anterior: int = Field(ge=0, strict=True)
    estado: Literal['Pendiente', 'Aprobada', 'Rechazada']
    observaciones: str = Field(min_length=1, max_length=2000)
    responsable: str = Field(min_length=1, max_length=120)

    @field_validator('observaciones')
    @classmethod
    def texto_visible(cls, value):
        # Permitir texto Unicode y saltos/tabulaciones; no controles ocultos ni NUL.
        if (not any(not c.isspace() and not unicodedata.category(c).startswith('C') for c in value)
                or any(unicodedata.category(c).startswith('C') and c not in '\n\r\t' for c in value)):
            raise ValueError('Las observaciones deben contener texto visible, sin caracteres de control ocultos.')
        return value
