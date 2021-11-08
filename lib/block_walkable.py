import redis
from os import environ
from lib.db import db, Block
from vars import walkable_blocks

r = redis.Redis(host=environ['REDIS_HOST'], port=environ['REDIS_PORT'], db=0)

def set_block_walkable(x, y, z, walkable=True):
    """
    Set a block to be walkable or not.
    """
    print(f"Setting {x}:{z}:{y} to {1 if walkable else 0}")
    return r.setbit(f"{x}:{z}", y, 1 if walkable else 0)

def get_block_walkable(x, y, z):
    """
    Return whether a block is walkable or not.
    """
    return r.getbit(f"{x}:{z}", y)

print("Setting up redis...")
r.set('loaded', 'true')
blocks = db.session.query(Block).all()
for block in blocks:
    set_block_walkable(block.x, block.y, block.z, block.name in walkable_blocks)
