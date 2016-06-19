
# New quick and dirty DB interface

# TODO make use of the orm

from sqlalchemy import *
import hashlib

def sha256hash(self, string):
  if type(string) is str:
    s = string.encode()
  else:
    s = string
  return hashlib.sha256(s).hexdigest()

engine = create_engine('sqlite:///door.db', echo=True)

meta = MetaData()
users = Table("users", meta, autoload=True, autoload_with=engine)
transactions = Table("transactions", meta, autoload=True, autoload_with=engine)
machine = Table("machine", meta, autoload=True, autoload_with=engine)
slot_product = Table("slot_product", meta, autoload=True, autoload_with=engine)
product = Table("product", meta, autoload=True, autoload_with=engine)

ins = users.insert()
print(str(ins))

def add_user(name, realname="", phone="", email="", address=""):
    q = users.insert().values(username=name, realname=realname, email=email, address=address)
    try:
        engine.execute(q)
        return True
    except:
        pass
    return False

def set_password(user, password):
    q = users.update().where(users.c.username == user).values(password=sha256(password))
    engine.execute(q)

def authenticate_user(user, password):
    q = select([users]).where(users.c.username==user).where(users.c.password==password).where(users.c.enabled==1)
    for row in engine.execute(q):
        return True
    return False

def authenticate_admin(user, password):
    q = select([users]).where(users.c.username==user).where(users.c.password==password).where(users.c.admin==1)
    for row in engine.execute(q):
        return True
    return False

def get_email(user):
    q = select([users.c.email]).where(users.c.username==user)
    r = engine.execute(q).fetchone()
    if r:
        return r[0]
    return ""

def add_funds(user,value,desc=""):
    r = engine.execute("INSERT INTO transactions (uid,value,desc) SELECT DISTINCT users.uid, :value, :desc FROM users WHERE username=:user", value=value, desc=desc, user=user)

def subtract_funds(user, value, desc="", overdraft=False):
    if value < 0:
        return False
    if not overdraft:
        r = engine.execute("INSERT INTO transactions (uid, value, desc) SELECT DISTINCT users.uid,:nvalue,:desc FROM users, transactions WHERE transactions.uid=users.uid AND username=:user GROUP BY users.uid HAVING TOTAL(value) >= :value", nvalue=-value,desc=desc,user=user,value=value)
        if r.rowcount > 0:
            return True
        return False
    else:
        engine.execute("INSERT INTO transactions (uid, value, desc) SELECT DISTINCT users.uid,:nvalue,:desc FROM users WHERE users.username=:user", nvalue=-value,desc=desc,user=user)
        return True

def balance(user):
    r = engine.execute("SELECT TOTAL(transactions.value) FROM transactions, users WHERE transactions.uid=users.uid AND users.username=:user", user=user)
    r.fetchone()[0]

def transaction_history(user):
    q = select([transactions.c.tid, transactions.c.timestamp, transactions.c.desc, transactions.c.value]).where(transactions.c.uid==users.c.uid).where(users.c.username==user)
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

#def authenticate_machine(id, key):

#def getproduct(machine, column)

