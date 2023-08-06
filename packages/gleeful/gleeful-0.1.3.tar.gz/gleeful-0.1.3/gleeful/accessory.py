import logging
import signal
import threading
import random

from collections import OrderedDict
import pyhap.accessory

from .services.base import Service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


class AccessoryBase(type):

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, AccessoryBase)]
        if not parents:
            return new_class

        if isinstance(new_class.category, str):
            new_class.category = getattr(pyhap.accessory.Category, attrs['category'])

        new_class._services = OrderedDict()

        for name, attr in attrs.items():
            if isinstance(attr, Service):
                new_class._services[name] = attr

        if not hasattr(new_class, 'AccessoryInformation'):
            new_class.AccessoryInformation = type('AccessoryInformation', (object,), {})

        return new_class


class Accessory(pyhap.accessory.Accessory, metaclass=AccessoryBase):
    def __init__(self, *args, **kwargs):
        self.persist_file = kwargs.pop('persist_file', 'accessory.state')
        self.port = kwargs.pop('port', random.randint(50000, 60000))
        super().__init__(*args, **kwargs)

    @property
    def driver(self):
        if not hasattr(self, '_driver'):
            from pyhap.accessory_driver import AccessoryDriver
            self._driver = AccessoryDriver(self, port=self.port, persist_file=self.persist_file)
            signal.signal(signal.SIGINT, self._driver.signal_handler)
            signal.signal(signal.SIGTERM, self._driver.signal_handler)
        return self._driver

    def start(self):
        self.driver.start()

    def get_accessory_information(self):
        info_service = pyhap.loader.get_serv_loader().get('AccessoryInformation')

        for attr in ['Manufacturer', 'Model', 'SerialNumber']:
            info_service.get_characteristic(attr).set_value(
                getattr(self.AccessoryInformation, attr, attr)
            )

        info_service.get_characteristic('Name').set_value(
            self.display_name
        )

        return info_service

    def _set_services(self):
        # We no longer need to define _set_services(), as we define this using attributes.
        self.add_service(self.get_accessory_information())
        for name, service in self._services.items():
            if service.service not in self.services:
                self.add_service(service.service)

    def run(self):
        super().run()
        for name, service in self._services.items():
            threading.Thread(target=service.run, name=name, args=[self.run_sentinel]).start()

    def stop(self):
        super().stop()
        for name, service in self._services.items():
            service.stop()
