import copy
import quopri

# Абстрактный пользователь.
class User:
    pass

# Читатель.
class Reader(User):
    pass

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
    def create(cls, type_):
        return cls.types[type_]()

# Порождающий паттерн Прототип - заметка
class NotePrototype:
    # Прототип заметок.

    def clone(self):
        return copy.deepcopy(self)


class Note(NotePrototype):

    def __init__(self, name, description, category):
        self.name = name
        self.description = description
        self.category = category
        self.category.notes.append(self)

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

# Категория.
class Category:
    auto_id = 0

    def __init__(self, name, description, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.description = description
        self.category = category
        self.notes = []

    def note_count(self):
        result = len(self.notes)
        if self.category:
            result += self.category.note_count()
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
        self.reader = []
        self.editor = []
        self.notes = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_note(type_, name, description, category):
        return NoteFactory.create(type_, name, description, category)

    def get_course(self, name):
        for item in self.notes:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')

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

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)
