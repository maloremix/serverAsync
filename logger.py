# app_logger.py
import logging
from datetime import datetime

_log_format = f"""%(time_request)s %(message)s; %(asctime)s.%(msecs)03d; %(message_answer)s """
_log_format_ignore = "%(time_request)s %(message)s; проигнорировано; %(message_answer)s"
def get_file_handler(log_format):
    file_handler = logging.FileHandler("x.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, "%Y-%m-%d; %H:%M:%S"))
    return file_handler

def get_logger(name, log_format):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler(log_format))
    return logger

logger1 = get_logger("log_default", _log_format)
logger2 = get_logger("log_ignore", _log_format_ignore)
logger1.propagate = False
logger2.propagate = False

def log_server(time_request, message_request, message_answer, ignore=False):
    if not ignore:
        logger_out = logging.LoggerAdapter(logger1, {"time_request": time_request, "message_answer": message_answer})
    else:
        logger_out = logging.LoggerAdapter(logger2, {"time_request": time_request, "message_answer": message_answer})
    logger_out.info(message_request)