
from datetime import time

from sqlalchemy import (
    Date,
    String,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.sql.expression import false as sql_false

from app.src.database.database import (
    Base,
    TableNames,
)
from app.src.utils.translation import translate_days_of_week_from_eng_to_rus
from app.src.validators.poll import PollParams


class Poll(Base):
    """Декларативная модель представления опроса."""

    __tablename__ = TableNames.poll
    __table_args__ = {'comment': 'Опрос'}

    # Primary keys.

    id: Mapped[int] = mapped_column(
        comment='ID',
        primary_key=True,
        autoincrement=True,
    )

    # Fields.

    block_answer_delta_hours: Mapped[int] = mapped_column(
        comment='через сколько часов после публикации блокировать ответы',
        server_default='24',
    )
    chat_id: Mapped[str] = mapped_column(
        String(length=PollParams.CHAT_ID_LEN_MAX),
        comment='id чата/группы Telegram',
    )
    dates_skip: Mapped[list[str]] = mapped_column(
        ARRAY(String(length=PollParams.SKIP_DATE_LEN_MAX)),
        comment='даты для пропуска отправки',
        server_default=text("'{}'::text[]"),
        nullable=True,
    )
    is_allows_anonymous_answers: Mapped[bool] = mapped_column(
        comment='статус анонимных ответов',
    )
    is_allows_multiple_answers: Mapped[bool] = mapped_column(
        comment='статус множественного выбора ответов',
    )
    is_blocked: Mapped[bool] = mapped_column(
        comment='статус блокировки опроса',
        server_default=sql_false(),
    )
    last_send_date: Mapped[Date] = mapped_column(
        Date(),
        comment='дата последней отправки опроса',
        nullable=True,
        server_default=None,
    )
    message_id: Mapped[str] = mapped_column(
        String(length=PollParams.MESSAGE_ID_LEN_MAX),
        comment='id сообщения Telegram',
        nullable=True,
        server_default=None,
    )
    topic: Mapped[str] = mapped_column(
        String(length=PollParams.TOPIC_LEN_MAX),
        comment='тема опроса',
    )
    options: Mapped[list[str]] = mapped_column(
        ARRAY(String(length=PollParams.OPTION_LEN_MAX)),
        comment='варианты ответов',
    )
    send_days_of_week_list: Mapped[list[str]] = mapped_column(
        ARRAY(String(length=PollParams.SEND_DATE_LEN_MAX)),
        comment='дни недели для отправки',
    )
    send_time: Mapped[time] = mapped_column(
        Time(),
        comment='время для отправки',
    )
    title: Mapped[str] = mapped_column(
        String(length=PollParams.TITLE_LEN_MAX),
    )
    user_id_telegram: Mapped[int] = mapped_column(
        comment='id пользователя Telegram, кто отправил опрос',
    )

    def to_dict_repr(
        self,
        represent_days_of_week_in_rus: bool = False,
        represent_date_as_str: bool = False,
        represent_time_as_str: bool = False,
    ) -> dict[str, any]:
        """
        Возвращает словарь, представляющий объект Poll.
        """
        data: dict[str, any] = {
            'id': self.id,
            'block_answer_delta_hours': self.block_answer_delta_hours,
            'chat_id': self.chat_id,
            'dates_skip': self.dates_skip,
            'is_allows_anonymous_answers': self.is_allows_anonymous_answers,
            'is_allows_multiple_answers': self.is_allows_multiple_answers,
            'is_blocked': self.is_blocked,
            'last_send_date': self.last_send_date,
            'message_id': self.message_id,
            'topic': self.topic,
            'options': self.options,
            'send_days_of_week_list': self.send_days_of_week_list,
            'send_time': self.send_time,
            'title': self.title,
            'user_id_telegram': self.user_id_telegram,
        }

        if represent_days_of_week_in_rus:
            data['send_days_of_week_list'] = translate_days_of_week_from_eng_to_rus(days=data['send_days_of_week_list'])

        if represent_date_as_str:
            data['last_send_date'] = str(data['last_send_date'])
            data['dates_skip'] = [
                str(date) for date in data['dates_skip']
            ]
        if represent_time_as_str:
            data['send_time'] = str(data['send_time'])

        return data

    def __str__(self) -> str:
        return self.topic
