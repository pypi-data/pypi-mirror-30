from abc import ABCMeta, abstractmethod


class Component:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cloud_driver(self): pass

