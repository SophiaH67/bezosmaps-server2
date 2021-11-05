from db import db, Block, Inventory, Item, Enchantment

chest = Block(x=1, y=1, z=1, name="chest")
db.session.add(chest)
db.session.commit()

chest_inventory = Inventory()

chest_inventory.block = chest

db.session.add(chest_inventory)
db.session.commit()

steak = Item(
  name="steak",
  count=3,
  max_count=64,
  display_name="Steak",
  slot=2,
  inventory=chest_inventory)

db.session.add(steak)
db.session.commit()

bow = Item(
  name="bow",
  count=1,
  max_count=1,
  display_name="Bow",
  slot=1,
  inventory=chest_inventory
)

power_v = Enchantment(
  name="power",
  display_name="Power",
  level=5,
  item=bow
)

db.session.add(power_v)
db.session.commit()

chest = Block.query.filter_by(x=1, y=1, z=1).first()
print(chest.inventory)
db.session.delete(chest)
print(chest.inventory)
chest_inventory = Inventory.query.filter_by(block_id=chest.id).first()
print(chest_inventory)
