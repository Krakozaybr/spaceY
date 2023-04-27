from datetime import datetime, timedelta

from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.util.preloaded import orm

from app.models.abstract import Model
from app.models.db_session import SqlAlchemyBase


class Invite(SqlAlchemyBase, Model):

    __tablename__ = "invites"

    LIFE_TIME = timedelta(days=15)

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime, default=datetime.now)
    url = Column(String, unique=True)

    @property
    def invite_url(self):
        return f"/invite/{self.url}"

    professor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    professor = orm.relationship("User", backref="invite_urls")
