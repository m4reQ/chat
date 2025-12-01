CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(256) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash BINARY(60) NOT NULL,
    country_code CHAR(2) NOT NULL,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT NOW(),
    last_active DATETIME NOT NULL DEFAULT NOW(),
    current_activity_status ENUM("ACTIVE", "OFFLINE", "BRB", "DONT_DISTURB") NOT NULL DEFAULT "OFFLINE",
    last_set_user_activity_status ENUM("ACTIVE", "BRB", "DONT_DISTURB") NOT NULL DEFAULT "ACTIVE");

CREATE TABLE chat_rooms(
    id SERIAL PRIMARY KEY,
    name VARCHAR(256),
    type ENUM("PUBLIC", "PRIVATE", "INTERNAL") NOT NULL,
    owner BIGINT UNSIGNED,

    FOREIGN KEY (owner) REFERENCES users(id));

CREATE TABLE chat_room_users(
    id SERIAL PRIMARY KEY,
    room_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,

    FOREIGN KEY (room_id) REFERENCES chat_rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id));

CREATE TABLE api_keys(
    id SERIAL PRIMARY KEY,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    api_key CHAR(32) UNIQUE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT NOW());

DELIMITER //

CREATE PROCEDURE GenerateNewAPIKey()
BEGIN
    INSERT INTO api_keys(api_key) VALUES(REPLACE(uuid(), "-", ""));
END //