from flask import Flask, request
from flask_cors import CORS
from vars import walkable_blocks
from werkzeug.routing import IntegerConverter
import json
import sys

app = Flask(__name__)
CORS(app)
app.app_context().push()

from lib.block_walkable import set_block_walkable, get_block_walkable
from lib.db import db, Block, Inventory, Item, Enchantment
from lib.pathfind import pathfind

class SignedIntConverter(IntegerConverter):
    regex = r'-?\d+'

app.url_map.converters['sint'] = SignedIntConverter

@app.route("/")
def hello_world():
    return "<p>Hello, Future Amazon Worker!</p>"

@app.get("/item")
def get_item():
    item_name = request.args.get('name')
    results = Item.query.filter(Item.name.ilike(f'%{item_name}%') | Item.display_name.ilike(f'%{item_name}%')).all()
    for result in results:
        print(result.inventory)
    return json.dumps([result.to_dict(rules=('-enchantments.item', '-inventory.items', '-inventory.block.inventory')) for result in results])

@app.get("/block")
def get_all_blocks():
    return json.dumps([result.to_dict(rules=('-inventory.block', '-inventory.items.inventory', '-inventory.items.enchantments.item')) for result in Block.query.filter(Block.name != 'minecraft:air').all()])

@app.get("/block/<sint:x>/<sint:y>/<sint:z>")
def get_block(x, y, z):
    block = db.session.query(Block).filter_by(x=x, y=y, z=z).first()
    if block is None:
        return "No block found", 404
    return block.to_dict(rules=('-inventory.block', '-inventory.items.inventory', '-inventory.items.enchantments.item'))

@app.get("/path/<sint:cx>/<sint:cy>/<sint:cz>/<sint:tx>/<sint:ty>/<sint:tz>")
def path(cx, cy, cz, tx, ty, tz):
    path = pathfind(cx, cy, cz, tx, ty, tz)
    return { "path": path} if path else { "error": "No path found" }

class block_dto():
    def __init__(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.name = data["name"]
        self.inventory = data["inventory"] if "inventory" in data else None
    x: int
    y: int
    z: int
    name: str
    inventory: dict or None

@app.post("/block/<sint:x>/<sint:y>/<sint:z>")
def set_block(x, y, z):
    block = block_dto(request.json)
    sys.stdout.write(f"Settings block {x} {y} {z} to be {'walkable' if block.name in walkable_blocks else 'not walkable'}\n")
    set_block_walkable(x, y, z, block.name in walkable_blocks)

    block_db: Block = db.session.query(Block).where(Block.x == x, Block.y == y, Block.z == z).first()
    if block_db is None:
        block_db = Block(x=x, y=y, z=z, name=block.name)

    if block.inventory is not None:
        # Overwrite inventory
        if block_db.inventory is not None:
            db.session.delete(block_db.inventory)
        inventory_db = Inventory(max_count=block.inventory["maxCount"], block=block_db)
        db.session.add(inventory_db)

        for item in block.inventory["items"]:
            if type(item) is not dict:
                continue
            item_db = Item(
                count=item.get("count"),
                max_count=item.get("maxCount"),
                name=item.get("name"),
                display_name=item.get("displayName"),
                slot=item.get("slot"),
                damage=item.get("damage", None),
                max_damage=item.get("maxDamage", None),
                inventory=inventory_db
            )
            db.session.add(item_db)
            for enchantment in item.get("enchantments", []):
                enchantment_db = Enchantment(
                    name=enchantment.get("name"),
                    level=enchantment.get("level"),
                    item=item_db
                )
                db.session.add(enchantment_db)
        pass
    elif block_db.inventory is not None:
        # Remove block_db.inventory
        db.session.delete(block_db.inventory)
        pass
    
    block_db.name = block.name
    db.session.add(block_db)
    db.session.commit()
    return block_db.to_dict(rules=('-inventory.block', '-inventory.items.inventory', '-inventory.items.enchantments.item'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)