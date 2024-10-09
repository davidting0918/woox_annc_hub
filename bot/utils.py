import argparse
import logging
import os

import requests as req
from telegram import Bot


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


async def save_file(id: str, bot: Bot) -> dict:
    if id == "":
        return {
            "url": "",
            "path": "",
            "id": "",
        }

    info = await bot.get_file(id)
    url = info.file_path
    name = info.file_path.split("/")[-1]

    current_path = os.path.abspath(os.path.dirname(__file__))
    path = f"{os.path.join(current_path, 'db/files')}/{name}"

    res = req.get(url)
    with open(path, "wb") as f:
        f.write(res.content)
        f.close()

    result = {
        "url": url,
        "path": path,
        "id": id,
    }
    return result


def init_args(name: str):
    parser = argparse.ArgumentParser(name)
    parser.add_argument(
        "--test",
        action="store_true",
        default=False,
        help="Run in test mode, default is False",
    )
    return parser.parse_args()
