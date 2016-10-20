CREATE TABLE machine (machine TEXT PRIMARY KEY,
  key TEXT);

CREATE TABLE slot_product (spid INTEGER PRIMARY KEY,
  slot INTEGER,
  machine TEXT references machine,
  product INTEGER references product);

CREATE TABLE product (pid INTEGER PRIMARY KEY,
  product TEXT,
  price INTEGER);

ALTER TABLE transactions ADD machine TEXT references machine;
ALTER TABLE transactions ADD product INTEGER references product;
ALTER TABLE users ADD stripe_id TEXT;


