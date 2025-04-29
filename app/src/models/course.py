from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.src.database.database import (
    Base,
    TableNames,
)
from app.src.validators.course import CourseParams


class Course(Base):
    """Декларативная модель представления курса."""

    __tablename__ = TableNames.course
    __table_args__ = {'comment': 'Курс'}

    # Primary keys.

    id: Mapped[int] = mapped_column(
        comment='ID',
        primary_key=True,
        autoincrement=True,
    )

    # Fields.

    description: Mapped[str] = mapped_column(
        String(length=CourseParams.DESCRIPTION_LEN_MAX),
        comment='описание курса',
    )
    keyboard_coordinates: Mapped[str] = mapped_column(
        String(length=CourseParams.KEYBOARD_COORDINATES_LEN_MAX),
        comment='координаты на клавиатуре',
        unique=True,
    )
    picture_file_id: Mapped[str] = mapped_column(
        String(length=CourseParams.PICTURE_FILE_ID_LEN_MAX),
        comment='id картинки в Telegram',
    )
    tariffs: Mapped[str] = mapped_column(
        String(length=CourseParams.TARIFFS_LEN_MAX),
        comment='тарифы',
    )
    title: Mapped[str] = mapped_column(
        String(length=CourseParams.TITLE_LEN_MAX),
        comment='название',
        unique=True,
    )
    user_id_telegram: Mapped[int] = mapped_column(
        comment='id пользователя Telegram, кто добавил курс',
    )

    def to_dict_repr(self) -> dict[str, any]:
        """
        Возвращает словарь, представляющий объект Poll.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'tariffs': self.tariffs,
            'picture_file_id': self.picture_file_id,
            'keyboard_coordinates': self.keyboard_coordinates,
            'user_id_telegram': self.user_id_telegram,
        }
