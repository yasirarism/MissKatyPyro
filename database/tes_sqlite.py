# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2021 Amano Team

import sqlite3

db = sqlite3.connect("database/yasir.db")
dbc = db.cursor()


dbc.executescript(
    """
CREATE TABLE IF NOT EXISTS groups(
    chat_id INTEGER PRIMARY KEY,
    welcome TEXT,
    welcome_enabled INTEGER,
    rules TEXT,
    warns_limit INTEGER,
    chat_lang TEXT,
    cached_admins,
    antichannelpin INTEGER,
    delservicemsgs INTEGER,
    warn_action TEXT
);
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    chat_lang TEXT
);
CREATE TABLE IF NOT EXISTS channels(
    chat_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS was_restarted_at(
    chat_id INTEGER,
    message_id INTEGER
);
    """
)


db.commit()
