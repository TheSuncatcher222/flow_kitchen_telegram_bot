from typing import TYPE_CHECKING

from app.src.crud.course import course_crud
from app.src.database.database import async_session_maker

if TYPE_CHECKING:
    from app.src.models.course import Course


async def get_all_courses_for_keyboard() -> dict[str, str]:
    """Возвращает словарь названий курсов и их координат на клавиатуре."""
    async with async_session_maker() as session:
        courses: list[Course] = await course_crud.retrieve_all(session=session)
    return {c.title: c.keyboard_coordinates for c in courses}


async def get_all_courses_titles() -> list[str | None]:
    """Возвращает список названий курсов."""
    async with async_session_maker() as session:
        return [c.title for c in await course_crud.retrieve_all(session=session)]
