from flask import Flask, jsonify, request
from models import db,User,Role,Permission
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/', methods=['GET'])
def index():
    return (jsonify({'message': 'Welcome to Moringa IMS API'}), 200)

@app.route('/users',methods=['GET','POST'])
def get_users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        contact = data.get('contact')
        password = data.get('password')
        role_id = data.get('role_id')
        user = User(username=username,email=email,contact=contact,password=password,role_id=role_id)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    
@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    if request.method == 'GET':
        return jsonify(user.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        user.username = data['username']
        user.email = data['email']
        user.contact = data['contact']
        user.password = data['password']
        user.role_id = data['role_id']
        db.session.commit()
        return jsonify(user.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 200

@app.route('/roles',methods=['POST'])
def create_role():        
    data = request.get_json()
    name = data.get('name')
    role = Role(name=name)
    db.session.add(role)
    db.session.commit()
    return jsonify(role.to_dict()), 201

@app.route('/roles/<int:role_id>', methods=['GET', 'PUT', 'DELETE'])
def get_role(role_id):
    role = Role.query.get(role_id)
    if role is None:
        return jsonify({'message': 'Role not found'}), 404
    if request.method == 'GET':
        return jsonify(role.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        role.name = data.get('name', role.name)
        role.description = data.get('description', role.description)
      
        db.session.commit()
        return jsonify(role.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(role)
        db.session.commit()
        return jsonify({'message': 'Role deleted'}), 200

@app.route('/roles/all', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200    
    
@app.route('/permissions',methods=['POST'])
def create_permission():
    data = request.get_json()
    name = data.get('name')
    permission = Permission(name=name)
    db.session.add(permission)
    db.session.commit()
    return jsonify(permission.to_dict()), 201
@app.route('/permissions/all', methods=['GET'])
def get_permissions():
    permissions = Permission.query.all()
    return jsonify([permission.to_dict() for permission in permissions]), 200
@app.route('/permissions/<int:permission_id>', methods=['GET', 'PUT', 'DELETE'])
def get_permission(permission_id):
    permission = Permission.query.get(permission_id)
    if permission is None:
        return jsonify({'message': 'Permission not found'}), 404
    if request.method == 'GET':
        return jsonify(permission.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        permission.name = data.get('name', permission.name)
        db.session.commit()
        return jsonify(permission.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(permission)
        db.session.commit()
        return jsonify({'message': 'Permission deleted'}), 200
if __name__ == '__main__':
    app.run(debug=True) 