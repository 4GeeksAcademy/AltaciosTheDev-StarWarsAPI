from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    #if we receive post with new character to be created, need this
    def __init__(self, name,email,password,is_active):
        self.name = name
        self.email = email
        self.password = password
        self.is_active = is_active

    #if we would like to print the character
    def __repr__(self):
        return f'<User {self.name}>'
    
    #to send as response need to serialize to jsonify later on
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "favorites": [favorite.serialize() for favorite in self.favorites] if self.favorites else None
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
        self.name = name
        self.terrain = terrain
        self.description = description
        self.location = location
        self.key_event = key_event

    def __repr__(self):
        return f'<Planet {self.name}>'
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "description":self.description,
            "location": self.location,
            "key_event": self.key_event,
            "residents": [resident.serialize() for resident in self.residents],
            "favorites": [favorite.serialize() for favorite in self.favorites] if self.favorites else None
        }

class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True,nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    faction = db.Column(db.String(120), nullable=False)
    race = db.Column(db.String(120), nullable=False)

    homeworld_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    homeworld = db.relationship(Planet, backref="residents") #helps with a bi directional relationship in which we don't have to specify another and can access the residents of each planet, on the planet object.

    def __init__(self,name,gender,faction,race):
        self.name = name
        self.gender = gender
        self.faction = faction
        self.race = race

    def __repr__(self):
        return f'<Character {self.name}>'
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faction": self.faction,
            "gender": self.gender,
            "race":self.race,
            "homeland": self.homeworld.name,
            "favorites": [favorite.serialize() for favorite in self.favorites] if self.favorites else None
        }

class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    user = db.relationship(User, backref="favorites") #helps with a bi directional relationship in which we don't have to specify another and can access the residents of each planet, on the planet object.


    planet_id = db.Column(db.Integer,db.ForeignKey('planet.id'),nullable=True)
    planet = db.relationship(Planet, backref="favorites") #helps with a bi directional relationship in which we don't have to specify another and can access the residents of each planet, on the planet object.


    character_id = db.Column(db.Integer,db.ForeignKey('character.id'),nullable=True)
    character = db.relationship(Character, backref="favorites") #helps with a bi directional relationship in which we don't have to specify another and can access the residents of each planet, on the planet object.

    def __init__(self, user, planet=None, character=None):
        self.user = user
        self.planet = planet
        self.character = character

        if (self.planet is None and self.character is None) or \
           (self.planet is not None and self.character is not None):
            raise ValueError("Please specify either a planet or a character, but not both.")

    def __repr__(self):
        return f'<Favorite {self.id}>'
    
    def serialize(self):
        return{
            "id": self.id,
            "user": self.user.name,
            "planet":self.planet.name if self.planet else None,
            "character": self.character.name if self.character else None
        }

