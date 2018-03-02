import sys
import os
import time
import argparse

from handlers.bitfinex import BitfinexWebSocketClient


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--storage-path",
                        help="Path to store files (default /tmp)",
                        default="/tmp")
    parser.add_argument("-c", "--channel",
                        help="channel name (default ticker)",
                        default="ticker")
    parser.add_argument("-u", "--url",
                        help="server url (default wss://api.bitfinex.com/ws/)",
                        default="wss://api.bitfinex.com/ws/")
    return parser.parse_args()


def check_storage_path(storage_path):
    if not os.path.isdir(storage_path):
        try:
            os.makedirs(storage_path)
        except Exception as e:
            print("Cannot create dir: {}".format(e))
            return False
    return True

if __name__ == "__main__":
    args = parse_args()

    if not check_storage_path(args.storage_path):
        sys.exit(1)

    pairs = ['BTCUSD', 'LTCUSD', 'ETCUSD', 'ETHUSD', 'RRTUSD']
    threads = {}

    for pair in pairs:
        wss = BitfinexWebSocketClient(args.url, args.storage_path)
        wss.start()
        threads[pair] = wss

    # ждём коннекта
    time.sleep(1)
    for pair, wss in threads.items():
        wss.subscribe(args.channel, pair)

    try:
        for wss in threads.values():
            wss.join()
    except KeyboardInterrupt:
        print("Stopped by user...")
        # закрываем
        for wss in threads.values():
            wss.close()
        print("Closing...")
        # ждём закрытия
        for wss in threads.values():
            wss.join()
