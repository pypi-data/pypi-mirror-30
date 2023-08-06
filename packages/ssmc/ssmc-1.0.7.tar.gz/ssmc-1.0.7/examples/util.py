import logging
import sys
import time
from contextlib import contextmanager


# common logger
def get_logger():
    # logger
    logger = logging.getLogger(__name__)
    # set stream handler: output to stderr
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # # set stream handler: output to stdout
    # ch_metric = logging.FileHandler(filename=f"log/{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.log")
    # ch_metric.setLevel(MEASURE_LOG_LEVEL)
    # formatter = logging.Formatter('%(message)s')
    # ch_metric.setFormatter(formatter)
    # logger.addHandler(ch_metric)

    return logger


# parse config
class Config(dict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self


def set_env(debug=False):
    from os import environ
    config = Config()
    config.token = environ.get("SAKURA_CLOUD_API_KEY", None)
    config.secret = environ.get("SAKURA_CLOUD_API_SECRET_TOKEN", None)
    config.zone = environ.get("SAKURA_CLOUD_ZONE", "tk1v")
    config.debug = environ.get("SAKURA_CLOUD_API_DEBUG", False)
    config.base_url = environ.get("SAKURA_CLOUD_BASE_URL", "https://secure.sakura.ad.jp/cloud")
    config.common_service_item_master_zone = environ.get("SAKURA_CLOUD_COMMON_ITEM_MASTER_ZONE", "is1a")
    if config.token is None or config.secret is None:
        raise RuntimeError("Please set SAKURA_CLOUD_API_KEY and SAKURA_CLOUD_API_SECRET_TOKEN")
    return config


# log level
MEASURE_LOG_LEVEL = 25


@contextmanager
def measure(name: str, logger: logging.Logger):
    """実行時間を測る用"""
    t1 = time.time()
    yield
    t2 = time.time()
    logger.log(MEASURE_LOG_LEVEL, f"{name}\t{t2-t1}")


# luhn アルゴリズム: ICCIDのチェックをしたいとき用
def add_check_digit(numStr):
    def check(numStr):
        d = list(map(int, numStr))
        return (sum(d[-1::-2]) + sum([sum(divmod(2 * x, 10)) for x in d[-2::-2]])) % 10

    def genCheckDigit(numStr):
        digit = check(numStr + "0")
        return (10 - digit) % 10

    return numStr + str(genCheckDigit(numStr))
