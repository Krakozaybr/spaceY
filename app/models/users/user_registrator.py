from abc import ABC, abstractmethod

from app.models.db_session import create_session
from app.models.users.user import User
from string import ascii_letters, digits


class Validator(ABC):
    error_msg: str

    @abstractmethod
    def validate(self):
        pass

    def error(self):
        return self.error_msg


class LoginValidator(Validator):
    allowed_chars = set(ascii_letters + digits + "_")

    def __init__(self, login: str):
        self.login = login
        self.error_msg = ""

    @staticmethod
    def login_available(login: str):
        if login:
            with create_session() as session:
                return session.query(User).filter(User.login == login).first() is None
        return False

    @staticmethod
    def check_login_length(login: str):
        return 30 >= len(login) > 3

    @classmethod
    def check_login_chars(cls, login: str):
        return set(login) < cls.allowed_chars

    def validate(self):
        if not self.check_login_length(self.login):
            self.error_msg = "Логин должен быть от 4 до 30 символов длинной"
        elif not self.check_login_chars(self.login):
            self.error_msg = "Логин может содержать только латинские символы, цифры и знак нижнего подчеркивания"
        elif not self.login_available(self.login):
            self.error_msg = "Логин уже занят"
        else:
            return True
        return False


class PasswordValidator(Validator):
    def __init__(self, password: str):
        self.password = password
        self.error_msg = ""

    @staticmethod
    def check_password_length(password: str):
        return 8 <= len(password) <= 100

    def validate(self):
        if self.check_password_length(self.password):
            return True
        self.error_msg = "Пароль должен быть от 8 до 100 символов длинной"
        return False


class UserRegistrator:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.error_msg = ""

    @staticmethod
    def check_password(password: str):
        return len(password) > 3

    def register(self, session: "Session", is_student=False, professor=None):

        login_validator = LoginValidator(self.login)
        password_validator = PasswordValidator(self.password)

        if not login_validator.validate():
            self.error_msg = login_validator.error()
            return None

        if not password_validator.validate():
            self.error_msg = password_validator.error()
            return None

        user = User()
        user.set_password(self.password)
        user.login = self.login
        user.is_student = is_student
        if professor is not None:
            user.professor = professor

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def error(self):
        return self.error_msg
