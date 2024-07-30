from app.src.crud.async_crud.base_async_crud import BaseAsyncCrud
from app.src.models.poll import Poll


class PoolCrud(BaseAsyncCrud):
    """Класс CRUD запросов к базе данных к таблице Poll."""


poll_async_crud: PoolCrud = PoolCrud(
    model=Poll,
    unique_columns=('title',),
    unique_columns_err='Опрос с таким названием в панели управления уже существует',
)
