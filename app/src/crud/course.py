from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import Select

from app.src.database.base_async_crud import (
    AsyncSession,
    BaseAsyncCrud,
)
from app.src.models.course import Course


class CourseCrud(BaseAsyncCrud):
    """Класс CRUD запросов к базе данных к таблице Course."""

    async def retrieve_by_keyboard_coordinates(
        self,
        *,
        obj_keyboard_coordinates: str,
        session: AsyncSession,
    ) -> Course | None:
        """Получает один объект из базы данных по keyboard_coordinates."""
        query: Select = select(Course).where(Course.keyboard_coordinates == obj_keyboard_coordinates)
        return (await session.execute(query)).scalars().first()

    async def retrieve_by_title(
        self,
        *,
        obj_title: str,
        session: AsyncSession,
    ) -> Course | None:
        """Получает один объект из базы данных по title."""
        query: Select = select(Course).where(Course.title == obj_title)
        return (await session.execute(query)).scalars().first()


course_crud: CourseCrud = CourseCrud(
    model=Course,
    unique_columns=('title',),
    unique_columns_err='Курс с таким названием уже добавлен в базу данных',
)
