import logging
import logging.config
import rich.logging

def setup_logging(level="INFO") -> logging.Logger:
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
                "level": level,
                "formatter": "simple",
                "()": "rich.logging.RichHandler",
                "rich_tracebacks": True,
                "show_time": False
            },
        },
        "loggers": {"root": {"level": level, "handlers": ["stdout"]}},
    }
    logging.config.dictConfig(config=logging_config)
    return logging.getLogger(__name__)