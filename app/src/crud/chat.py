from sqlalchemy.sql import (
    delete,
    select,
)
from sqlalchemy.sql.dml import Delete
from sqlalchemy.sql.selectable import Select

from app.src.database.base_async_crud import (
    AsyncSession,
    BaseAsyncCrud,
)
from app.src.models.chat import Chat


class ChatCrud(BaseAsyncCrud):
    """Класс CRUD запросов к базе данных к таблице Chat."""

    async def retrieve_by_chat_id(
        self,
        *,
        obj_chat_id: int,
        session: AsyncSession,
    ) -> Chat | None:
        query: Select = select(Chat).where(Chat.chat_id == obj_chat_id)
        return (await session.execute(query)).scalars().first()

    async def delete_by_chat_id(
        self,
        *,
        chat_id: int,
        session: AsyncSession,
        perform_commit: bool = True,
    ) -> None:
        stmt: Delete = delete(Chat).where(Chat.chat_id == chat_id)
        await session.execute(stmt)

        if perform_commit:
            await session.commit()


chat_crud: ChatCrud = ChatCrud(
    model=Chat,
    unique_columns=('chat_id',),
    unique_columns_err='Чат с таким id уже добавлен в базу данных',
)
