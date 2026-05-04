from datetime import datetime
import json
from logging import FileHandler, Formatter, Logger, basicConfig, getLogger
import logging
import os
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

console = Console()

def load_log_config() -> dict[str, Any]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "assets", "logger_config.json")
    
    defaults = {
        "level": "INFO",
        "file_logging": {"enabled": True, "directory": "logs", "encoding": "utf-8"},
        "console_logging": {"rich_tracebacks": True, "markup": True}
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return {**defaults, **json.load(f)}
        except Exception as e:
            print(f"Warning: Could not load logger_config.json ({e}). Using defaults.")
    
    return defaults

def setup_logger(name: str = "teh-bot") -> Logger:
    config = load_log_config()
    logger = getLogger(name)
    
    level = getattr(logging, config["level"].upper(), logging.INFO)
    logger.setLevel(level)
    
    if logger.hasHandlers():
        return logger
    
    rich_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        console=console,
        show_time=True
    )
    
    c_config = config["console_logging"]
    rich_handler = RichHandler(
        rich_tracebacks=c_config.get("rich_tracebacks", True),
        markup=c_config.get("markup", True),
        console=console,
        show_time=True
    )
    logger.addHandler(rich_handler)

    f_config = config["file_logging"]
    if f_config.get("enabled"):
        log_dir = f_config.get("directory", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(
            log_filename, 
            encoding=f_config.get("encoding", "utf-8")
        )
        
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger

log = setup_logger()