from collections import defaultdict


class PluginRegistry:
    def __init__(self):
        self.mutations = defaultdict(list)
        self.transforms = {}
