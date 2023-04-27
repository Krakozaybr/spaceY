from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Integer, String, Column, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import backref
from sqlalchemy.util.preloaded import orm
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.abstract import Model
from app.models.db_session import SqlAlchemyBase
from app.utils.utils import media_img_url, static_img_url


class User(SqlAlchemyBase, Model, UserMixin):

    __tablename__ = "users"

    DEFAULT_AVATAR = "default_avatar.png"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    description = Column(String, default="")
    created_at = Column(DateTime, default=datetime.now)
    is_student = Column(Boolean, default=True)
    rating = Column(Integer, default=0)

    professor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    professor = orm.relationship("User", backref="students", remote_side=id)

    is_staff = Column(Boolean, default=False)
    avatar = Column(String, default="")

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password, password)

    def generate_invite(self):
        return

    @property
    def img_url(self):
        if self.avatar:
            return media_img_url(self.avatar)
        return static_img_url(self.DEFAULT_AVATAR)

    @property
    def preview_url(self):
        return f"/users/{self.id}"
