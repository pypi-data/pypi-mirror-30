from . import Application


class Server(object):
    app: Application = Application()

    def __init__(self, host: str, port: int, debug: bool=False) -> None:
        self.app_host = host
        self.app_port = port
        self.debug = debug

    def run(self):
        self.app.run(host=self.app_host, port=self.app_port)
