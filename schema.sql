CREATE TABLE accounts (
    owner_id bigint,
    balance bigint,
    items json,
    settings json,
    pet_bars json,
    pets VARCHAR[]
)

CREATE TABLE pets (
    owner_id bigint,
    type VARCHAR,
    earns bigint,
    name VARCHAR,
    level bigint,
    age VARCHAR,
    kenneled boolean,
    hunger bigint,
    thirst bigint,
    species VARCHAR
)

CREATE TABLE kennel (
    owner_id bigint,
    name VARCHAR,
    overdue boolean,
    release_date timestamp
)

CREATE TABLE tokens (
    token VARCHAR,
    error VARCHAR
)

CREATE TABLE usage (
    usage json
)