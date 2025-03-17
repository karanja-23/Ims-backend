from flask import Flask, jsonify, request
from models import db,User,Role,Permission,RolePermission,Space,Vendors,FixedAssets,Orders
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

@app.route('/fixed-assets', methods=['POST', 'GET'])
def fixed_assets():
    if request.method == 'POST':
        data = request.get_json()
        asset = FixedAssets(
            asset_name=data.get('asset_name'),
            serial_number=data.get('serial_number'),
            quantity=data.get('quantity', 1),  # Default quantity is 1
            vendor=data.get('vendor'),
            purchase_price=data.get('purchase_price'),
            date_of_purchase=data.get('date_of_purchase'),
            physical_location=data.get('physical_location'),
            department_owner=data.get('department_owner'),
            depreciation_rate=data.get('depreciation_rate'),
            depreciation_start_date=data.get('depreciation_start_date')
        )
        db.session.add(asset)
        db.session.commit()
        return jsonify({"message": "Fixed asset created successfully"}), 201

    if request.method == 'GET':
        assets = FixedAssets.query.all()
        return jsonify([asset.to_dict() for asset in assets]), 200

@app.route('/fixed-assets/<int:asset_id>', methods=['GET', 'PUT', 'DELETE'])
def fixed_asset(asset_id):
    asset = FixedAssets.query.get(asset_id)
    if asset is None:
        return jsonify({'message': 'Fixed asset not found'}), 404

    if request.method == 'GET':
        return jsonify(asset.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json()
        asset.asset_name = data.get('asset_name', asset.asset_name)
        asset.serial_number = data.get('serial_number', asset.serial_number)
        asset.quantity = data.get('quantity', asset.quantity)
        asset.vendor = data.get('vendor', asset.vendor)
        asset.purchase_price = data.get('purchase_price', asset.purchase_price)
        asset.date_of_purchase = data.get('date_of_purchase', asset.date_of_purchase)
        asset.physical_location = data.get('physical_location', asset.physical_location)
        asset.department_owner = data.get('department_owner', asset.department_owner)
        asset.depreciation_rate = data.get('depreciation_rate', asset.depreciation_rate)
        asset.depreciation_start_date = data.get('depreciation_start_date', asset.depreciation_start_date)
        db.session.commit()
        return jsonify({"message": "Fixed asset updated successfully"}), 200

    if request.method == 'DELETE':
        db.session.delete(asset)
        db.session.commit()
        return jsonify({"message": "Fixed asset deleted successfully"}), 200

@app.route('/orders', methods=['POST', 'GET'])
def orders():
    if request.method == 'POST':
        data = request.get_json()
        order = Orders(
            order_number=data.get('order_number'),
            status=data.get('status'),
            total=data.get('total'),
            receiving_date=data.get('receiving_date'),
            is_paid=data.get('is_paid', False),  # Default is_paid is False
            sent=data.get('sent', 0)  # Default sent is 0
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({"message": "Order created successfully"}), 201

    if request.method == 'GET':
        orders = Orders.query.all()
        return jsonify([order.to_dict() for order in orders]), 200

@app.route('/orders/<int:order_id>', methods=['GET', 'PUT', 'DELETE'])
def order(order_id):
    order = Orders.query.get(order_id)
    if order is None:
        return jsonify({'message': 'Order not found'}), 404

    if request.method == 'GET':
        return jsonify(order.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json()
        order.order_number = data.get('order_number', order.order_number)
        order.status = data.get('status', order.status)
        order.total = data.get('total', order.total)
        order.receiving_date = data.get('receiving_date', order.receiving_date)
        order.is_paid = data.get('is_paid', order.is_paid)
        order.sent = data.get('sent', order.sent)
        db.session.commit()
        return jsonify({"message": "Order updated successfully"}), 200

    if request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True) 