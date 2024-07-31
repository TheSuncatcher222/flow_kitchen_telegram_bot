from app.src.crud.async_crud.base_async_crud import BaseAsyncCrud
from app.src.models.chat import Chat


class ChatCrud(BaseAsyncCrud):
    """Класс CRUD запросов к базе данных к таблице Poll."""


chat_async_crud: ChatCrud = ChatCrud(
    model=Chat,
    unique_columns=('chat_id',),
    unique_columns_err='Чат с таким id уже добавлен в базу данных',
)
