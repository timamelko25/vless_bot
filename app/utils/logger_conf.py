import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logging.root.handlers = []

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
    logging.getLogger("aiormq.connection").setLevel(logging.WARNING)
    logging.getLogger("aio_pika.robust_connection").setLevel(logging.WARNING)
    logging.getLogger("aio_pika.queue").setLevel(logging.WARNING)
    logging.getLogger("aio_pika.connection").setLevel(logging.WARNING)
    logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)
    logging.getLogger("aio_pika.exchange").setLevel(logging.WARNING)
    logging.getLogger("apscheduler.executors").setLevel(logging.WARNING)
    
    # for name in logging.root.manager.loggerDict:
    #     logging.getLogger(name).handlers = []
    #     logging.getLogger(name).propagate = True
    #     logging.getLogger(name).setLevel(logging.INFO)

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = []
        uv_logger.propagate = True
        uv_logger.setLevel(logging.INFO)
