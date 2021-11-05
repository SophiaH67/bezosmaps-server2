from flask import Flask, request
from vars import walkable_blocks
from werkzeug.routing import IntegerConverter

app = Flask(__name__)
app.app_context().push()

from lib.block_walkable import set_block_walkable, get_block_walkable
from lib.db import db, Block, Inventory, Item, Enchantment
from lib.pathfind import pathfind

class SignedIntConverter(IntegerConverter):
    regex = r'-?\d+'

app.url_map.converters['sint'] = SignedIntConverter

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/block/<sint:x>/<sint:y>/<sint:z>")
def walkable(x, y, z):
    block = db.session.query(Block).filter_by(x=x, y=y, z=z).first()
    if block is None:
        return "No block found", 404
    return block.as_dict()

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
    inventory: bool or None

@app.post("/block/<sint:x>/<sint:y>/<sint:z>")
def set_block(x, y, z):
    block = block_dto(request.json)
    block_db: Block = db.session.query(Block).where(Block.x == x, Block.y == y, Block.z == z).first()
    if block_db is None:
        block_db = Block(x=x, y=y, z=z, name=block.name)

    if block.inventory is not None:
        # Overwrite inventory
        if block_db.inventory is not None:
            block_db.inventory.delete()
        inventory_db = Inventory()
        db.session.add(inventory_db)

        for item in block.inventory:
            item_db = Item(
                count=item.count,
                max_count=item.max_count,
                name=item.name,
                display_name=item.display_name,
                slot=item.slot,
                damage=item.damage,
                max_damage=item.max_damage,
                inventory=inventory_db
            )
            db.session.add(item_db)
            for enchantment in item.enchantments:
                enchantment_db = Enchantment(
                    name=enchantment.name,
                    level=enchantment.level,
                    item=item_db
                )
                db.session.add(enchantment_db)
            block_db.inventory.append(item_db)
        pass
    elif block_db.inventory is not None and block.inventory is None:
        # Remove block_db.inventory
        block_db.inventory.delete()
        pass
    
    block_db.name = block.name
    set_block_walkable(x, y, z, block.name in walkable_blocks)
    db.session.add(block_db)
    db.session.commit()
    return block_db.as_dict()