import copy
import quopri
from common.exception import RecordNotFoundException, DbCommitException, DbUpdateException, DbDeleteException
from patterns.behavioral_patterns import Subject, ConsoleWriter
from patterns.architectural_pattern import DomainObject
import sqlite3
import threading


# Абстрактный пользователь.
class User:
    id = 0

    def __init__(self, name):
        self.name = name


# Читатель.
class Reader(User, DomainObject):

    def __init__(self, name):
        self.notes = []
        super().__init__(name)


# Редактор.
class Editor(User):
    pass


# Порождающий паттерн Абстрактная фабрика - фабрика пользователей.
class UserFactory:
    types = {
        'reader': Reader,
        'editor': Editor
    }

    # Порождающий паттерн Фабричный метод.
    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


# Порождающий паттерн Прототип - заметка
class NotePrototype:
    # Прототип заметок.

    def clone(self):
        return copy.deepcopy(self)


class Note(NotePrototype, Subject, DomainObject):
    id = 0

    def __init__(self, name, description, category):
        self.name = name
        self.description = description
        self.category = category
        self.category.notes.append(self)
        self.reader = None
        super().__init__()

    def add_reader(self, reader: Reader):
        self.reader = reader
        reader.notes.append(self)
        self.notify()

    def __eq__(self, other):
        return self.name == other.name and \
               self.description == other.description and \
               self.category.name == other.category.name


class DatabaseNote(Note):
    pass


class FileSystemNote(Note):
    pass


class CommonNote(Note):
    pass


class ObjectOrientedNote(Note):
    pass


class PatternNote(Note):
    pass


# Категория
class Category(DomainObject):
    id = 0

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.notes = []

    def notes_count(self):
        result = len(self.notes)
        if self.category:
            result += self.category.notes_count()
        return result

    def __eq__(self, other):
        return self.id == other.id


# Порождающий паттерн Абстрактная фабрика - фабрика записок
class NoteFactory:
    types = {
        'database': DatabaseNote,
        'filesystem': FileSystemNote,
        'common': CommonNote,
        'oop': ObjectOrientedNote,
        'pattern': PatternNote,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, description, category):
        return cls.types[type_](name, description, category)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.readers = []
        self.editors = []
        self.notes = []
        self.categories = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_note(type_, name, description, category):
        return NoteFactory.create(type_, name, description, category)

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')


# Порождающий паттерн Синглтон.
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)


class ReaderMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'user'

    def all(self):
        statement = f'SELECT id, name from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            reader = Reader(name)
            reader.id = id
            result.append(reader)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            reader = Reader(result[1])
            reader.id = result[0]
            return reader
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, type_id) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, 1,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class NoteMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'note'

    def all(self):
        statement = f'SELECT n.id, n.name, n.description, u.id, u.name, c.id, c.name ' \
                    f'FROM {self.tablename} n ' \
                    f'LEFT JOIN user u ON n.user_id = u.id ' \
                    f'LEFT JOIN note_to_category nc ON n.id = nc.note_id ' \
                    f'LEFT JOIN category c ON nc.category_id = c.id'

        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name, description, user_id, user_name, category_id, category_name  = item
            category = None
            reader = None
            if category_name:
                category = Engine.create_category(category_name, None)
                category.id = category_id
            if user_id:
                reader = Engine.create_user('reader', user_name)
                reader.id = user_id
            if id:
                note = Note(name, description, category)
                note.id = id
                if reader:
                    note.reader = reader
                result.append(note)

        return result

    def find_by_id(self, id):
        statement = f'SELECT n.id, n.name, n.description, c.id, c.name ' \
                    f'FROM {self.tablename} n ' \
                    f'LEFT JOIN note_to_category nc ON n.id = nc.note_id ' \
                    f'LEFT JOIN category c ON nc.category_id = c.id ' \
                    f'WHERE n.id=?'
        self.cursor.execute(statement, (id,))
        id, name, description, category_id, category_name = self.cursor.fetchone()
        if id:
            category = None
            if category_id:
                category = Engine.create_category(category_name, None)
                category.id = category_id

            note = Note(name, description, category)
            note.id = id
            return note
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def get_by_category_id(self, category_id):
        statement = f'SELECT n.id, n.name, n.description, u.id, u.name, c.id, c.name ' \
                    f'FROM {self.tablename} n ' \
                    f'LEFT JOIN user u ON n.user_id = u.id ' \
                    f'LEFT JOIN note_to_category nc ON n.id = nc.note_id ' \
                    f'LEFT JOIN category c ON nc.category_id = c.id ' \
                    f'WHERE c.id=?'
        self.cursor.execute(statement, (category_id,))
        result = []
        for item in self.cursor.fetchall():
            id, name, description, user_id, user_name, cat_id, category_name  = item
            category = Engine.create_category(category_name, None)
            category.id = cat_id
            note = Note(name, description, category)
            note.id = id
            result.append(note)
        return result

    def insert(self, obj):
        statement_note = f"INSERT INTO {self.tablename} (name, description, user_id) VALUES (?, ?, ?) returning id"
        reader_id = None
        if obj.reader:
            reader_id = obj.reader.id
        cursor = self.cursor.execute(statement_note, (obj.name, obj.description, reader_id,))

        if obj.category:
            statement_cat = f"INSERT INTO note_to_category (category_id, note_id) VALUES (?, ?)"
            self.cursor.execute(statement_cat, (obj.category.id, cursor.lastrowid,))

        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)

    def update_user_id(self, note_id, user_id):
        statement = f"UPDATE {self.tablename} SET user_id=? WHERE id=?"
        self.cursor.execute(statement, (user_id, note_id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def clear_user_id(self, user_id):
        statement = f"UPDATE {self.tablename} SET user_id=null WHERE user_id=?"
        self.cursor.execute(statement, (user_id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)


class CategoryMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'category'

    def all(self):
        statement = f'SELECT c.id, c.name, n.id, n.name, n.description, u.id, u.name ' \
                    f'FROM {self.tablename} c ' \
                    f'LEFT JOIN note_to_category nc ON c.id = nc.category_id ' \
                    f'LEFT JOIN note n ON nc.note_id = n.id ' \
                    f'LEFT JOIN user u ON n.user_id = u.id'

        result = []
        self.cursor.execute(statement)
        category_id = int()
        category = None
        for item in self.cursor.fetchall():
            id, name, note_id, note_name, note_description, user_id, user_name = item
            if id:
                if category_id != id:
                    category = Engine.create_category(name, None)
                    category.id = id
                    if note_name and note_description and category:
                        note = Note(note_name, note_description, category)
                        note.id = note_id
                        if note not in category.notes:
                            category.notes.append(note)
                else:
                    if note_name and note_description and category:
                        note = Note(note_name, note_description, category)
                        note.id = note_id
                        if note not in category.notes:
                            category.notes.append(note)

                category_id = id
                if category not in result:
                    result.append(category)

        return result

    def find_by_id(self, id):
        statement = f'SELECT c.id, c.name, n.id, n.name, n.description, u.id, u.name ' \
                    f'FROM {self.tablename} c ' \
                    f'LEFT JOIN note_to_category nc ON c.id = nc.category_id ' \
                    f'LEFT JOIN note n ON nc.note_id = n.id ' \
                    f'LEFT JOIN user u ON n.user_id = u.id ' \
                    f'WHERE c.id=?'
        result = []
        self.cursor.execute(statement, (id,))
        category_id = int()
        category = None
        for item in self.cursor.fetchall():
            id, name, note_id, note_name, note_description, user_id, user_name = item
            if id:
                if category_id != id:
                    category = Engine.create_category(name, None)
                    category.id = id
                    if note_name and note_description and category:
                        note = Note(note_name, note_description, category)
                        note.id = note_id
                        if note not in category.notes:
                            category.notes.append(note)
                else:
                    if note_name and note_description and category:
                        note = Note(note_name, note_description, category)
                        note.id = note_id
                        if note not in category.notes:
                            category.notes.append(note)

                category_id = id

                if category not in result:
                    result.append(category)

        if len(result) > 0:
            return result[0]
        else:
            return result

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)

connection = sqlite3.connect('database/pynotes.sqlite')

# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'reader': ReaderMapper,
        'note': NoteMapper,
        'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Reader):
            return ReaderMapper(connection)
        if isinstance(obj, Note):
            return NoteMapper(connection)
        if isinstance(obj, Category):
            return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)