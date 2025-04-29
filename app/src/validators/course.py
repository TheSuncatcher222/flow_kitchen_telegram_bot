from re import fullmatch

from aiogram.types import PhotoSize

from app.src.database.database import async_session_maker


class CourseParams:
    """
    Параметры курса.
    """

    DESCRIPTION_LEN_MAX: int = 900
    KEYBOARD_COORDINATES_LEN_MAX: int = 5
    PICTURE_FILE_ID_LEN_MAX: int = 256
    TARIFFS_LEN_MAX: int = 1000
    TITLE_LEN_MAX: int = 48


def validate_course_description(value: str) -> str:
    """
    Производит валидацию описания курса.
    """
    value: str = value.strip()
    if value.startswith('/'):
        raise ValueError('Описание курса не должно начинаться с "/".')
    if len(value) > CourseParams.DESCRIPTION_LEN_MAX:
        raise ValueError(
            'Описание курса слишком длинное. '
            f'Максимальная длина - {CourseParams.DESCRIPTION_LEN_MAX} символов. '
            f'Текущая длина - {len(value)} символов.',
        )
    return value


def validate_course_picture(value: PhotoSize) -> str:
    """
    Производит валидацию картинки курса.
    Возвращает ID фото в Telegram.
    """
    if value.width > 1080 or value.height > 1080:
        raise ValueError(
            'Фото слишком большое, должно быть не более 1080x1080. '
            f'Текущее разрешение - {value.width}x{value.height}',
        )
    return value.file_id


async def validate_course_keyboard_coordinates(value: str) -> str:
    """
    Производит валидацию координат курса на клавиатуре.
    """
    # INFO. Циклический импорт.
    from app.src.crud.course import course_crud

    value: str = value.strip()
    async with async_session_maker() as session:
        if await course_crud.retrieve_by_keyboard_coordinates(obj_keyboard_coordinates=value, session=session):
            raise ValueError('Курс с такими координатами на клавиатуре уже существует.')
    value: str = value.strip()
    if not fullmatch(pattern=r'\d{1,2} \d{1,2}', string=value):
        raise ValueError('Координаты должны быть в формате "1 1". Допускаются двузначные числа.')
    return value


def validate_course_tariffs(value: str) -> str:
    """
    Производит валидацию описания тарифов курса.
    """
    value: str = value.strip()
    if value.startswith('/'):
        raise ValueError('Описание тарифов курса не должно начинаться с "/".')
    if len(value) > CourseParams.TARIFFS_LEN_MAX:
        raise ValueError(
            'Описание тарифов курса слишком длинное. '
            f'Максимальная длина - {CourseParams.TARIFFS_LEN_MAX} символов. '
            f'Текущая длина - {len(value)} символов.',
        )
    return value


async def validate_course_title(value: str) -> str:
    """
    Производит валидацию названия курса.
    """
    # INFO. Циклический импорт.
    from app.src.crud.course import course_crud

    value: str = value.strip()
    async with async_session_maker() as session:
        if await course_crud.retrieve_by_title(obj_title=value, session=session):
            raise ValueError('Курс с таким названием уже существует.')
    if value.startswith('/'):
        raise ValueError('Название курса не должно начинаться с "/".')
    if len(value) > CourseParams.TITLE_LEN_MAX:
        raise ValueError(
            'Название курса слишком длинное. '
            f'Максимальная длина - {CourseParams.TITLE_LEN_MAX} символов. '
            f'Текущая длина - {len(value)} символов.',
        )
    return value
