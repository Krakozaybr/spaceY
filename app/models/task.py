import json
from typing import List

from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.util.preloaded import orm

from app.models.abstract import Model
from app.models.db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, Model):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    max_estimation = Column(Integer, default=10)
    title = Column(String)
    description = Column(String)
    value = Column(Integer)

    # test
    question = Column(String, nullable=True)
    # text
    text = Column(String, nullable=True)
    # scheme
    image = Column(String, nullable=True)  # path to img
    # video
    video = Column(String, nullable=True)  # path to video

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship("User", backref="tasks")

    def set_variants(self, vals: List[str]):
        self.variants_json = json.dumps(vals)

    @property
    def variants(self):
        return json.loads(self.variants_json)

    @property
    def url(self):
        return f"/task/{self.id}"
