import bglogs
import logging


def log_and_assert(caplog, level, method):

    name = "tests"
    msg = "test_default_{}".format(method.__name__)

    method(msg)

    for record in caplog.records:
        assert record.msg == msg
        assert record.name == name
        assert record.levelno == level


def test_default_info(caplog):
    log_and_assert(caplog, logging.INFO, bglogs.info)


def test_default_debug(caplog):
    log_and_assert(caplog, logging.DEBUG, bglogs.debug)


def test_default_warning(caplog):
    log_and_assert(caplog, logging.WARNING, bglogs.warning)


def test_default_error(caplog):
    log_and_assert(caplog, logging.ERROR, bglogs.error)


def test_default_critical(caplog):
    log_and_assert(caplog, logging.CRITICAL, bglogs.critical)
