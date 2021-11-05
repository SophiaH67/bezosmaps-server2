from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# A sqlalchemy class to represent a block
class Block(db.Model, SerializerMixin):
    __tablename__ = 'blocks'
    __table_args__ = (db.UniqueConstraint('x', 'y', 'z'),)
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    x = db.Column(db.Integer, index=True)
    y = db.Column(db.Integer, index=True)
    z = db.Column(db.Integer, index=True)
    name = db.Column(db.String)
    inventory = db.relationship('Inventory', backref='block', uselist=False, cascade="all, delete-orphan")

class Inventory(db.Model, SerializerMixin):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    max_count = db.Column(db.Integer)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    items = db.relationship('Item', backref='inventory')

class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    count = db.Column(db.Integer)
    max_count = db.Column(db.Integer)
    name = db.Column(db.String)
    display_name = db.Column(db.String)
    slot = db.Column(db.Integer)
    damage = db.Column(db.Integer, nullable=True)
    max_damage = db.Column(db.Integer, nullable=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    enchantments = db.relationship('Enchantment', backref='item')

class Enchantment(db.Model):
    __tablename__ = 'enchantments'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    display_name = db.Column(db.String)
    level = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
db.create_all()

