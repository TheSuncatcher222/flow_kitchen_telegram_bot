from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import Select

from app.src.crud.sync_crud.base_sync_crud import BaseSyncCrud
from app.src.database.database import Base
from app.src.models.poll import Poll


class PollSyncCrud(BaseSyncCrud):

    def retrieve_by_title(
        self,
        *,
        obj_title: str,
        session: Session,
    ) -> Poll | None:
        """
        Получает один объект из базы данных по названию.
        """
        query: Select = select(self.model).where(self.model.title == obj_title)
        result: list[Base] = (session.execute(query)).scalars().first()
        return result


poll_sync_crud: PollSyncCrud = PollSyncCrud(
    model=Poll,
    unique_columns=('title',),
    unique_columns_err='Опрос с таким названием в панели управления уже существует',
)
