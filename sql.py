import os
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "supersecretkey"  # Change this in production!
db = SQLAlchemy(app)

# Serializer for tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    reset_token = db.Column(db.String(128))
    reset_token_expiry = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

@app.route('/request-reset', methods=['POST'])
def request_reset():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404

    token = serializer.dumps(email, salt='password-reset')
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    user.reset_token = token
    user.reset_token_expiry = expiry
    db.session.commit()

    # For demo: show token in response. In production, send by email!
    return jsonify({'message': 'Password reset token generated.', 'reset_token': token})

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'error': 'Token and new password required.'}), 400

    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        return jsonify({'error': 'Token expired.'}), 400
    except BadSignature:
        return jsonify({'error': 'Invalid token.'}), 400

    user = User.query.filter_by(email=email, reset_token=token).first()
    if not user or user.reset_token_expiry < datetime.datetime.utcnow():
        return jsonify({'error': 'Invalid or expired token.'}), 400

    user.password_hash = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    return jsonify({'message': 'Password has been reset.'})

# For demo: user registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409
    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered.'}), 201

if __name__ == '__main__':
    app.run(debug=True)
