CREATE TABLE machine (
    machine text NOT NULL,
    key text
);

CREATE TABLE product (
    pid integer NOT NULL,
    product text,
    price integer
);

CREATE SEQUENCE product_pid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE product_pid_seq OWNED BY product.pid;

CREATE TABLE slot_product (
    spid integer NOT NULL,
    slot integer,
    machine text,
    product integer
);

CREATE SEQUENCE slot_product_spid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE slot_product_spid_seq OWNED BY slot_product.spid;

CREATE TABLE transactions (
    tid integer NOT NULL,
    uid integer,
    value integer,
    descr text,
    "timestamp" timestamp without time zone DEFAULT now(),
    machine text,
    product integer,
    "user" text,
    username text
);

CREATE SEQUENCE transactions_tid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE transactions_tid_seq OWNED BY transactions.tid;

CREATE TABLE users (
    uid integer NOT NULL,
    username text NOT NULL,
    card_data text,
    enabled integer DEFAULT 1 NOT NULL,
    admin integer DEFAULT 0 NOT NULL,
    access_areas text,
    phone text,
    email text,
    address text,
    realname text,
    password text,
    sshkey text,
    stripe_id text
);

CREATE SEQUENCE users_uid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE users_uid_seq OWNED BY users.uid;

ALTER TABLE ONLY product ALTER COLUMN pid SET DEFAULT nextval('product_pid_seq'::regclass);
ALTER TABLE ONLY slot_product ALTER COLUMN spid SET DEFAULT nextval('slot_product_spid_seq'::regclass);
ALTER TABLE ONLY transactions ALTER COLUMN tid SET DEFAULT nextval('transactions_tid_seq'::regclass);
ALTER TABLE ONLY users ALTER COLUMN uid SET DEFAULT nextval('users_uid_seq'::regclass);

ALTER TABLE ONLY machine
    ADD CONSTRAINT machine_pkey PRIMARY KEY (machine);
ALTER TABLE ONLY product
    ADD CONSTRAINT product_pkey PRIMARY KEY (pid);
ALTER TABLE ONLY slot_product
    ADD CONSTRAINT slot_product_pkey PRIMARY KEY (spid);
ALTER TABLE ONLY transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (tid);
ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uid);
ALTER TABLE ONLY users
    ADD CONSTRAINT users_username_key UNIQUE (username);
ALTER TABLE ONLY slot_product
    ADD CONSTRAINT slot_product_machine_fkey FOREIGN KEY (machine) REFERENCES machine(machine);
ALTER TABLE ONLY slot_product
    ADD CONSTRAINT slot_product_product_fkey FOREIGN KEY (product) REFERENCES product(pid);
ALTER TABLE ONLY transactions
    ADD CONSTRAINT transactions_machine_fkey FOREIGN KEY (machine) REFERENCES machine(machine);
ALTER TABLE ONLY transactions
    ADD CONSTRAINT transactions_product_fkey FOREIGN KEY (product) REFERENCES product(pid);
