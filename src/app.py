import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configure database URI
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Error handler for API exceptions
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Route for sitemap generation
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Route for retrieving all users
@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

# Route for creating a new user
@app.route('/user', methods=['POST'])
def create_user():
    request_body_user = request.get_json()
    
    if not request_body_user:
        return jsonify({"error": "No data provided"}), 400

    if 'first_name' not in request_body_user or 'email' not in request_body_user or 'password' not in request_body_user:
        return jsonify({"error": "Missing required fields"}), 400

    user = User(
        first_name=request_body_user['first_name'],
        email=request_body_user['email'],
        password=generate_password_hash(request_body_user['password'])  # Hash password for security
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 201

# Route for updating an existing user
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    request_body_user = request.get_json()
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if 'first_name' in request_body_user:
        user.first_name = request_body_user['first_name']
    if 'email' in request_body_user:
        user.email = request_body_user['email']
    if 'password' in request_body_user:
        user.password = generate_password_hash(request_body_user['password'])

    db.session.commit()

    return jsonify(user.serialize()), 200

# Route for deleting an existing user
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User removed"}), 200

# Run the app
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
