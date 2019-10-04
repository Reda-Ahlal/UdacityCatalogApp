from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class Movie(Base):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    year = Column(Integer)
    director = Column(String(100))
    description = Column(String(300))
    created_date = Column(DateTime(), default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'director': self.director,
            'description': self.description,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///moviescatalog.db')


Base.metadata.create_all(engine)
