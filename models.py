from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
db = SQLAlchemy()


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', back_populates='users', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'contact': self.contact,
            'role': self.role.to_dict()
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
    account_number = db.Column(db.String(255), nullable=True)
    paybill_number = db.Column(db.String(255), nullable=True)
    till_number = db.Column(db.String(255), nullable=True)  
    contact_person_name = db.Column(db.String(255), nullable=True)
    contact_person_email = db.Column(db.String(255), nullable=True)
    contact_person_contact = db.Column(db.String(255), nullable=True)
    
class FixedAssets(db.Model, SerializerMixin):
    __tablename__ = 'fixed-assests'
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(255), nullable=False)
    serial_number = db.Column(db.String(255), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    vendor = db.Column(db.String(255), nullable=False)
    purchase_price = db.Column(db.Numeric(8, 2), nullable=False)
    date_of_purchase = db.Column(db.Date, nullable=False)
    physical_location = db.Column(db.String(255), nullable=False)
    department_owner = db.Column(db.String(255), nullable=False)
    depreciation_rate = db.Column(db.Numeric(8, 2), nullable=False)
    depreciation_start_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'asset_name': self.asset_name,
            'serial_number': self.serial_number,
            'quantity': self.quantity,
            'vendor': self.vendor,
            'purchase_price': float(self.purchase_price),
            'date_of_purchase': self.date_of_purchase.isoformat(),
            'physical_location': self.physical_location,
            'department_owner': self.department_owner,
            'depreciation_rate': float(self.depreciation_rate),
            'depreciation_start_date': self.depreciation_start_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Orders(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    total = db.Column(db.Numeric(8, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    receiving_date = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, nullable=False, default=False)
    sent = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status,
            'total': float(self.total),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'receiving_date': self.receiving_date.isoformat(),
            'is_paid': self.is_paid,
            'sent': self.sent
        } 