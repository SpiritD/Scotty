import json
import websocket
from os import path
from datetime import datetime

from handlers.base_handler import BaseWebSocketClient
from handlers.common_file_handler import write_to_file

now = datetime.now

ERROR_CODES = {
    10000: "Unknown event",
    10001: "Unknown pair",
    10300: "Subscription failed (generic)",
    10301: "Already subscribed",
    10302: "Unknown channel",
    10400: "Unsubscription failed (generic)",
    10401: "Not subscribed"
}


class BitfinexWebSocketClient(BaseWebSocketClient):
    def subscribe(self, channel, pair, write_every_second=False):
        if not self.is_connected:
            print("Error: not connected.")
            return
        subscribe_data = {'event': 'subscribe', 'channel': channel,
                          'symbol': pair}
        self.pair_name = pair
        self.file_path = path.join(self.storage_dir, self.pair_name)
        self.write_every_second = write_every_second
        try:
            print("subscribe: {} {}".format(channel, pair))
            self.socket.send(json.dumps(subscribe_data))
        except websocket.WebSocketConnectionClosedException:
            print("send() error:", subscribe_data)

    def _on_message(self, ws, message):
        print("On message %s" % message)
        data = json.loads(message)
        # согласно протоколу 11 полей
        # https://docs.bitfinex.com/v1/reference#ws-public-ticker
        if isinstance(data, list):
            # если "биение сердца"
            if len(data) == 2:
                # если нужно записывать каждую секунду
                if self.write_every_second and data[1] == 'hb':
                    if self.last_data:
                        # пишем последние данные
                        self.save_data(self.last_data)
            elif len(data) == 11:
                self.save_data(data)
                if self.write_every_second:
                    self.last_data = data

        elif isinstance(data, dict):
            if data.get("event") == "error":
                err_code = data.get("code")
                if err_code:
                    return self.error_handle(err_code)

    def save_data(self, data):
        # Стакан отображает суммарное количество отложенных заявок на
        # покупку и продажу контрактов или акций по каждой цене выше и
        # ниже рыночной цены.
        depth_of_market = ' '.join([str(i) for i in data[1:5]])
        msg_line = "{} {} {}".format(data[7], now().timestamp(),
                                     depth_of_market)
        write_to_file(self.file_path, msg_line)

    def error_handle(self, err_code):
        if err_code in ERROR_CODES:
            print("Error: %s" % ERROR_CODES.get(err_code))
