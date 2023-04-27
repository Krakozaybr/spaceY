import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, scoped_session

from settings import DB_FILE

SqlAlchemyBase = dec.declarative_base()

__factory = None


class CarefulSession(orm.Session):
    def add(self, object_):
        object_session = orm.object_session(object_)
        if object_session and object_session is not self:
            object_session.expunge(object_)
            object_session.close()
        return super().add(object_)


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f"sqlite:///{db_file.strip()}?check_same_thread=False"

    engine = sa.create_engine(conn_str, echo=False)
    __factory = scoped_session(orm.sessionmaker(engine, class_=CarefulSession))

    @sa.event.listens_for(__factory, "after_commit")
    def receive_after_commit(session):
        objects = filter(
            lambda o: hasattr(o, "_prev_session"), session.identity_map.values()
        )
        for object_ in objects:
            prev_session = object_._prev_session()
            if prev_session:
                session.expunge(object_)
                prev_session.add(object_)
                delattr(object_, "_prev_session")

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    if __factory is None:
        global_init(DB_FILE)
    return __factory()
