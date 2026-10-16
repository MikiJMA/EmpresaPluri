"""Entradas declaradas compatibles con ENIF; no son consultas al INEGI sobre una persona."""
import math
from pydantic import BaseModel, ConfigDict, Field, field_validator


TIPOS_CREDITO = ['departamental', 'bancaria', 'nomina', 'personal', 'automotriz',
                 'vivienda', 'grupal', 'aplicacion', 'otro']
CATEGORIAS = {'periodicidad': [1, 2, 3, 4], 'ingreso_variable': [1, 2],
              'presupuesto': [1, 2], 'gastos_cubiertos': [1, 2], 'ahorro_emergencia': [1, 2, 3, 4, 5]}
COLUMNAS = ['log_ingreso', *[f'{nombre}_{valor}' for nombre, valores in CATEGORIAS.items() for valor in valores],
            *[f'credito_{tipo}' for tipo in TIPOS_CREDITO]]


class PerfilENIF(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)
    ingreso_laboral: float = Field(gt=0, le=98000)
    periodicidad: int = Field(ge=1, le=4)
    ingreso_variable: int = Field(ge=1, le=2)
    presupuesto: int = Field(ge=1, le=2)
    gastos_cubiertos: int = Field(ge=1, le=2)
    ahorro_emergencia: int = Field(ge=1, le=5)
    creditos: list[str] = Field(min_length=1, max_length=9)

    @field_validator('creditos')
    @classmethod
    def productos_validos(cls, valores):
        if len(set(valores)) != len(valores) or not set(valores) <= set(TIPOS_CREDITO):
            raise ValueError('Selecciona productos distintos de la lista ENIF.')
        return sorted(valores)


def vectorizar(perfil):
    """Una transformación compartida por entrenamiento e inferencia, sin imputaciones."""
    if not isinstance(perfil, PerfilENIF):
        perfil = PerfilENIF.model_validate(perfil)
    return [math.log1p(perfil.ingreso_laboral),
            *[float(getattr(perfil, nombre) == valor) for nombre, valores in CATEGORIAS.items() for valor in valores],
            *[float(tipo in perfil.creditos) for tipo in TIPOS_CREDITO]]
