import copy
import quopri
import sqlite3
import threading

from common.exception import RecordNotFoundException, DbCommitException, DbUpdateException, DbDeleteException
from patterns.behavioral_patterns import Subject, ConsoleWriter
from architectural_system_pattern_unit_of_work import DomainObject


# Абстрактный пользователь.
class User:
    auto_id = 1

    def __init__(self, name):
        self.id = User.auto_id
        User.auto_id += 1
        self.name = name


# Читатель.
class Reader(User):

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


class Note(NotePrototype, Subject):
    auto_id = 1

    def __init__(self, name, description, category):
        self.id = Note.auto_id
        Note.auto_id += 1
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
class Category:
    auto_id = 1

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.notes = []

    def notes_count(self):
        result = len(self.notes)
        if self.category:
            result += self.category.notes_count()
        return result


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

    def find_note_by_id(self, id):
        for item in self.notes:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет заметки с id = {id}')

    def get_new_note_id(self):
        max_id = 1
        for note in self.notes:
            if note.id > max_id:
                max_id = note.id

        for item in self.categories:
            for note in item.notes:
                if note.id > max_id:
                    max_id = note.id

        return max_id + 1

    def del_note_by_id(self, id):
        for item in self.notes:
            if item.id == id:
                self.notes.remove(item)

        for item in self.categories:
            for note in item.notes:
                if note.id == id:
                    item.notes.remove(note)

    def clear_notes_reader(self, reader_id):
        for item in self.notes:
            if item.reader:
                if item.reader.id == reader_id:
                    item.reader = None

        for item in self.categories:
            for note in item.notes:
                if note.reader:
                    if note.reader.id == reader_id:
                        note.reader = None

    def get_reader_by_id(self, id):
        for item in self.readers:
            if item.id == id:
                return item

    @staticmethod
    def create_note(type_, name, description, category):
        return NoteFactory.create(type_, name, description, category)

    def get_note_by_name(self, name):
        for item in self.notes:
            if item.name == name:
                return item
        return None

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
        self.tablename = 'reader'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
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
            return Reader(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        # Где взять obj.id? Добавить в DomainModel? Или добавить когда берем объект из базы
        self.cursor.execute(statement, (obj.name, obj.id))
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


connection = sqlite3.connect('patterns.sqlite')
