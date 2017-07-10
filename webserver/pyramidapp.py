from pyramid.config import Configurator
from pyramid.response import Response

def hello_word(request):
    return Response(
        'Hello world from Pyramid!\n',
        content_type='text/plain',
    )

config = Configurator()
config.add_route('hello', '/hello')
config.add_view(hello_word, route_name='hello')
print('DEBUG\tpyramid.config.Configurator')
app = config.make_wsgi_app()
