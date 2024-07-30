from app.src.config.config import settings


def check_if_user_is_admin(user_id: int | str) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    """
    if str(user_id) in settings.BOT_ADMIN_IDS.split(','):
        return True
    return False
