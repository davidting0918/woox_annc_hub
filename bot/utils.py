import logging


def get_logger(name: str):
    log_path_map = {"EventBot": "log/event_bot.log", "CommandBot": "log/command_bot.log"}
    logger = logging.getLogger(name)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_path_map[name])
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger
