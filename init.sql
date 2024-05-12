DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'tg_bot') THEN
        CREATE DATABASE tg_bot;
    END IF;
END $$;

\c tg_bot;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'emails') THEN
        CREATE TABLE emails (
            email_id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'numbers') THEN
        CREATE TABLE numbers (
            number_id SERIAL PRIMARY KEY,
            number VARCHAR(255) NOT NULL
        );
    END IF;
END $$;

INSERT INTO emails (email) VALUES ('test1@example.com'), ('test2@example.com');
INSERT INTO numbers (number) VALUES ('1234567890'), ('0987654321');

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'repl') THEN
        CREATE USER repl WITH REPLICATION ENCRYPTED PASSWORD '1234';
    END IF;
END $$;
