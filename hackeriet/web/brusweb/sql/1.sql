CREATE TABLE users
        (uid INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
        card_data TEXT, enabled INTEGER NOT NULL DEFAULT 1, admin INTEGER NOT NULL DEFAULT 0,
        access_areas TEXT, phone TEXT, email TEXT, address TEXT, realname TEXT, password TEXT, sshkey TEXT);
CREATE TABLE transactions (tid INTEGER PRIMARY KEY, uid INTEGER, value INTEGER, descr TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

