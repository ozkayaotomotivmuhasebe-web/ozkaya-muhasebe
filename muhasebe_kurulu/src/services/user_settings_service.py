import json
from src.database.db import session_scope
from src.database.models import UserSetting


class UserSettingsService:
    """Kullanici ayarlari servisi"""

    @staticmethod
    def get_setting(user_id, key, default=None):
        with session_scope() as session:
            setting = session.query(UserSetting).filter_by(user_id=user_id, key=key).first()
            if setting and setting.value is not None:
                return setting.value
            return default

    @staticmethod
    def get_json_setting(user_id, key, default=None):
        value = UserSettingsService.get_setting(user_id, key, None)
        if value is None:
            return default
        try:
            return json.loads(value)
        except Exception:
            return default

    @staticmethod
    def set_setting(user_id, key, value):
        with session_scope() as session:
            setting = session.query(UserSetting).filter_by(user_id=user_id, key=key).first()
            if not setting:
                setting = UserSetting(user_id=user_id, key=key, value=value)
                session.add(setting)
            else:
                setting.value = value

    @staticmethod
    def set_json_setting(user_id, key, value):
        payload = json.dumps(value, ensure_ascii=False)
        UserSettingsService.set_setting(user_id, key, payload)
