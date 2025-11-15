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
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Fixed - removed extra comma
    image_location = Column(String(255), nullable=True) 
    prep_time = Column(Integer, nullable=True)  # in minutes
    cook_time = Column(Integer, nullable=True)  # in minutes
    total_time = Column(Integer, nullable=True)  # in minutes
    servings = Column(Integer, nullable=True)  # number of servings
    
    user = relationship('User', back_populates='recipes')
    favorites = relationship('Favorite', back_populates='recipe', cascade='all, delete-orphan')
    
    def __init__(self, *, name, ingredients, instructions, category, user_id=None, prep_time=None, cook_time=None, total_time=None, servings=None, image_location=None):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.category = category
        self.user_id = user_id
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.total_time = total_time
        self.servings = servings
        self.image_location = image_location

    def __repr__(self):
        return f'<Recipe {self.name!r}>'

    def to_dict(self):
        # Include additional_info fields if available
        info = self.additional_info
        return {
            'recipe_id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'category': self.category,
            'user_id': self.user_id,
            'prep_time': info.prep_time if info else None,
            'cook_time': info.cook_time if info else None,
            'total_time': info.total_time if info else None,
            'servings': info.servings if info else None,
            'image_location': self.image_location,
        }