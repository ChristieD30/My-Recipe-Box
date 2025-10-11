from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    ingredients = Column(String(500), nullable=False)
    instructions = Column(String(1000), nullable=False)  # Changed to nullable=False since it's required
    category = Column(String(50), nullable=True)  # New category field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Made nullable
    
    user = relationship('User', back_populates='recipes')
    favorites = relationship('Favorite', back_populates='recipe', cascade='all, delete-orphan')

    def __init__(self, *, name, ingredients, instructions, category, user_id=None):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.category = category
        self.user_id = user_id

    def __repr__(self):
        return f'<Recipe {self.name!r}>'
    

    def to_dict(self):
        return {
            'recipe_id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'category': self.category,
            'user_id': self.user_id
        }