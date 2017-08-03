import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False)
    picture = Column(String(150))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(32),nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'),nullable=False)
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'),nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category': self.category.name
        }


engine = create_engine('sqlite:///catalog_with_user.db')

Base.metadata.create_all(engine)
