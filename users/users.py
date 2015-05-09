import sqlite3

class Users:
    def __init__(self, file="door.db"):
        self.db = sqlite3.connect(file)
        self.db.execute('''CREATE TABLE IF NOT EXISTS users
        (uid INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
        card_data TEXT, enabled INTEGER NOT NULL DEFAULT 1, access_areas TEXT,
        phone TEXT, email TEXT, address TEXT, realname TEXT)''')

    def add_user(self, name, realname="", phone="", email="", address=""):
        #try:
            with self.db:
                self.db.execute("INSERT INTO users (username, realname, phone, email, address) VALUES (?, ?, ?, ?, ?)", (name, realname, phone, email, address))
        #except sqlite3.IntegrityError:
        #    print("Unable to add user")
        #    return("Integrity error")

    def get_card_data(self, user):
        for row in self.db.execute("SELECT card_data FROM users where enabled = 1 AND username = ?", [user]):
            return row[0]

    def update_card_data(self, user, data):
        #try:
            with self.db:
                self.db.execute("UPDATE users SET card_data = ? WHERE username = ?", (data, user))
        #except sqlite3.IntegryError:
        #    print("Unable to update database")

    def get_card_user(self, data):
        for row in self.db.execute("SELECT username FROM users WHERE enabled = 1 AND card_data = ?", [data]):
            return row[0]


if __name__ == "__main__":
    users = Users()


