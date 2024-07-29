from typing import Annotated
from pydantic import UUID4, Field
from workout_api.contrib.schemas import BaseSchema

class CentroTreinamentoIn(BaseSchema):
    nome: Annotated[str, Field(description='Nome centro de treinamento', example='CT corinthians', max_length=20)]
    endereco: Annotated[str, Field(description='Endereco do ct', example='Rua x, 101 av soberrbo', max_length=60)]
    proprietario: Annotated[str, Field(description='Proprietario do centro de treinamento', example='juvenal', max_length=30)]

class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[str, Field(description='Nome do centro de treinamento', example='CT king', max_length=20)]

class CentroTreinamentoOut(CentroTreinamentoIn):
    id: Annotated[UUID4, Field(description='Identificador centro de treinamento')]




