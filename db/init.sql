CREATE USER replacerepl_name WITH REPLICATION ENCRYPTED PASSWORD 'replacerepl_pass';

CREATE TABLE IF NOT EXISTS emails (
    email_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS numbers (
    number_id SERIAL PRIMARY KEY,
    number VARCHAR(255) NOT NULL
);

INSERT INTO emails (email) VALUES ('test1@example.com'), ('test2@example.com');
INSERT INTO numbers (number) VALUES ('1234567890'), ('0987654321');
