from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.util.preloaded import orm

from app.models.abstract import Model
from app.models.db_session import SqlAlchemyBase


class TaskProgress(SqlAlchemyBase, Model):

    __tablename__ = "task_progresses"

    # states
    NOT_VISIBLE = "Закрыт"
    VISIBLE = "Открыт"
    STARTED = "Начат"
    SENT = "Отправлен"
    CHECKED = "Проверен"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String, default=NOT_VISIBLE)
    estimation = Column(Integer, nullable=True)
    answer = Column(Integer, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship("User", backref="progresses")

    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = orm.relationship("Task", backref="progresses")

    @property
    def url(self):
        return f"/task_progress/{self.id}"

    @property
    def can_close(self):
        return self.state in [self.VISIBLE, self.STARTED]

    @property
    def can_estimate(self):
        return self.state in [self.SENT, self.CHECKED]

    @property
    def estimation_url(self):
        return f"/progress/{self.id}"
