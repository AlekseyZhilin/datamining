from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table


Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=False)
    posts = relationship(Post)


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=False)
    posts = relationship(Post, secondary=tag_post)
