from abc import ABCMeta
from abc import abstractmethod


class VirtualTrafficGeneratorResourceDriverInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_inventory(self, context):
        pass

    @abstractmethod
    def connect_child_resources(self, context):
        pass
