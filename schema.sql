-- SQLite schema (no data)
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE config (
	id INTEGER NOT NULL, 
	"key" VARCHAR(50) NOT NULL, 
	value VARCHAR(200) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE ("key")
);
CREATE TABLE "course" (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                customer_id INTEGER NOT NULL,
                is_trial BOOLEAN DEFAULT 0,
                trial_price FLOAT,
                source VARCHAR(50),
                trial_status VARCHAR(20) DEFAULT 'registered',
                refund_amount FLOAT DEFAULT 0,
                refund_fee FLOAT DEFAULT 0,
                course_type VARCHAR(50),
                sessions INTEGER,
                price FLOAT,
                cost FLOAT,
                gift_sessions INTEGER DEFAULT 0,
                other_cost FLOAT DEFAULT 0,
                payment_channel VARCHAR(50),
                converted_from_trial INTEGER,
                converted_to_course INTEGER,
                created_at DATETIME,
                updated_at DATETIME, refund_channel VARCHAR(50), snapshot_course_cost FLOAT DEFAULT 0, snapshot_fee_rate FLOAT DEFAULT 0, meta TEXT,
                FOREIGN KEY (customer_id) REFERENCES customer (id),
                FOREIGN KEY (converted_from_trial) REFERENCES course (id),
                FOREIGN KEY (converted_to_course) REFERENCES course (id)
            );
CREATE TABLE customer (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	gender VARCHAR(10), 
	grade VARCHAR(50), 
	region VARCHAR(100), 
	phone VARCHAR(20) NOT NULL, 
	source VARCHAR(50), 
	employee_id INTEGER, 
	created_at DATETIME, has_tutoring_experience VARCHAR(10), 
	PRIMARY KEY (id), 
	UNIQUE (phone), 
	FOREIGN KEY(employee_id) REFERENCES employee (id)
);
CREATE TABLE employee (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE taobao_order (
	id INTEGER NOT NULL, 
	name VARCHAR(100), 
	level VARCHAR(50), 
	amount FLOAT, 
	commission FLOAT, 
	evaluated BOOLEAN, 
	order_time DATETIME, 
	created_at DATETIME, settled BOOLEAN DEFAULT 0, settled_at DATETIME, taobao_fee FLOAT DEFAULT 0, 
	PRIMARY KEY (id)
);
COMMIT;
