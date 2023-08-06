from pathlib import Path
import subprocess
import random

from .base import Service


class TemperatureSensor(Service):
    service = 'TemperatureSensor'

    def __init__(self, *args, **kwargs):
        self.refresh_time = kwargs.pop('refresh', 10)
        self.current_temperature = self.service.get_characteristic('CurrentTemperature')
        super().__init__(*args, **kwargs)

    def update_temperature(self):
        current_temperature = self.read_current_temperature()
        if current_temperature is not None:
            self.current_temperature.set_value(current_temperature)

    def run(self, sentinel):
        self.update_temperature()
        while not sentinel.wait(self.refresh_time):
            self.update_temperature()


class FakeTemperature(TemperatureSensor):
    def __init__(self, *args, **kwargs):
        self.minimum_value = kwargs.pop('minimum', 0)
        self.maximum_value = kwargs.pop('maximum', 40)
        super().__init__(*args, **kwargs)

    def read_current_temperature(self):
        return random.randint(self.minimum_value, self.maximum_value)


class DS18B20(TemperatureSensor):
    def __init__(self, *args, **kwargs):
        self.sensor_id = kwargs.pop('sensor_id')
        super().__init__(*args, **kwargs)

    @property
    def temperature_file(self):
        return Path('/sys/bus/w1/devices/') / self.sensor_id / 'w1_slave'

    @property
    def temperature_raw_data(self):
        return self.temperature_file.open().read()

    def read_current_temperature(self):
        raw_data = self.temperature_raw_data.split('\n')
        if raw_data[0].strip().split()[-1] == 'YES':
            return float(raw_data[1].strip().split('t=')[1]) / 1000


class RemoteDS18B20(DS18B20):
    def __init__(self, *args, **kwargs):
        self.server = kwargs.pop('server')
        super().__init__(*args, **kwargs)

    @property
    def temperature_raw_data(self):
        return subprocess.check_output([
            'ssh',
            self.server,
            'cat',
            str(super().temperature_file)
        ]).decode('utf-8')
