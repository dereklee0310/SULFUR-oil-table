import logging
import logging.config
import rich.logging

def setup_logging() -> logging.Logger:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        # "filters": {}
        "formatters": {
            # RichHandler do the job for us, so we don't need to incldue time & level
            "simple": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "stdout": {
                "level": "INFO",
                "formatter": "simple",
                "()": "rich.logging.RichHandler",
                "rich_tracebacks": True,
                "show_time": False
            },
        },
        "loggers": {"root": {"level": "INFO", "handlers": ["stdout"]}},
    }
    logging.config.dictConfig(config=logging_config)
    return logging.getLogger(__name__)