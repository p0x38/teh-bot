import importlib.util
import sys


def load_plugin_module(path: str):
    spec = importlib.util.spec_from_file_location("plugin", path)
    module = importlib.util.module_from_spec(spec)

    module.__dict__["__builtins__"] = __builtins__

    sys.modules[path] = module
    spec.loader.exec_module(module)

    return module
