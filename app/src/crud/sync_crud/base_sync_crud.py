"""
Модуль базового класса синхронных CRUD запросов в базу данных.
"""

from sqlalchemy.sql import (
    delete,
    select,
    update,
)
from sqlalchemy.sql.dml import (
    Delete,
    Update,
)
from sqlalchemy.sql.selectable import Select

from app.src.database.database import Base

PAGINATION_LIMIT_DEFAULT: int = 15
PAGINATION_OFFSET_DEFAULT: int = 0


class BaseSyncCrud():
    """Базовый класс синхронных CRUD запросов к базе данных."""

    def __init__(
        self,
        *,
        model: Base,
        unique_columns: tuple[str] = None,
        unique_columns_err: str = 'Объект уже существует',
    ):
        self.model = model
        self.unique_columns_err = unique_columns_err
        self.unique_columns = unique_columns

    def create(
        self,
        *,
        obj_data: dict[str, any],
        # TODO. Узнать тип.
        session: any,
        perform_cleanup: bool = True,
        perform_commit: bool = True,
    ) -> Base:
        self._check_unique(obj_data=obj_data, session=session)

        if perform_cleanup:
            obj_data: dict[str, any] = self._clean_obj_data_non_model_fields(obj_data=obj_data)

        obj: Base = self.model(**obj_data)
        session.add(self.model(**obj_data))

        if perform_commit:
            session.commit()

        return obj

    def retrieve_all(
        self,
        *,
        limit: int = PAGINATION_LIMIT_DEFAULT,
        offset: int = PAGINATION_OFFSET_DEFAULT,
        session: any,
    ) -> list[Base]:
        """Получает несколько объектов из базы данных."""
        query: Select = select(self.model).limit(limit).offset(offset)
        result: list[Base] = (session.execute(query)).scalars().all()
        return result

    def update_by_id(
        self,
        *,
        obj_id: int,
        obj_data: dict[str, any],
        session: any,
        perform_check_unique: bool = True,
        perform_cleanup: bool = True,
        perform_commit: bool = True,
    ) -> Base:
        if perform_check_unique:
            self._check_unique(obj_data=obj_data, session=session)

        if perform_cleanup:
            obj_data: dict[str, any] = self._clean_obj_data_non_model_fields(obj_data=obj_data)

        stmt: Update = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**obj_data)
            .returning(self.model)
        )
        obj: Base = (session.execute(stmt)).scalars().first()

        if perform_commit:
            session.commit()

        return obj

    def delete_by_id(
        self,
        *,
        obj_id: int,
        session: any,
        perform_commit: bool = True,
    ) -> None:
        """
        Удаляет один объект из базы данных по указанному id.
        """
        stmt: Delete = delete(self.model).where(self.model.id == obj_id)
        session.execute(stmt)

        if perform_commit:
            session.commit()

        return

    def _check_unique(
        self,
        *,
        obj_data: dict[str, any],
        session: any,
    ) -> None:
        """Проверяет уникальность переданных значений."""
        if self.unique_columns is None:
            return

        conditions: list = []
        for column_name in self.unique_columns:
            conditions.append(getattr(self.model, column_name) == obj_data[column_name])
        query: Select = select(self.model).filter(*conditions)

        if len((session.execute(query)).scalars().all()) != 0:
            raise ValueError(self.unique_columns_err)

        return

    def _clean_obj_data_non_model_fields(
        self,
        *,
        obj_data: dict[str, any],
    ) -> dict[str, any]:
        """
        Удаляет из переданных данных поля, которые не являются колонками модели.
        Возвращает новый словарь obj_data без удаленных полей.

        Атрибуты:
            obj_data: dict[str, any] - данные для обновления объекта
        """
        model_valid_columns: set[str] = {
            col.name
            for col
            in self.model.__table__.columns
        }
        return {
            k: v
            for k, v
            in obj_data.items()
            if k in model_valid_columns
        }
