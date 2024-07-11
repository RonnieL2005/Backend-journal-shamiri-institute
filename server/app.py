from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a random secret key

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# User model (assumed to be needed for authentication)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # other fields as necessary

# JournalEntry model
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Authentication endpoint for user login (for simplicity)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401


# Decorator to verify the user from JWT token
def token_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify(message="User not found"), 404
        return f(current_user, *args, **kwargs)
    return decorated_function

# Create journal entry endpoint
@app.route('/journal', methods=['POST'])
@token_required
def create_journal_entry(current_user):
    data = request.get_json()
    new_entry = JournalEntry(
        title=data['title'], 
        content=data['content'], 
        category=data.get('category'), 
        user_id=current_user.id
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'message': 'Journal entry created successfully!'})

# Update journal entry endpoint
@app.route('/journal/<int:entry_id>', methods=['PUT'])
@token_required
def update_journal_entry(current_user, entry_id):
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        return jsonify({'message': 'Journal entry not found!'}), 404

    data = request.get_json()
    entry.title = data['title']
    entry.content = data['content']
    entry.category = data.get('category')
    db.session.commit()
    return jsonify({'message': 'Journal entry updated successfully!'})

# Delete journal entry endpoint
@app.route('/journal/<int:entry_id>', methods=['DELETE'])
@token_required
def delete_journal_entry(current_user, entry_id):
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        return jsonify({'message': 'Journal entry not found!'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Journal entry deleted successfully!'})

# Get all journal entries for a user endpoint
@app.route('/journal', methods=['GET'])
@token_required
def get_all_journal_entries(current_user):
    entries = JournalEntry.query.filter_by(user_id=current_user.id).all()
    journal_entries = [
        {
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'category': entry.category,
            'date_created': entry.date_created
        }
        for entry in entries
    ]
    return jsonify({'journal_entries': journal_entries})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  

    app.run(debug=True)
