CREATE TABLE apis (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    apiid TEXT NOT NULL,
    shortname TEXT NOT NULL,
    version TEXT,
    desc TEXT,
    params TEXT,
    apigroup TEXT,
    example TEXT,
    success TEXT,
    error TEXT
);
