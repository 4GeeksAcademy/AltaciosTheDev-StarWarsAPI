"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

#from models import Person

app = Flask(__name__)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#gets all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users],200)

#gets specific user
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):

    user = User.query.get(id)
    
    return jsonify(user.serialize()), 200

#gets favorite of specific user
@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_user_favorites(id):

    user = User.query.get(id)
    favorites = user.favorites

    return jsonify([favorite.serialize() for favorite in favorites]), 200

#gets all characters
@app.route('/people', methods=["GET"])
def get_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

#gets specific character
@app.route('/people/<int:id>', methods=["GET"])
def get_person(id):
    character = Character.query.get(id)
    return jsonify(character.serialize()), 200

#gets all planets
@app.route('/planets', methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

#gets specific planet
@app.route('/planets/<int:id>', methods=["GET"])
def get_planet(id):
    planet = Planet.query.get(id)
    return jsonify(planet.serialize()), 200

#logs a user and returns access token with identity of logged user
@app.route("/login", methods=["POST"])
def login():
    #from request object, store email and password in variables, else None.
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    # Query your database for email and password, else None.
    user = User.query.filter_by(email=email, password=password).first()

    if user is None:
        # The user was not found on the database
        return jsonify({"msg": "Bad email or password"}), 401 
    
    # Create a new token with the user id inside
    access_token = create_access_token(identity=user.email)
    return jsonify({ "token": access_token, "user_id": user.id }) #

#gets specific logged in user's favorites, knows which one by using the get_jwt_identity function.
@app.route("/users/favorites", methods=["GET"])
@jwt_required() #will return "msg": "Missing Authorization Header" if it is not present. 

def get_current_user_favorites():
    # Access the identity of the current user with get_jwt_identity
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).first()
    return jsonify(current_user.serialize()), 200

#creates new favorite instance with the user from the identity and the id of the planet sent as query parameter
@app.route("/favorite/planet/<int:planet_id>", methods=["POST", "DELETE"])
@jwt_required()

def favorite_planet_to_current_user(planet_id):
    current_user_email = get_jwt_identity() #will provide email of currently logged user, accessible through the header's token
    current_user = User.query.filter_by(email=current_user_email).one_or_none()

    if current_user == None:
        return jsonify({"msg": "User not found"}), 404

    planet_to_favorite = Planet.query.filter_by(id=planet_id).one_or_none()

    if planet_to_favorite == None:
        return jsonify({"msg": "Planet not found"}), 404
    
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, planet_id=planet_to_favorite.id).one_or_none()

    if request.method == "POST":
        if existing_favorite:
            return jsonify({"msg": f"CANNOT FAVORITE, Planet {planet_to_favorite.name}is already a favorite for user {current_user.email} "}), 400
    
        #current_user not None, planet_to_favorite not None AND existing_favorite is None, then:
        new_favorite_planet = Favorite(user=current_user, planet=planet_to_favorite)
        db.session.add(new_favorite_planet) # add new favorite object to the Favorite table
        db.session.commit()  # Similar to the Git commit, what this does is save all the changes you have made 
        return jsonify({"msg": f"Planet {planet_to_favorite.name}SUCCESSFULLY made a favorite for user {current_user.email}"}), 200
    
    else: #request.method == "DELETE"
        if existing_favorite == None:
            return jsonify({"msg": f"CANNOT DELETE, Planet {planet_to_favorite.name}is CURRENTLY NOT a favorite for user {current_user.email} "}), 400
    
        #current_user not None, planet_to_favorite not None AND existing_favorite is NOT None, then:
        db.session.delete(existing_favorite) # add new favorite object to the Favorite table
        db.session.commit()  # Similar to the Git commit, what this does is save all the changes you have made 
        return jsonify({"msg": f"Planet {planet_to_favorite.name}SUCCESSFULLY DELETED from favorite for user {current_user.email}"}), 200

    
#creates new favorite instance with the user from the identity and the id of the character sent as query parameter  
@app.route("/favorite/people/<int:people_id>", methods=["POST", "DELETE"])
@jwt_required()

def favorite_character_to_current_user(people_id):
    #identify user
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email=current_user_email).one_or_none()

    if current_user == None:
        return jsonify({"msg": "User not found"}), 404

    #identify character
    character_to_favorite = Character.query.filter_by(id=people_id).one_or_none()

    if character_to_favorite == None:
        return jsonify({"msg": "character not found"}), 404

    #check user already has character as favorite
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, character_id=character_to_favorite.id).one_or_none()

    if request.method == "POST":
        if existing_favorite:
            return jsonify({"msg": f"CANNOT FAVORITE, Character {character_to_favorite.name} is already a favorite for user {current_user.email} "}), 400

        #finally, create new favorite
        new_favorite_character = Favorite(user=current_user, character=character_to_favorite)
        db.session.add(new_favorite_character)
        db.session.commit()
        return jsonify({"msg": f"Character {character_to_favorite.name} SUCCESSFULLY made a favorite for user {current_user.email}"}), 200
    
    else: #request.method == "DELETE"
        if existing_favorite == None:
            return jsonify({"msg": f"CANNOT DELETE, Character {character_to_favorite.name} is CURRENTLY NOT a favorite for user {current_user.email} "}), 400
    
        #current_user not None, planet_to_favorite not None AND existing_favorite is NOT None, then:
        db.session.delete(existing_favorite) # add new favorite object to the Favorite table
        db.session.commit()  # Similar to the Git commit, what this does is save all the changes you have made 
        return jsonify({"msg": f"Character {character_to_favorite.name} SUCCESSFULLY DELETED from favorite for user {current_user.email}"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
