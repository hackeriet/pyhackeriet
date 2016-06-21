
# New quick and dirty DB interface

# TODO make use of the orm

from sqlalchemy import *
import hashlib

def sha256hash(string):
  if type(string) is str:
    s = string.encode()
  else:
    s = string
  return hashlib.sha256(s).hexdigest()

#engine = create_engine('sqlite:///door.db', echo=True)
engine = create_engine('postgresql://brus:brus@localhost/brus', echo=True)


meta = MetaData()
users = Table("users", meta, autoload=True, autoload_with=engine)
transactions = Table("transactions", meta, autoload=True, autoload_with=engine)
machine = Table("machine", meta, autoload=True, autoload_with=engine)
slot_product = Table("slot_product", meta, autoload=True, autoload_with=engine)
product = Table("product", meta, autoload=True, autoload_with=engine)

def add_user(name, realname="", phone="", email="", address=""):
    q = users.insert().values(username=name, realname=realname, email=email, address=address)
    try:
        engine.execute(q)
        return True
    except:
        pass
    return False

def set_password(user, password):
    q = users.update().where(users.c.username == user).values(password=sha256hash(password))
    engine.execute(q)

def authenticate(user, password):
    q = select([users]).where(users.c.username==user).where(users.c.password==sha256hash(password)).where(users.c.enabled==1)
    for row in engine.execute(q):
        print(row)
        return True
    return False

def authenticate_admin(user, password):
    q = select([users]).where(users.c.username==user).where(users.c.password==sha256hash(password)).where(users.c.admin==1)
    for row in engine.execute(q):
        return True
    return False

def get_email(user):
    q = select([users.c.email]).where(users.c.username==user)
    r = engine.execute(q).fetchone()
    if r:
        return r[0]
    return ""

def add_funds(user,value,descr=""):
    r = engine.execute(text("INSERT INTO transactions (uid,value,descr) SELECT DISTINCT users.uid, :value, :descr FROM users WHERE username=:user"), value=value, descr=descr, user=user)

def subtract_funds(user, value, descr="", overdraft=False):
    if value < 0:
        return False
    if not overdraft:
        r = engine.execute(text("INSERT INTO transactions (uid, value, descr) SELECT DISTINCT users.uid,:nvalue,:descr FROM users, transactions WHERE transactions.uid=users.uid AND username=:user GROUP BY users.uid HAVING SUM(value) >= :value"), nvalue=-value,descr=descr,user=user,value=value)
        return r.rowcount > 0
    else:
        engine.execute(text("INSERT INTO transactions (uid, value, descr) SELECT DISTINCT users.uid,:nvalue,:descr FROM users WHERE users.username=:user"), nvalue=-value,descr=descr,user=user)
        return True

def subtract_funds_card(card, value, descr=""):
  if value < 0:
    return False
  r = engine.execute(text("INSERT INTO transactions (uid, value, descr) SELECT DISTINCT users.uid,:nvalue,:descr FROM users, transactions WHERE transactions.uid=users.uid AND card_data=:cdata GROUP BY users.uid HAVING SUM(value) >= :value"), nvalue=-value,descr=descr,cdata=card,value=value)
  return r.rowcount > 0


def balance(user):
    r = engine.execute(text("SELECT SUM(transactions.value) FROM transactions, users WHERE transactions.uid=users.uid AND users.username=:user"), user=user)
    return r.fetchone()[0]

def transaction_history(user):
    q = select([transactions.c.tid, transactions.c.timestamp, transactions.c.descr, transactions.c.value]).where(transactions.c.uid==users.c.uid).where(users.c.username==user)
    return engine.execute(q).fetchall()

#def reset_password:
def list_users():
    q=select([users.c.username])
    return engine.execute(q).fetchall()

#def get_outgoing_transactions():
#    q=select()

def set_stripe_id(user,id):
    q = users.update().where(users.c.username == user).values(stripe_id=id)
    engine.execute(q)

def get_stripe_id(user):
    q=select([users.c.stripe_id]).where(users.c.username == user)
    r=engine.execute(q).fetchone()
    if r:
        return r[0]
    return r

def authenticate_machine(id, key):
    q = select([machine]).where(machine.c.machine==id).where(machine.c.key==key)
    for row in engine.execute(q):
        return True
    return False

def getproduct(machine, slot):
  q = select([slot_product.c.product]).where(slot_product.c.machine==machine).where(slot_product.c.slot==slot)
  r=engine.execute(q).fetchone()
  if r:
    return r[0]
  return None

def get_product_price_descr(pid):
  q = select([product.c.price, product.c.product]).where(product.c.pid==pid)
  return engine.execute(q).fetchone()

