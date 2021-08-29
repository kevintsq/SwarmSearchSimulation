import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import sys


class Logger:
    def __init__(self):
        console_queue = Queue(-1)  # no limit on size
        console_queue_handler = QueueHandler(console_queue)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.CRITICAL)
        console_handler.setFormatter(logging.Formatter('%(levelname)s:\t%(message)s'))
        self.console_listener = QueueListener(console_queue, console_handler, respect_handler_level=True)

        file_queue = Queue(-1)  # no limit on size
        file_queue_handler = QueueHandler(file_queue)
        file_handler = logging.FileHandler("results.csv", "w", "utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.file_listener = QueueListener(file_queue, file_handler, respect_handler_level=True)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_queue_handler)
        self.logger.addHandler(file_queue_handler)

    def start(self):
        self.console_listener.start()
        self.file_listener.start()

    def stop(self):
        self.console_listener.stop()
        self.file_listener.stop()

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def critical(self, msg):
        self.logger.critical(msg)
