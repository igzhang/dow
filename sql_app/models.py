from sqlalchemy import Boolean, Column, Text, Integer, String, SmallInteger

from .database import Base


class App(Base):
    __tablename__ = "app"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String, unique=True, index=True)
    app_type = Column(String)
    output = Column(String)
    git_url = Column(String)
    desc = Column(String, default='')


class Env(Base):
    __tablename__ = "env"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, index=True)
    name = Column(String)
    domain = Column(String)
    context = Column(String)
    desc = Column(String)
    build_shell = Column(String)


class BuildTemplate(Base):
    __tablename__ = "build_template"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_type = Column(String(length=10), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    content = Column(Text, nullable=False)
