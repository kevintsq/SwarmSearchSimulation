import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import sys

queue = Queue(-1)  # no limit on size

debug_queue_handler = QueueHandler(queue)
debug_handler = logging.StreamHandler(sys.stdout)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter('%(levelname)s:\t%(message)s'))
debug_listener = QueueListener(queue, debug_handler)

info_queue_handler = QueueHandler(queue)
info_handler = logging.FileHandler("results.csv", "w")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(message)s'))
info_listener = QueueListener(queue, info_handler)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(debug_queue_handler)
logger.addHandler(info_queue_handler)

debug_listener.start()
info_listener.start()
# debug_listener.stop()
# info_listener.stop()
