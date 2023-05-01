from abc import ABC, abstractmethod
from enum import Enum, auto
import os
import sys

import config


class LoggerType(Enum):
    SQLite3 = auto()
    MySQL = auto()
    File = auto()


class Logger:
    __logger = None

    def __init__(self, logger_type=LoggerType.SQLite3):
        Logger.__logger = Logger.get_logger(logger_type)

    @staticmethod
    def get_logger(logger_type=LoggerType.SQLite3, robot_max_cnt=10, reset=False):
        if Logger.__logger is None:
            if logger_type == LoggerType.SQLite3:
                Logger.__logger = SQLite3Logger(robot_max_cnt, reset)
            elif logger_type == LoggerType.MySQL:
                Logger.__logger = MySQLLogger(robot_max_cnt, reset)
            else:
                Logger.__logger = FileLogger(robot_max_cnt, reset)
        return Logger.__logger

    def __enter__(self):
        return self.__logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__logger.__exit__(exc_type, exc_val, exc_tb)


class AbstractLogger(ABC):
    def __init__(self, robot_max_cnt=10):
        self.attributes_with_type = {"no": "INT",
                                     "site_width": "INT",
                                     "site_height": "INT",
                                     "room_cnt": "INT",
                                     "injury_cnt": "INT",
                                     "departure_position": "TEXT",
                                     "robot_type": "TEXT",
                                     "robot_cnt": "INT",
                                     "mode": "TEXT",
                                     "room_visited": "INT",
                                     "injury_rescued": "INT",
                                     "returned": "INT",
                                     "total_action_cnt": "INT"}
        for i in range(robot_max_cnt):
            self.attributes_with_type[f"robot_{i}_visits"] = "INT"
            self.attributes_with_type[f"robot_{i}_rescues"] = "INT"
            self.attributes_with_type[f"robot_{i}_collides"] = "INT"
        self.attributes = tuple(self.attributes_with_type.keys())

    @abstractmethod
    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def log(self, *items):
        """items must be a tuple of the same order as self.attributes!!!"""


class MySQLLogger(AbstractLogger):
    def __init__(self, robot_max_cnt=10, reset=False):
        super().__init__(robot_max_cnt)

        import mysql.connector

        self.db = mysql.connector.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD
        )
        self.cursor = self.db.cursor()
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS results;")
        self.cursor.execute(f"USE results;")
        if reset:
            self.cursor.execute(f"DROP TABLE IF EXISTS results;")
        self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS results ({','.join((' '.join(item) for item in self.attributes_with_type.items()))});")
        self.db.commit()

    def __del__(self):
        self.db.commit()
        self.db.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.commit()

    def log(self, *items):
        self.cursor.execute(f"INSERT INTO results ({','.join(self.attributes[:len(items)])}) VALUES {items!r};")


class SQLite3Logger(AbstractLogger):
    def __init__(self, robot_max_cnt, reset=False):
        super().__init__(robot_max_cnt)

        import sqlite3

        if not os.path.exists(config.RESULT_DIR):
            os.mkdir(config.RESULT_DIR)
        is_exist = os.path.exists(f"{config.RESULT_DIR}/results.db")
        if reset and is_exist:
            os.remove(f"{config.RESULT_DIR}/results.db")
        self.db = sqlite3.connect(f"{config.RESULT_DIR}/results.db")
        self.cursor = self.db.cursor()
        if reset or not is_exist:
            self.cursor.execute(
                f"CREATE TABLE results ({','.join((' '.join(item) for item in self.attributes_with_type.items()))});")
            self.db.commit()

    def __del__(self):
        self.db.close()

    def log(self, *items):
        self.cursor.execute(f"INSERT INTO results ({','.join(self.attributes[:len(items)])}) VALUES {items!r};")
        self.db.commit()


class FileLogger(AbstractLogger):
    """Must use a lock when using this logger in a multiprocessing environment!!!"""
    def __init__(self, robot_max_cnt=10, reset=False):
        super().__init__(robot_max_cnt)

        import logging
        from logging.handlers import QueueHandler, QueueListener
        from queue import Queue

        console_queue = Queue(-1)  # no limit on size
        console_queue_handler = QueueHandler(console_queue)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.CRITICAL)
        console_handler.setFormatter(logging.Formatter('%(levelname)s:\t%(message)s'))
        self.console_listener = QueueListener(console_queue, console_handler, respect_handler_level=True)

        file_queue = Queue(-1)  # no limit on size
        file_queue_handler = QueueHandler(file_queue)
        if not os.path.exists(config.RESULT_DIR):
            os.mkdir(config.RESULT_DIR)
        file_handler = logging.FileHandler(f"{config.RESULT_DIR}/results.csv", "w" if reset else "a", "utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.file_listener = QueueListener(file_queue, file_handler, respect_handler_level=True)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_queue_handler)
        self.logger.addHandler(file_queue_handler)

        self.console_listener.start()
        self.file_listener.start()

        if reset:
            self.log(*self.attributes)

    def __del__(self):
        self.console_listener.stop()
        self.file_listener.stop()

    def log(self, *items):
        self.logger.info(",".join(map(str, items)))

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def critical(self, msg):
        self.logger.critical(msg)
