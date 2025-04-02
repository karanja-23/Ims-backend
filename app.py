from flask import Flask, jsonify, request
from models import db,User,Role,Permission,RolePermission,Space,Vendors,FixedAssets, Category, FixedAssetHistory,Request, Inventory, InventoryCategory, InventoryItem
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
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.contact = data.get('contact', user.contact)
        user.password = data.get('password', user.password)
        user.role_id = data.get('role_id', user.role_id)

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
    
@app.route('/assets',methods=['POST','GET'])
def create_asset():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        purchase_date = data.get('purchase_date')
        purchase_cost = data.get('purchase_cost')
        description = data.get('description')
        serial_number = data.get('serial_number')
        assign_id = data.get('assign_id')
        status = data.get('status')
        space_id = data.get('space_id')
        vendor_id = data.get('vendor_id')
        category_id = data.get('category_id')
        
        asset = FixedAssets(
            name=name,
            purchase_date=purchase_date,
            purchase_cost=purchase_cost,
            description=description,
            serial_number=serial_number,
            assign_id=assign_id,
            status=status,
            space_id=space_id,
            vendor_id=vendor_id,
            category_id=category_id
        )       
                
        db.session.add(asset)
        db.session.commit()
        return jsonify({"message": "Fixed asset created successfully"}), 201
    if request.method == 'GET':
        assets = FixedAssets.query.all()
        return jsonify([asset.to_dict() for asset in assets]), 200

@app.route('/assets/<int:asset_id>', methods=['GET', 'PUT', 'DELETE'])
def get_asset(asset_id):
    asset = FixedAssets.query.get(asset_id)
    if asset is None:
        return jsonify({'message': 'Asset not found'}), 404
    if request.method == 'GET':
        return jsonify(asset.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        asset.name = data.get('name', asset.name)
        asset.purchase_date = data.get('purchase_date', asset.purchase_date)
        asset.purchase_cost = data.get('purchase_cost', asset.purchase_cost)
        asset.description = data.get('description', asset.description)
        asset.serial_number = data.get('serial_number', asset.serial_number)
        asset.assign_id = data.get('assign_id', asset.assign_id)
        asset.status = data.get('status', asset.status)
        asset.space_id = data.get('space_id', asset.space_id)
        asset.vendor_id = data.get('vendor_id', asset.vendor_id)
        asset.category_id = data.get('category_id', asset.category_id)
        asset.condition = data.get('condition', asset.condition)
        db.session.commit()
        return jsonify({'message': 'Asset updated'}), 200
    if request.method == 'DELETE':
        db.session.delete(asset)
        db.session.commit()
        return jsonify({'message': 'Asset deleted'}), 200

@app.route('/assets/filter/<serial_number>', methods=['GET'])
def get_asset_by_serial_number(serial_number):
    asset = FixedAssets.query.filter_by(serial_number=serial_number).first()
    if asset is None:
        return jsonify({'message': 'Asset not found'}), 404
    return jsonify(asset.to_dict()), 200
@app.route('/categories',methods=['POST','GET'])
def create_category():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return jsonify({"message": "Category created successfully"}), 201
    if request.method == 'GET':
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200

@app.route('/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'message': 'Category not found'}), 404
    if request.method == 'GET':
        return jsonify(category.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        category.name = data.get('name', category.name)
        db.session.commit()
        return jsonify(category.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted'}), 200

@app.route('/assets/<int:asset_id>/history', methods=['POST'])
def add_asset_history(asset_id):
    asset = FixedAssets.query.get(asset_id)
    if asset is None:
        return jsonify({'message': 'Asset not found'}), 404
    data = request.get_json()
    status = data.get('status')
    assigned_to = data.get('assigned_to')
    space_id = data.get('space_id')
    history = FixedAssetHistory(fixed_asset_id=asset_id, status=status,assigned_to=assigned_to, space_id=space_id)
    db.session.add(history)
    db.session.commit()
    return jsonify({'message': 'Asset history added'}), 201

@app.route('/assets/history', methods=['DELETE'])
def delete_asset_history():
    FixedAssetHistory.query.delete()
    db.session.commit()
    return jsonify({'message': 'Asset history deleted'}), 200

@app.route('/requests', methods=['GET','POST'])
def get_categories():
    if request.method == 'POST':
        data = request.get_json()
        asset_id = data.get('asset_id')
        user_id=data.get('user_id')
        new_request = Request(asset_id=asset_id, user_id=user_id)
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"message": "Request created successfully"}), 201
    if request.method == 'GET':
        requests = Request.query.all()
        return jsonify([request.to_dict() for request in requests]), 200
        

@app.route('/requests/<int:request_id>', methods=['GET', 'PUT', 'DELETE'])
def get_request(request_id):
    my_request = Request.query.get(request_id)
    if my_request is None:
        return jsonify({'message': 'Request not found'}), 404
    if request.method == 'GET':
        return jsonify(my_request.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        my_request.asset_id = data.get('asset_id', my_request.asset_id)
        my_request.user_id = data.get('user_id', my_request.user_id)
        my_request.status = data.get('status', my_request.status)
        db.session.commit()
        return jsonify(my_request.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(my_request)
        db.session.commit()
        return jsonify({'message': 'Request deleted'}), 200

@app.route('/inventory/categories', methods=['GET', 'POST'])
def get_inventory_categories():
    if request.method == 'GET':
        categories = InventoryCategory.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        category = InventoryCategory(name=name)
        db.session.add(category)
        db.session.commit()
        return jsonify({"message": "Category created successfully"}), 201

@app.route('/inventory/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
def get_inventory_category(category_id):
    category = InventoryCategory.query.get(category_id)
    if category is None:
        return jsonify({'message': 'Category not found'}), 404
    if request.method == 'GET':
        return jsonify(category.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        category.name = data.get('name', category.name)
        db.session.commit()
        return jsonify(category.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted'}), 200
    
@app.route('/inventory', methods=['GET', 'POST'])
def get_inventories():
    if request.method == 'GET':
        inventories = Inventory.query.all()
        return jsonify([inventory.to_dict() for inventory in inventories]), 200
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        category_id = data.get('category_id')
        unit_cost = data.get('unit_cost')
        inventory = Inventory(name=name, category_id=category_id,unit_cost=unit_cost)
        db.session.add(inventory)
        db.session.commit()
        return jsonify({"message": "Inventory created successfully"}), 201
    
@app.route('/inventory/<int:inventory_id>', methods=['GET', 'PUT', 'DELETE'])
def get_inventory(inventory_id):
    inventory = Inventory.query.get(inventory_id)
    if inventory is None:
        return jsonify({'message': 'Inventory item not found'}), 404
    if request.method == 'GET':
        return jsonify(inventory.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        inventory.name = data.get('name', inventory.name)
        inventory.category_id = data.get('category_id', inventory.category_id)
        inventory.quantity = data.get('quantity', inventory.quantity)
        inventory.unit_cost = data.get('unit_cost', inventory.unit_cost)
        db.session.commit()
        return jsonify(inventory.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(inventory)
        db.session.commit()
        return jsonify({'message': 'Inventory item deleted'}), 200

@app.route('/update/quantity/<int:inventory_id>', methods=['PUT'])
def update_inventory_quantity(inventory_id):
    inventory = Inventory.query.get(inventory_id)
    if inventory is None:
        return jsonify({'message': 'Inventory item not found'}), 404

    
    inventory.quantity = inventory.quantity + 1
    db.session.commit()

    return jsonify(inventory.to_dict()), 200
@app.route('/inventory/items', methods=['GET', 'POST'])
def get_inventory_items():
    if request.method == 'GET':
        inventory_items = InventoryItem.query.all()
        return jsonify([item.to_dict() for item in inventory_items]), 200
    if request.method == 'POST':
        data = request.get_json()
        inventory_id = data.get('inventory_id')
        serial_number= data.get('serial_number')
        description = data.get('description')
        date_acquired = data.get('date_acquired')
        condition = data.get('condition')      
        quantity = data.get('quantity')
        vendor_id = data.get('vendor_id')
        unit_cost = data.get('unit_cost')
        space_id = data.get('space_id')
        inventory_item = InventoryItem(
            inventory_id=inventory_id,
            serial_number=serial_number,
            description=description,
            date_acquired=date_acquired,
            condition=condition,
            quantity=quantity,
            vendor_id=vendor_id,
            unit_cost=unit_cost,
            space_id=space_id
        )
        db.session.add(inventory_item)
        db.session.commit()
        return jsonify({"message": "Inventory item created successfully"}), 201

@app.route('/inventory/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])  
def get_inventory_item(item_id):
    item = InventoryItem.query.get(item_id)
    if item is None:
        return jsonify({'message': 'Inventory item not found'}), 404
    if request.method == 'GET':
        return jsonify(item.to_dict()), 200
    if request.method == 'PUT':
        data = request.get_json()
        item.inventory_id = data.get('inventory_id', item.inventory_id)
        item.serial_number = data.get('serial_number', item.serial_number)
        item.description = data.get('description', item.description)
        item.date_acquired = data.get('date_acquired', item.date_acquired)
        item.condition = data.get('condition', item.condition)
        item.status = data.get('status', item.status)
        item.quantity = data.get('quantity', item.quantity)
        item.assigned_to = data.get('assigned_to', item.assigned_to)
        item.vendor_id = data.get('vendor_id', item.vendor_id)
        item.unit_cost = data.get('unit_cost', item.unit_cost)
        db.session.commit()
        return jsonify(item.to_dict()), 200
    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Inventory item deleted'}), 200
if __name__ == '__main__':
    app.run(debug=True) 