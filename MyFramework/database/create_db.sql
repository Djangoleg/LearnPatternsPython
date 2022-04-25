
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS user_type;
CREATE TABLE user_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR (50)
);

DROP TABLE IF EXISTS 'user';
CREATE TABLE 'user' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name VARCHAR (50),
    type_id INTEGER,
    FOREIGN KEY (type_id)
      REFERENCES user_type (id)
         ON DELETE SET NULL
         ON UPDATE NO ACTION
);

DROP TABLE IF EXISTS category;
CREATE TABLE category (
   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
   name TEXT NOT NULL
);

DROP TABLE IF EXISTS note;
CREATE TABLE note (
   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
   name TEXT NOT NULL,
   description TEXT NOT NULL,
   reader_id INTEGER,
   FOREIGN KEY (reader_id)
      REFERENCES reader (id)
         ON DELETE SET NULL
         ON UPDATE NO ACTION
);

DROP TABLE IF EXISTS note_to_category;
CREATE TABLE note_to_category (
    category_id INTEGER,
    note_id INTEGER,
    PRIMARY KEY (category_id, note_id),
    FOREIGN KEY (category_id)
      REFERENCES category (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION,
    FOREIGN KEY (note_id)
      REFERENCES note (id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
);

INSERT INTO user_type (id, name) VALUES (1, 'reader');
INSERT INTO user_type (id, name) VALUES (2, 'editor');

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
