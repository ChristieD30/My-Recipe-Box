from app import db
from app.model.users import User

class UserService:
    @staticmethod
    def add_user(username, email, name, password):
        new_user = User(username=username, name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    

    #test