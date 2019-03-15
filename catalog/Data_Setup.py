import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class ProductName(Base):
    __tablename__ = 'productname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="productname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class ModuleName(Base):
    __tablename__ = 'modulename'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    rating = Column(String(150))
    color = Column(String(150))
    discount = Column(String(150))
    price = Column(String(10))
    materialtype = Column(String(250))
    date = Column(DateTime, nullable=False)
    productnameid = Column(Integer, ForeignKey('productname.id'))
    productname = relationship(
        ProductName, backref=backref('modulename', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="modulename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'rating': self. rating,
            'color': self. color,
            'discount': self. discount,
            'price': self. price,
            'materialtype': self. materialtype,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///fashion.db')
Base.metadata.create_all(engin)
