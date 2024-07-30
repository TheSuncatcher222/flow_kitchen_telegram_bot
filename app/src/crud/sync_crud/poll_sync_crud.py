from app.src.crud.sync_crud.base_sync_crud import BaseSyncCrud
from app.src.models.poll import Poll


class PollSyncCrud(BaseSyncCrud):
    pass


poll_sync_crud: PollSyncCrud = PollSyncCrud(
    model=Poll,
    unique_columns=('title',),
    unique_columns_err='Опрос с таким названием в панели управления уже существует',
)
