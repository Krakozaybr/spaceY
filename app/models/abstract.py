from sqlalchemy_serializer import SerializerMixin


class Model(SerializerMixin):
    def save_model(self, session):
        session.add(self)
        session.commit()
        session.refresh(self)
