import sqlalchemy.dialects.mssql.pymssql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, VARCHAR, INT
LENGHT = 100

Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", INT, ForeignKey("post.id")),
    Column("tag_id", INT, ForeignKey("tag.id")),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(INT, primary_key=True, autoincrement=True)
    url = Column(String(LENGHT), nullable=False, unique=True)
    title = Column(String(LENGHT), nullable=False, unique=False)
    author_id = Column(INT, ForeignKey("author.id"))
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)


class Author(Base):
    __tablename__ = "author"
    id = Column(INT, primary_key=True, autoincrement=True)
    url = Column(String(LENGHT), nullable=False, unique=True)
    name = Column(String(LENGHT), nullable=False, unique=False)
    posts = relationship(Post)


class Tag(Base):
    __tablename__ = "tag"
    id = Column(INT, primary_key=True, autoincrement=True)
    url = Column(String(LENGHT), nullable=False, unique=True)
    name = Column(String(LENGHT), nullable=False, unique=False)
    posts = relationship(Post, secondary=tag_post)
