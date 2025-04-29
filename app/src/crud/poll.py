from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import Select

from app.src.database.base_async_crud import (
    AsyncSession,
    BaseAsyncCrud,
)
from app.src.models.poll import Poll


class PollCrud(BaseAsyncCrud):
    """Класс CRUD запросов к базе данных к таблице Poll."""

    async def retrieve_by_title(
        self,
        *,
        obj_title: str,
        session: AsyncSession,
    ) -> Poll | None:
        """Получает один объект из базы данных по title."""
        query: Select = select(Poll).where(Poll.title == obj_title)
        return (await session.execute(query)).scalars().first()


poll_crud: PollCrud = PollCrud(
    model=Poll,
)
