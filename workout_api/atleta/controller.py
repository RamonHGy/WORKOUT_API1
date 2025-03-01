from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.future import select

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.categorias.models import CategoriaModel
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.models import AtletaModel
from workout_api.centro_de_treinamento.models import CentroTreinamentoModel  # Importar o modelo se necessário

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn = Body(...)
): 
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(select(CategoriaModel).filter_by(nome=categoria_nome))).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {categoria_nome} não foi encontrada'
        )
    
    centro_treinamento= (await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado'
        )
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id


        db_session.add(atleta_model)
        await db_session.commit()
    except Exception:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ocorreu um erro ao inserir os dados no banco.'
         )
    
    return atleta_out
    
@router.get(
    '/', 
    summary='Consultar todos atletas',
    status_code=status.HTTP_200_OK,
    response_model= list[AtletaOut],           
)
async def query(
    db_session: DatabaseDependency,
    nome: Optional[str] = Query(None, description='nome do atleta'),
    cpf: Optional[str] = Query(None, description='Cpf do atleta')
    ) -> list[AtletaOut]:
    query = select(AtletaModel)
    if nome:
        query = query.filter(AtletaModel.nome == nome)
    if cpf:
        query = query.filter(AtletaModel.cpf == cpf)

    result = await db_session.execute(query)
    atletas = result.scalars().all()
    
    return [AtletaOut.model_validate(atleta) for atleta in atletas]

@router.get(
    '/{id}', 
    summary='Consultar atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model= AtletaOut,           
)

@router.patch(
    '/{id}', 
    summary='Editar dados do atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model= AtletaOut,           
)
async def query_id(id: UUID4, db_session: DatabaseDependency,
    atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:

    result = await db_session.execute(select(AtletaModel).filter(AtletaModel.id==id))
    atleta: AtletaOut = result.scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta

@router.delete(
    '/{id}', 
    summary='Deletar um atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)

async def query_id(id: UUID4, db_session: DatabaseDependency) -> None:
    result = await db_session.execute(select(AtletaModel).filter(AtletaModel.id==id))
    atleta: AtletaOut = result.scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()

    return None