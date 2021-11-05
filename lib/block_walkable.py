import redis

from lib.db import db, Block
from vars import walkable_blocks

r = redis.Redis(host='localhost', port=6379, db=0)

def set_block_walkable(x, y, z, walkable=True):
    """
    Set a block to be walkable or not.
    """
    return r.setbit(f"{x}:{z}", y, 1 if walkable else 0)

def get_block_walkable(x, y, z):
    """
    Return whether a block is walkable or not.
    """
    return r.getbit(f"{x}:{z}", y)

loaded = r.get('loaded')
if loaded is None:
    print("Setting up redis...")
    r.set('loaded', 'true')
    blocks = db.session.query(Block).all()
    for block in blocks:
        set_block_walkable(block.x, block.y, block.z, block.name in walkable_blocks)
