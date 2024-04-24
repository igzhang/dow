import asyncio
from typing import Union
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func

from . import models, schemas


async def get_app_list(db: AsyncSession, page: int, per_page: int, app_name: str, desc: str) -> Union[list[models.App], int]:
    """
    Retrieve data from database table `app`
    """
    offset = (page - 1) * per_page
    stmt = select(models.App)
    if app_name:
        stmt = stmt.where(models.App.app_name.like(f'%{app_name}%'))
    if desc:
        stmt = stmt.where(models.App.desc.like(f'%{desc}%'))
    count_stmt = select(func.count()).select_from(stmt)
    stmt = stmt.order_by(models.App.id.desc()).offset(offset).limit(per_page)

    results = await db.scalars(stmt)
    count = await db.scalar(count_stmt)

    return results, count


async def create_app(db: AsyncSession, create_app_form: schemas.AppCreate):
    """
    create app row in DB
    """
    await db.execute(
        insert(models.App),
        [create_app_form.model_dump()],
    )
    await db.commit()


async def check_app_name_duplicates(db: AsyncSession, app_name: str) -> bool:
    """
    check if app name is exist
    """
    stmt = select(func.count()).where(models.App.app_name == app_name)
    match_row = await db.scalar(stmt)
    return match_row > 0


async def query_app_details(db: AsyncSession, app_id: int) -> models.App | None:
    """
    query one app row in DB
    """
    stmt = select(models.App).where(models.App.id == app_id)
    result = await db.scalar(stmt)
    return result


async def update_app_details(db: AsyncSession, app_id: int, edit_app_form: schemas.AppCreate):
    """
    update field info in table app
    """
    update_stmt = update(models.App).where(models.App.id == app_id).values(**edit_app_form.model_dump())
    await db.execute(update_stmt)
    await db.commit()


async def get_app_env_list(db: AsyncSession, app_id: int) -> list[models.Env]:
    """
    query env list with target app
    """
    stmt = select(models.Env).where(models.Env.app_id == app_id)
    return await db.scalars(stmt)


async def get_build_template_list(db: AsyncSession) -> list[models.BuildTemplate]:
    stmt = select(models.BuildTemplate).order_by(models.BuildTemplate.id)
    return await db.scalars(stmt)


async def edit_build_template(db: AsyncSession, template_id: int, content: str):
    stmt = update(models.BuildTemplate).where(models.BuildTemplate.id == template_id).values(content=content)
    await db.execute(stmt)
    await db.commit()
