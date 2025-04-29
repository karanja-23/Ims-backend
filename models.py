from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy_serializer import SerializerMixin
db = SQLAlchemy()
import datetime
from datetime import date
from datetime import datetime 

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', back_populates='users', lazy=True)
    fixed_assets = db.relationship('FixedAssets', back_populates='assign', lazy=True)
    history= db.relationship('FixedAssetHistory', back_populates='user', lazy=True)
    requests = db.relationship('Request', back_populates='user') 
    assigned_inventory = db.relationship('InventoryItem', back_populates='assigned_user', lazy=True)
    inventory_history = db.relationship('InventoryHistory', back_populates='user', lazy=True)
    orders = db.relationship('Orders', back_populates='user', lazy=True)
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'contact': self.contact,
            'role': self.role.to_dict(),
            'history': [history.to_dict() for history in self.history],
            'fixed_assets': [{'id': asset.id, 'name': asset.name} for asset in self.fixed_assets],
            'requests': [request.to_dict() for request in self.requests],
            'inventory_history': [history.to_dict() for history in self.inventory_history]
        }

    def __repr__(self):
        return '<User %r>' % self.username
    
    
class Role(db.Model, SerializerMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    permissions = db.relationship('Permission', secondary='role_permission', back_populates='roles', lazy=True)
    users = db.relationship('User', back_populates='role', lazy=True)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [permission.to_dict() for permission in self.permissions]
        }
    
class RolePermission(db.Model, SerializerMixin):
    __tablename__ = 'role_permission'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    

    
class Permission(db.Model, SerializerMixin):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)  
    roles = db.relationship('Role', secondary='role_permission', back_populates='permissions', lazy=True)  
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
        
class Space(db.Model, SerializerMixin):
    __tablename__ = 'spaces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255),default='active', nullable=False)
    fixed_assets = db.relationship('FixedAssets', back_populates='space', lazy=True)
    history = db.relationship('FixedAssetHistory', back_populates='space', lazy=True)
    assigned_inventory = db.relationship('InventoryItem', back_populates='space', lazy=True)
    inventory_history = db.relationship('InventoryHistory', back_populates='space', lazy=True)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'status': self.status,
            'fixed_assets': [fixed_asset.to_dict() for fixed_asset in self.fixed_assets],
            'history': [history.to_dict() for history in self.history],
            'inventory_items': [inventory_item.to_dict() for inventory_item in self.assigned_inventory],
            'inventory_history': [history.to_dict() for history in self.inventory_history]  
        }
    
    
class Vendors(db.Model, SerializerMixin):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(120), unique=True, nullable=False)
    kra_pin = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    postal_code = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255), nullable=True)
    bank_name = db.Column(db.String(255), nullable=True)
    account_name = db.Column(db.String(255), nullable=True)
    account_number = db.Column(db.String(255), nullable=True)
    paybill_number = db.Column(db.String(255), nullable=True)
    till_number = db.Column(db.String(255), nullable=True)  
    contact_person_name = db.Column(db.String(255), nullable=True)
    contact_person_email = db.Column(db.String(255), nullable=True)
    contact_person_contact = db.Column(db.String(255), nullable=True)
    fixed_assets = db.relationship('FixedAssets', back_populates='vendor', lazy=True)
    assigned_inventory = db.relationship('InventoryItem', back_populates='vendor', lazy=True)
    orders = db.relationship('Orders', back_populates='vendor', lazy=True)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'contact': self.contact,
            'kra_pin': self.kra_pin,
            'address': self.address,
            'postal_code': self.postal_code,
            'city': self.city,
            'country': self.country,
            'bank_name': self.bank_name,
            'account_name': self.account_name,
            'account_number': self.account_number,
            'paybill_number': self.paybill_number,
            'till_number': self.till_number,
            'contact_person_name': self.contact_person_name,
            'contact_person_email': self.contact_person_email,
            'contact_person_contact': self.contact_person_contact,
            'fixed_assets': [fixed_asset.to_dict() for fixed_asset in self.fixed_assets],
            'orders': [order.to_dict() for order in self.orders],
        }
    
class Category(db.Model, SerializerMixin):    
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    fixed_assets = db.relationship('FixedAssets', back_populates='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            
        }
    
class FixedAssets(db.Model, SerializerMixin):
    __tablename__ = 'fixed_assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    purchase_date = db.Column(db.Date(), unique=False, nullable=False)
    purchase_cost = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    serial_number = db.Column(db.String(255), nullable=False)    
    assign_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assign = db.relationship('User', back_populates='fixed_assets', lazy=True)
    status = db.Column(db.String(255),default='unassigned', nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=True)
    space = db.relationship('Space', back_populates='fixed_assets', lazy=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)
    vendor = db.relationship('Vendors', back_populates='fixed_assets', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', back_populates='fixed_assets', lazy=True)
    history = db.relationship('FixedAssetHistory', back_populates='asset', lazy=True)
    requests = db.relationship('Request', back_populates='asset') 
    condition = db.Column(db.String(255), nullable=True)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'purchase_date': self.purchase_date,
            'purchase_cost': self.purchase_cost,
            'description': self.description,
            'serial_number': self.serial_number,
            'assign': self.assign.to_dict() if self.assign else None,
            'status': self.status,
            'space': {'id': self.space.id, 'name': self.space.name} if self.space else None,
            'vendor': {'id': self.vendor.id, 'name': self.vendor.name} if self.vendor else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'history': [history.to_dict() for history in self.history],
            'condition': self.condition
        }
        
    def update_status(self, new_status, user_id=None):
        """Update asset status and create a history log."""
        history_entry = FixedAssetHistory(
            fixed_asset_id=self.id,
            status=new_status,
            assigned_to=user_id,
            date=datetime.date.today()
        )
        db.session.add(history_entry)
        self.status = new_status  
        db.session.commit()    
    
class FixedAssetHistory(db.Model, SerializerMixin):
    __tablename__ = 'fixed_asset_history'
    id = db.Column(db.Integer, primary_key=True)
    fixed_asset_id = db.Column(db.Integer, db.ForeignKey('fixed_assets.id'), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)    
    date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    asset= db.relationship('FixedAssets', back_populates='history', lazy=True)
    user= db.relationship('User', back_populates='history', lazy=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=True)
    space = db.relationship('Space', back_populates='history', lazy=True)
    type= db.Column(db.String(255), default='fixed asset', nullable=True)
    def to_dict(self):
        return {
            'id': self.id,
            'fixed_asset_id': self.fixed_asset_id,
            'status': self.status,
             'asset': {'id': self.asset.id, 'name': self.asset.name, 'serial_number': self.asset.serial_number} if self.asset else None,
            'assigned_to': {'username': self.user.username} if self.user else None,
            'date': self.date.isoformat(),   
            'type': self.type        
            
        }
        
class InventoryHistory(db.Model, SerializerMixin):  
    __tablename__ = 'inventory_history'
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    inventory_item= db.relationship('InventoryItem', back_populates='history', lazy=True)
    user= db.relationship('User', back_populates='inventory_history', lazy=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=True)
    space = db.relationship('Space', back_populates='inventory_history', lazy=True)
    type = db.Column(db.String(255), default='inventory', nullable=True)
    def to_dict(self):
        return {
            'id': self.id,
            'inventory_item': {'id': self.inventory_item.id, 'serial_number': self.inventory_item.serial_number} if self.inventory_item else None,
            'status': self.status,
            'assigned_to': {'username': self.user.username} if self.user else None,
            'date': self.date.isoformat(),
            'space': {'id': self.space.id, 'name': self.space.name} if self.space else None,
            'name': self.inventory_item.inventory.name,
            'type': self.type
        }
    
class Request(db.Model, SerializerMixin):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='requests', lazy=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('fixed_assets.id'), nullable=False)
    status = db.Column(db.String(255),default='pending', nullable=False)
    asset = db.relationship('FixedAssets', back_populates='requests', lazy=True)
    date = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return{
            'id':self.id,
            'user': {'username': self.user.username, 'id': self.user.id} if self.user else None,
            'asset': {'id': self.asset.id, 'name': self.asset.name, 'serial_number': self.asset.serial_number} if self.asset else None,
            'date': self.date.isoformat(), 
            'status': self.status           
        }

class InventoryCategory(db.Model, SerializerMixin):
    __tablename__ = 'inventory_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    inventories = db.relationship('Inventory', back_populates='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
            
class Inventory(db.Model, SerializerMixin):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'), nullable=False)
    category = db.relationship('InventoryCategory', back_populates='inventories', lazy=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    inventory_items = db.relationship('InventoryItem', back_populates='inventory', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'inventory_items': [item.to_dict() for item in self.inventory_items]
        }
class InventoryItem(db.Model, SerializerMixin):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'), nullable=False)
    inventory = db.relationship('Inventory', back_populates='inventory_items', lazy=True)
    serial_number = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date_acquired = db.Column(db.Date, nullable=False)
    condition = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), default='unassigned', nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_user = db.relationship('User', back_populates='assigned_inventory', lazy=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)
    vendor = db.relationship('Vendors', back_populates='assigned_inventory', lazy=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=True)
    space = db.relationship('Space', back_populates='assigned_inventory', lazy=True)
    history = db.relationship('InventoryHistory', back_populates='inventory_item', lazy=True)
    def to_dict(self):
        return {
            'id': self.id,
            'inventory': {'id': self.inventory.id, 'name': self.inventory.name} if self.inventory else None,
            'serial_number': self.serial_number,
            'description': self.description,
            'date_acquired': self.date_acquired.isoformat(),
            'condition': self.condition,
            'status': self.status,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'assign': {'username': self.assigned_user.username, 'id': self.assigned_user.id} if self.assigned_user else None,
            'vendor': {'name': self.vendor.name} if self.vendor else None,
            'space': {'name': self.space.name, 'id': self.space.id} if self.space else None,
            'history': [history.to_dict() for history in self.history]
        }
        
class Orders(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id= db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    vendor = db.relationship('Vendors', back_populates='orders', lazy=True)
    date=db.Column(db.Date, nullable=False, default=datetime.utcnow)
    quantity=db.Column(db.Integer, nullable=False)
    status=db.Column(db.String(255), default='pending', nullable=False)
    order_items = db.relationship('OrderItem', back_populates='order', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='orders', lazy=True)
    
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'vendor': {'name': self.vendor.name, 'id': self.vendor.id} if self.vendor else None,
            'date': self.date.isoformat(),
            'status': self.status,
            'placed_by': {'username': self.user.username, 'id': self.user.id} if self.user else None
        }
def generate_next_order_id():
    last_order = Orders.query.order_by(Orders.id.desc()).first()
    if last_order and last_order.order_id.startswith("ORD"):
        last_number = int(last_order.order_id.replace("ORD", ""))
        next_number = last_number + 1
    else:
        next_number = 1
    return f"ORD{next_number:04d}"        
        
@event.listens_for(Orders, 'before_insert')
def set_order_id(mapper, connect, target):
    target.order_id = generate_next_order_id()    
class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Orders', back_populates='order_items', lazy=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'name': self.name,
            'quantity': self.quantity,
            'type': self.type,
            'unit_cost': self.unit_cost
        }
            
            
class Documents(db.Model, SerializerMixin):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    document = db.Column(db.LargeBinary, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'date_created': self.date_created.isoformat(),
            'description': self.description
        }