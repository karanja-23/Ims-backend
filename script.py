from app import app
from models import db

with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(tables)