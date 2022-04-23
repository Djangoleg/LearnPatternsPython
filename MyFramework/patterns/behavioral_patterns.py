import jsonpickle

from lite_framework.settings import SERVER_URL
from lite_framework.templator import render


# поведенческий паттерн - наблюдатель
# Курс
class Observer:

    def update(self, subject):
        pass


class Subject:

    def __init__(self):
        self.observers = []

    def notify(self):
        for item in self.observers:
            item.update(self)


class SmsNotifier(Observer):

    def update(self, subject):
        print('SMS->', 'установлен читатель заметки:', subject.reader.name)


class EmailNotifier(Observer):

    def update(self, subject):
        print(('EMAIL->', 'установлен читатель заметки:', subject.reader.name))


class BaseSerializer:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return jsonpickle.dumps(self.obj)

    @staticmethod
    def load(data):
        return jsonpickle.loads(data)


# поведенческий паттерн - Шаблонный метод
class TemplateView:
    template_name = 'template.html'

    def get_context_data(self):
        data = {}
        data['data'] = {'server_url': SERVER_URL}
        return data

    def get_template(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template()
        context = self.get_context_data()
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        return self.render_template_with_context()


class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context_object_name = 'objects_list'


    def get_queryset(self):
        print(self.queryset)
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        context = super().get_context_data()
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context[context_object_name] = queryset
        return context


class CreateView(TemplateView):
    template_name = 'create.html'

    @staticmethod
    def get_request_data(request):
        return request['data']

    def create_obj(self, data):
        pass

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = self.get_request_data(request)
            self.create_obj(data)

            return self.render_template_with_context()
        else:
            return super().__call__(request)

class DeleteView(ListView):

    @staticmethod
    def get_request_params(request):
        return request['request_params']

    def delete_obj(self, data):
        pass

    def __call__(self, request):
        if request['method'] == 'GET':
            request_params = self.get_request_params(request)
            self.delete_obj(request_params)
        return super().__call__(request)

# поведенческий паттерн - Стратегия
class ConsoleWriter:

    def write(self, text):
        print(text)


class FileWriter:

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, text):
        with open(self.file_name, 'a', encoding='utf-8') as f:
            f.write(f'{text}\n')

