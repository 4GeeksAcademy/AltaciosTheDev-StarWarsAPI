from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True,nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    faction = db.Column(db.String(120), nullable=False)
    race = db.Column(db.String(120), nullable=False)
    homeworld = db.Column(db.String(120), nullable=False)

    #if we receive post with new character to be created, need this
    def __init__(self, name,gender,faction,race,homeworld):
        self.name = name
        self.gender = gender
        self.faction = faction
        self.race = race
        self.homeworld = homeworld

    #if we would like to print the character
    def __repr__(self):
        return f'<Character {self.name}>'
    
    #to send as response need to serialize to jsonify later on
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "faction": self.faction,
            "race": self.race,
            "homeworld": self.homeworld,
        }
    
class Planet(db.Model):
    __tablename__="planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    terrain = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable = False)
    location = db.Column(db.String(250), nullable = False)
    key_event = db.Column(db.String(250), nullable = False)

    def __init__(self,name,terrain,description,location,key_event):
        self.name = name,
        self.terrain = terrain,
        self.description = description,
        self.location = location,
        self.key_eventy = key_event

    def __repr__(self):
        return f'<Planet {self.name}>'
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "description":self.description,
            "location": self.location,
            "key_event": self.key_event
        }

