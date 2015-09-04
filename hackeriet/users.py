import sqlite3
import hashlib

# TODO
# Split DB/User, make object oriented
 
class Users:
    def __init__(self, file="door.db"):
        self.db = sqlite3.connect(file)
        self.db.execute('''CREATE TABLE IF NOT EXISTS users
        (uid INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
        card_data TEXT, enabled INTEGER NOT NULL DEFAULT 1, admin INTEGER NOT NULL DEFAULT 0,
        access_areas TEXT, phone TEXT, email TEXT, address TEXT, realname TEXT, password TEXT, sshkey TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS transactions (tid INTEGER PRIMARY KEY, uid INTEGER, value INTEGER, desc TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.db.commit()

    def sha256hash(self, string):
        return hashlib.sha256(string.encode()).hexdigest()

    def add_user(self, name, realname="", phone="", email="", address=""):
        with self.db:
            self.db.execute("INSERT INTO users (username, realname, phone, email, address) VALUES (?, ?, ?, ?, ?)", (name, realname, phone, email, address))
        self.db.commit()

    def get_card_data(self, user):
        for row in self.db.execute("SELECT card_data FROM users where enabled = 1 AND username = ?", [user]):
            return row[0]

    def update_card_data(self, user, data):
        with self.db:
            self.db.execute("UPDATE users SET card_data = ? WHERE username = ?", (data, user))
        self.db.commit()

    def get_card_user(self, data):
        for row in self.db.execute("SELECT username FROM users WHERE enabled = 1 AND card_data = ?", [data]):
            return row[0]

    def authenticate(self, user, password):
        for row in self.db.execute("SELECT enabled FROM users WHERE username=? AND password=? AND enabled=1", (user, self.sha256hash(password))):
            return True
        return False

    def authenticate_admin(self, user, password):
        for row in self.db.execute("SELECT enabled FROM users WHERE username=? AND password=? AND enabled=1 AND admin=1", (user, self.sha256hash(password))):
            return True
        return False

    def set_password(self, user, password):
        self.db.execute("UPDATE users SET password=? WHERE username=?", (self.sha256hash(password), user))
        self.db.commit()

    def add_funds(self, user, value, desc=""):
        with self.db:
            self.db.execute("INSERT INTO transactions (uid,value,desc) SELECT DISTINCT users.uid, ?, ? FROM transactions, users WHERE transactions.uid=users.uid AND username=?", (value, desc, user))
        self.db.commit()

    def subtract_funds(self, user, value, desc="", overdraft=False):
        if value < 0:
            return False
        if not overdraft:
            with self.db:
                c = self.db.execute("INSERT INTO transactions (uid, value, desc) SELECT DISTINCT users.uid,?,? FROM transactions, users WHERE transactions.uid=users.uid AND users.username=? GROUP BY users.uid HAVING TOTAL(value) >= ?", (-value, desc, user, value))
            self.db.commit()
            if c.rowcount > 0:
                return True
            else:
                return False
        else:
            with self.db:
                self.db.execute("INSERT INTO transactions (uid, value, desc) SELECT DISTINCT users.uid,?,? FROM transactions, users WHERE transactions.uid=users.uid AND users.username=?", (-value, desc, user))
            self.db.commit()
            return True

    def balance(self, user):
        a = self.db.execute("SELECT TOTAL(transactions.value) FROM transactions, users WHERE transactions.uid=users.uid AND users.username=?", [user])
        return a.fetchone()[0]

    def transaction_history(self, user):
        a = self.db.execute("SELECT tid,timestamp,desc,value FROM transactions, users WHERE transactions.uid=users.uid AND users.username=? ORDER BY tid DESC", [user])
        return a.fetchall()

    # reset_password

    def list_users(self):
        return self.db.execute("SELECT username FROM users").fetchall()

if __name__ == "__main__":
    users = Users()


