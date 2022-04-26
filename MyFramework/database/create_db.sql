
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
   user_id INTEGER,
   FOREIGN KEY (user_id)
      REFERENCES 'user' (id)
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

INSERT INTO 'user' (id, name, type_id) VALUES (1, 'Test_user_1', 1);
INSERT INTO 'user' (id, name, type_id) VALUES (2, 'Test_user_2', 1);

INSERT INTO note (id, name, description, user_id)
VALUES (1, 'map() function', '# Return double of n<br>def addition(n):<br>return n + n<br># We double all numbers using map()<br>numbers = (1, 2, 3, 4)<br>result = map(addition, numbers)<br>print(list(result))<br><br># ((''John'', ''Jenny''), (''Charles'', ''Christy''), (''Mike'', ''Monica''))', 1);
INSERT INTO note (id, name, description, user_id)
VALUES (2, 'zip() Function', 'a = ("John", "Charles", "Mike")<br> b = ("Jenny", "Christy", "Monica", "Vicky")<br>print(tuple(x))<br><br># ((''John'', ''Jenny''), (''Charles'', ''Christy''), (''Mike'', ''Monica''))', 2);

INSERT INTO category (id, name) VALUES (1, 'common');

INSERT INTO note_to_category (category_id, note_id) VALUES (1, 1);
INSERT INTO note_to_category (category_id, note_id) VALUES (1, 2);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
