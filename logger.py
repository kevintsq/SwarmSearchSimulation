import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import sys


class Logger:
    def __init__(self):
        debug_queue = Queue(-1)  # no limit on size
        debug_queue_handler = QueueHandler(debug_queue)
        debug_handler = logging.StreamHandler(sys.stdout)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(logging.Formatter('%(levelname)s:\t%(message)s'))
        self.debug_listener = QueueListener(debug_queue, debug_handler, respect_handler_level=True)

        info_queue = Queue(-1)  # no limit on size
        info_queue_handler = QueueHandler(info_queue)
        info_handler = logging.FileHandler("results.csv", "w", "utf-8")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(logging.Formatter('%(message)s'))
        self.info_listener = QueueListener(info_queue, info_handler, respect_handler_level=True)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(debug_queue_handler)
        self.logger.addHandler(info_queue_handler)

    def start(self):
        self.debug_listener.start()
        self.info_listener.start()

    def stop(self):
        self.debug_listener.stop()
        self.info_listener.stop()

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)
