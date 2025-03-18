from flask import Flask, jsonify, request
from models import db,User,Role,Permission,RolePermission,Space,Vendors
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config ['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route('/', methods=['GET'])
def index():
    return (jsonify({'message': 'Welcome to Moringa IMS API'}), 200)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify({"error": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user.email))
    return jsonify({"access_token": access_token}),200
 
@app.route("/protected/user", methods=["GET"])
@jwt_required()
def protected_user():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    else:
        return jsonify(user.to_dict()), 200    
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
    
@app.route('/role_permission', methods=['POST','PATCH'])
def create_role_permissions():
    if request.method == 'POST':
        data = request.get_json()
        role_id = data.get('role_id')
        permission_ids = data.get('permission_ids', [])  # Expecting a list of permission IDs

        if not role_id or not isinstance(permission_ids, list) or not permission_ids:
            return jsonify({"error": "Invalid input"}), 400

        role_permissions = [
            RolePermission(role_id=role_id, permission_id=perm_id)
            for perm_id in permission_ids
        ]

        db.session.bulk_save_objects(role_permissions)
        db.session.commit()

        return jsonify([rp.to_dict() for rp in role_permissions]), 201
    if request.method == 'PATCH':
        data = request.get_json()
        role_id = data.get('role_id')
        permission_ids = data.get('permission_ids', [])  

        if not role_id or not isinstance(permission_ids, list) or not permission_ids:
            return jsonify({"error": "Invalid input"}), 400

        role = Role.query.get(role_id)
        if not role:
            return jsonify({"error": "Role not found"}), 404

        role.permissions = [Permission.query.get(perm_id) for perm_id in permission_ids]
        db.session.commit()

        return jsonify({"message": "Role permissions updated successfully"}), 200  
    
@app.route('/spaces',methods=['POST'])
def create_space():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    location = data.get('location')
    space = Space(name=name,description=description,location=location)
    db.session.add(space)
    db.session.commit()
    return jsonify({"message": "Space created successfully"}), 201
@app.route('/spaces/<int:space_id>', methods=['GET', 'PUT', 'DELETE'])
def get_space(space_id):
    space = Space.query.get(space_id)
    if space is None:
        return jsonify({'message': 'Space not found'}), 404
    if request.method == 'GET':
        return jsonify(space.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        space.name = data.get('name', space.name)
        space.description = data.get('description', space.description)
        space.location = data.get('location', space.location)
        space.status = data.get('status', space.status)
        db.session.commit()
        return jsonify({'message': 'Space updated'}), 200
    if request.method == 'DELETE':
        db.session.delete(space)
        db.session.commit()
        return jsonify({'message': 'Space deleted'}), 200
@app.route('/spaces/all', methods=['GET'])
def get_spaces():
    spaces = Space.query.all()
    return jsonify([space.to_dict() for space in spaces]), 200

@app.route('/vendors',methods=['POST','GET'])
def create_vendor():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        contact = data.get('contact')
        kra_pin = data.get('kra_pin')
        address = data.get('address')
        postal_code = data.get('postal_code')
        city = data.get('city')
        bank_name = data.get('bank_name')
        account_name = data.get('account_name')
        account_number = data.get('account_number')
        country = data.get('country')
        paybill_number = data.get('paybill_number')
        till_number = data.get('till_number')
        contact_person_name = data.get('contact_person_name')
        contact_person_email = data.get('contact_person_email')
        contact_person_contact = data.get('contact_person_contact')
    
        vendor = Vendors(
            name=name,
            email=email,
            contact=contact,
            kra_pin=kra_pin,
            address=address,
            postal_code=postal_code,
            city=city,
            country=country,
            bank_name=bank_name,
            account_name= account_name,
            account_number=account_number,
            paybill_number=paybill_number,
            till_number=till_number,
            contact_person_name=contact_person_name,
            contact_person_email=contact_person_email,
            contact_person_contact=contact_person_contact
        )        
           
        db.session.add(vendor)
        db.session.commit()
        return jsonify({"message": "Vendor created successfully"}), 201
    if request.method == 'GET':
        vendors = Vendors.query.all()
        return jsonify([vendor.to_dict() for vendor in vendors]), 200

@app.route('/vendors/<int:vendor_id>', methods=['GET', 'PUT', 'DELETE'])
def get_vendor(vendor_id):
    vendor = Vendors.query.get(vendor_id)
    if vendor is None:
        return jsonify({'message': 'Vendor not found'}), 404
    if request.method == 'GET':
        return jsonify(vendor.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        vendor.name = data.get('name', vendor.name)
        vendor.email = data.get('email', vendor.email)
        vendor.contact = data.get('contact', vendor.contact)
        vendor.kra_pin = data.get('kra_pin', vendor.kra_pin)
        vendor.address = data.get('address', vendor.address)
        vendor.postal_code = data.get('postal_code', vendor.postal_code)
        vendor.city = data.get('city', vendor.city)
        vendor.country = data.get('country', vendor.country)
        vendor.bank_name = data.get('bank_name', vendor.bank_name)
        vendor.account_name = data.get('account_name', vendor.account_name)
        vendor.account_number = data.get('account_number', vendor.account_number)
        vendor.paybill_number = data.get('paybill_number', vendor.paybill_number)
        vendor.till_number = data.get('till_number', vendor.till_number)
        vendor.contact_person_name = data.get('contact_person_name', vendor.contact_person_name)
        vendor.contact_person_email = data.get('contact_person_email', vendor.contact_person_email)
        vendor.contact_person_contact = data.get('contact_person_contact', vendor.contact_person_contact)
        db.session.commit()
        return jsonify({'message': 'Vendor updated'}), 200
    if request.method == 'DELETE':
        db.session.delete(vendor)
        db.session.commit()
        return jsonify({'message': 'Vendor deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True) 