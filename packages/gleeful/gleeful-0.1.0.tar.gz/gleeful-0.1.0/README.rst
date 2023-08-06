Gleeful: HomeKit Automation Protocol
====================================

This wraps the very useful `HAP-python` package to make creating new Accessories,
especially those with multiple services, really simple.


Here is an example::

  class Temperature(gleeful.Accessory):
      temperature = gleeful.services.temperature.DS18B20(sensor_id='28-00000000000')

      class AccessoryInformation:
          Name = 'Temperature'
          Manufacturer = 'Matthew Schinckel'
          Model = 'DS18B20'
          SerialNumber = '28-00000000000'


  Temperature(persist_file='/path/to/temperature.state').start()


Defining Services
------------------

Services must inherit from `gleeful.Service` in order for them to be correctly registered
with the accessory, and for the service attribute to be correctly determined::

  class PIR(gleeful.Service):
      service = 'MotionSensor'

      def __init__(self, *args, **kwargs):
          from gpio import MotionSensor
          self.motion = self.service.get_characteristic('MotionDetected')
          self.detector = gpiozero.MotionSensor(kwargs.pop('gpio_pin'))
          super().__init__(*args, **kwargs)

      def run(self, sentinel):
          self.detector.when_motion = lambda: self.motion.set_value(True)
          self.detector.when_no_motion = lambda: self.motion.set_value(False)


You will note a few things that are quite important in this example:

* You define the service on tha class as a string: this will be looked up from
  the HAP loader automatically, when using a class the service attribute will
  not be a string, but instead an instance of the HAP service that matches.

* The run method takes an extra argument: the sentinel that can be used to
  trigger repeating code or a stop situation. This is shared between all
  services within an accessory.

Why use this instead of `HAP-python`?
--------------------------------------

Gleeful makes it easy to have multiple services within a single accessory, and
encapsulating the logic within the service.

It also allows for you to serve directly from the accessory, by using `.start()`,
although you may also pass the accessory to a driver if you wish.
