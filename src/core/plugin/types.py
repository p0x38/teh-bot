from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .manager import PluginAPI

MutationRule = Callable[[str, Any], str]
Transformable = Callable[[str], str]


@dataclass
class PluginMeta:
    name: str
    version: str
    author: str = "unknown"
    description: str = ""


class Plugin:
    meta: PluginMeta

    def setup(self, api: "PluginAPI"):
        raise NotImplementedError
