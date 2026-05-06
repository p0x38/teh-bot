import json
import logging
import os
import uuid
from collections.abc import MutableMapping
from datetime import datetime
from logging import FileHandler, Formatter, LoggerAdapter, getLogger
from typing import Any

from pytz import UTC
from rich.console import Console
from rich.logging import RichHandler

from src.config.schema import LoggerConfig
from src.utils.trace_context import trace_id_var

console = Console()


class TraceLoggerAdapter(LoggerAdapter):
    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        trace_id = trace_id_var.get(None)
        return f"[trace:{trace_id}] {msg}", kwargs


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        trace_id: uuid.UUID | None = trace_id_var.get(None)

        record.trace_id = str(trace_id) if trace_id else "-"

        return True


def load_log_config() -> LoggerConfig:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "assets", "logger_config.json")

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            return LoggerConfig.model_validate(data)
    except FileNotFoundError:
        return LoggerConfig()
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in logger_config.json: {e}")
        return LoggerConfig()
    except OSError as e:
        print(f"OS Error: {e}")
        return LoggerConfig()


def setup_logger(name: str = "teh-bot"):
    config = load_log_config()

    logger = getLogger(name)
    level = getattr(logging, config.level, logging.INFO)
    logger.setLevel(level)

    if logger.handlers:
        logger.handlers.clear()

    rich_handler = RichHandler(
        rich_tracebacks=config.console_logging.rich_tracebacks,
        markup=config.console_logging.markup,
        console=console,
        show_time=True,
    )
    rich_handler.addFilter(TraceIdFilter())
    logger.addHandler(rich_handler)

    if config.file_logging.enabled:
        log_dir = config.file_logging.directory
        os.makedirs(log_dir, exist_ok=True)

        filename = f"{log_dir}/{datetime.now(UTC).strftime('%Y-%m-%d')}.log"

        file_handler = FileHandler(filename, encoding=config.file_logging.encoding)
        file_handler.addFilter(TraceIdFilter())

        file_handler.setFormatter(
            Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s [trace=%(trace_id)s]: %(message)s")
        )

        logger.addHandler(file_handler)

    return TraceLoggerAdapter(logger, {})


log = setup_logger()
