from klein import Klein

from .handlers import Handler


class Application(Klein):
    middleware = {}

    def set_handler(self, path, handler, *args, **kwargs):
        assert issubclass(handler, Handler)

        handler_obj = handler.as_handler()
        kwargs.setdefault('methods', handler.allowed_methods())
        kwargs.setdefault('endpoint', f'{handler_obj.__module__}.{handler_obj.__name__}')
        self.route(path, *args, **kwargs)(handler_obj)

    def __getitem__(self, item):
        if item not in self.middleware:
            raise KeyError(f'Middleware {item} is not registered')
        return self.middleware[item]

    def __setitem__(self, key, value):
        self.middleware[key] = value

    def __len__(self):
        return len(self.middleware)
