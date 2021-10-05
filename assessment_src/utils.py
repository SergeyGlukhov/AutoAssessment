import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

import alembic.command
import alembic.config


def setup_logging(log_config: dict):
    handlers = [logging.StreamHandler(stream=sys.stdout)]
    if log_config.get("file_path"):
        file_path = log_config.get("file_path")
        if not os.path.isfile(file_path):
            open(file_path, "a").close()
        handlers.append(
            TimedRotatingFileHandler(when="d", filename=file_path, backupCount=30)
        )
    logging.basicConfig(
        format=log_config["format"],
        style=log_config["style"],
        level=log_config["logger_level"],
        handlers=handlers,
    )
    gino_logger = logging.getLogger("gino")
    gino_logger.setLevel(logging.WARNING)


def run_migrations():
    conf = alembic.config.Config("alembic.ini")
    conf.attributes["configure_logger"] = False
    alembic.command.upgrade(conf, "head")
