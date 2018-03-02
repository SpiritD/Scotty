import websocket
from threading import Thread


class BaseWebSocketClient(Thread):
    def __init__(self, url, storage_dir):
        self.socket = None
        self.is_connected = False
        self.url = url
        self.storage_dir = storage_dir
        Thread.__init__(self)
        self.daemon = True

        self.pair_name = None
        self.file_path = None
        # записывать значения каждую секунду, даже если они не изменены
        self.write_every_second = None
        self.last_data = None

    def _on_open(self, ws):
        print("on_open")

    def _on_error(self, ws, error):
        print("Connection Error - %s", error)

    def _on_message(self, ws, message):
        raise NotImplementedError

    def _on_close(self, ws, *args):
        self.is_connected = False
        print("Connection closed")

    def _connect(self):
        self.socket = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self.is_connected = True

        self.socket.run_forever()

    def close(self):
        self.socket.close()

    def run(self):
        """Main method of Thread.

        :return:
        """
        print("Starting up.. {}".format(self.url))
        self._connect()
