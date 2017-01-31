
# New quick and dirty DB interface

# TODO make use of the orm

from sqlalchemy import *

#engine = create_engine('sqlite:///door.db', echo=True)
engine = create_engine('postgresql://brus:brus@localhost/brus', echo=True)

meta = MetaData()
users = Table("users", meta, autoload=True, autoload_with=engine)
transactions = Table("transactions", meta, autoload=True, autoload_with=engine)
machine = Table("machine", meta, autoload=True, autoload_with=engine)
slot_product = Table("slot_product", meta, autoload=True, autoload_with=engine)
product = Table("product", meta, autoload=True, autoload_with=engine)

def add_funds(user,value,descr=""):
  engine.execute(transactions.insert().values(value=value, descr="", username=user))

def subtract_funds(user, value, descr="", overdraft=False):
    if value < 0:
        return False
    if not overdraft:
      # FIXME session
      if balance(user) < value:
        return False
    r = engine.execute(transactions.insert().values(value=-value, descr=descr, username=user))
    return r.rowcount > 0

def balance(user):
    r = engine.execute(text("SELECT SUM(transactions.value) FROM transactions WHERE transactions.username=:user"), user=user)
    return r.fetchone()[0]

def transaction_history(user):
    q = select([transactions.c.tid, transactions.c.timestamp, transactions.c.descr,
                transactions.c.value]).where(transactions.c.username==user).order_by(transactions.c.tid.desc())
    return engine.execute(q).fetchall()

def get_outgoing_transactions():
    q = select([transactions.c.tid, transactions.c.timestamp, transactions.c.descr,
                transactions.c.value]).where(transactions.c.value>0).order_by(transactions.c.tid.desc())
    return engine.execute(q).fetchall()

def set_stripe_id(user,id):
  # merge() / insert or update
    q = users.update().where(users.c.username == user).values(stripe_id=id)
    engine.execute(q)

def get_stripe_id(user):
    q=select([users.c.stripe_id]).where(users.c.username == user)
    r=engine.execute(q).fetchone()
    if r:
        return r[0]
    return r

def getproduct(machine, slot):
  q = select([slot_product.c.product]).where(slot_product.c.machine==machine).where(slot_product.c.slot==slot)
  r=engine.execute(q).fetchone()
  if r:
    return r[0]
  return None

def get_product_price_descr(pid):
  q = select([product.c.price, product.c.product]).where(product.c.pid==pid)
  return engine.execute(q).fetchone()

