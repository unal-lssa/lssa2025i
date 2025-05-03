from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Linking table for many-to-many User-Role relationship
user_roles_table = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)

    # Back-reference from Role to User (optional)
    users = relationship("User", secondary=user_roles_table, back_populates="roles")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False) # Store hashed passwords

    # Many-to-many relationship with Role
    roles = relationship("Role", secondary=user_roles_table, back_populates="users")

    def __repr__(self):
        return f"<User(username='{self.username}')>"