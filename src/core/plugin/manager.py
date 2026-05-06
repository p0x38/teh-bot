import json
import os

from .registry import PluginRegistry
from .sandbox import load_plugin_module
from .types import Plugin


class PluginAPI:
    def __init__(self, manager: "PluginManager", plugin_name: str):
        self.manager = manager
        self.plugin_name = plugin_name

    def register_mutation(self, rule):
        self.manager.registry.mutations[self.plugin_name].append(rule)

    def register_transform(self, name: str, func):
        self.manager.registry.transforms[name] = func

    def get_config(self):
        return self.manager.configs.get(self.plugin_name, {})


class PluginManager:
    def __init__(self, base_path="src/plugins"):
        self.base_path = base_path
        self.registry = PluginRegistry()

        self.plugins: dict[str, Plugin] = {}
        self.configs: dict[str, dict] = {}

    def load_all(self):
        for name in os.listdir(self.base_path):
            path = os.path.join(self.base_path, name)
            if os.path.isdir(path):
                self.load_plugin(name)

    def load_plugin(self, name: str):
        plugin_path = os.path.join(self.base_path, name, "plugin.py")

        module = load_plugin_module(plugin_path)

        plugin: Plugin = module.plugin

        config_path = os.path.join(self.base_path, name, "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.configs[name] = json.load(f)
        else:
            self.configs[name] = {}

        api = PluginAPI(self, name)
        plugin.setup(api)

        self.plugins[name] = plugin

    def reload_plugin(self, name: str):
        self.registry.mutations[name].clear()

        self.load_plugin(name)

    def get_mutations(self, enabled_plugins: set[str]):
        rules = []
        for name in enabled_plugins:
            rules.extend(self.registry.mutations.get(name, []))
        return rules

    def get_transforms(self):
        return self.registry.transforms
