from pyhap import loader


class ServiceBase(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, ServiceBase)]
        if not parents:
            return new_class

        if isinstance(new_class.service, str):
            new_class.service = loader.get_serv_loader().get(new_class.service)

        return new_class


class Service(object, metaclass=ServiceBase):
    def run(self, sentinel):
        pass

    def stop(self):
        pass
