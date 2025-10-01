from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(25), nullable=False)
    password = Column(String(50))  # Simple password storage for now
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recipes = relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    favorites = relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    
    def __init__(self, username, email, name, password=''):
        self.username = username
        self.email = email
        self.name = name
        self.password = password
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
