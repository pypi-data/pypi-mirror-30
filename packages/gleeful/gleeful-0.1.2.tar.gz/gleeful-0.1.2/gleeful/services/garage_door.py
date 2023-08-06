import logging
import time

from .base import Service


OPEN = 0        # Valid for target and current states
CLOSED = 1      # Valid for target and current states
OPENING = 2     # Valid only for current state
CLOSING = 3     # Valid only for current state
STOPPED = 4     # Valid only for current state

logger = logging.getLogger(__file__)


class GarageDoor(Service):
    service = 'GarageDoorOpener'

    def __init__(self, *args, **kwargs):
        self.setup_gpio(**kwargs.pop('gpio_pins'))
        self.current_state = self.service.get_characteristic('CurrentDoorState')
        self.target_state = self.service.get_characteristic('TargetDoorState')
        self.target_state.setter_callback = self.set_target
        super().__init__(*args, **kwargs)

    def set_target(self, value):
        """
        Defines the behaviour that should happen when a HomeKit trigger event
        is sent. This will have already set the target_state to the opposite to
        what it was before (ie, if the door was already open, or opening,
        then the target_state will now be closed). Keep in mind that target_state
        only has OPEN/CLOSED, so HomeKit is not able to model "stopped in the middle"
        very well.
        """

    def setup_gpio(self, **pins):
        """
        Override the things that need to happen when the system starts up, and
        pins need configuring.
        """

    def door_is_open(self):
        logger.info("Open")
        self.current_state.set_value(OPEN)
        self.target_state.value = OPEN
        self.target_state.notify()

    def door_is_opening(self):
        logger.info("Opening")
        self.current_state.set_value(OPENING)
        self.target_state.value = OPEN
        self.target_state.notify()
        # self.start_stopped_timer()

    def door_is_closed(self):
        logger.info("Closed")
        self.current_state.set_value(CLOSED)
        self.target_state.value = CLOSED
        self.target_state.notify()

    def door_is_closing(self):
        logger.info("Closing")
        self.current_state.set_value(CLOSING)
        self.target_state.value = CLOSED
        self.target_state.notify()
        # self.start_stopped_timer()


class SingleButtonTwoSensorGarageDoor(GarageDoor):
    def setup_gpio(self, **pins):
        from gpiozero import Button, LED
        self.relay = LED(pins['relay'])
        self.top_limit = Button(pins['top_limit'])
        self.bottom_limit = Button(pins['bottom_limit'])

    def run(self, sentinel):
        """
        This uses gpiozero, which means we can use the really nice event
        handlers it provides. We then just need to detect what the current
        state is at startup, and set that in HomeKit.
        """
        self.top_limit.when_pressed = self.door_is_open
        self.top_limit.when_released = self.door_is_closing
        self.bottom_limit.when_pressed = self.door_is_closed
        self.bottom_limit.when_released = self.door_is_opening

        # Set initial state.
        if self.top_limit.is_pressed:
            self.door_is_open()
        elif self.bottom_limit.is_pressed:
            self.door_is_closed()

    def set_target(self, value):
        """
        This garage door system has a single button that triggers different
        behaviour depending upon the current state of the system. This mostly
        matches with the behaviour from HomeKit, with one exception: when the
        door is currently opening, a single press halts the door,
        and then a second press reverses the direction.

        The HomeKit assumption is that a single press reverses the direction,
        so we need to stop, wait for a second, and then re-trigger.

        However, if we are being set from HomeKit, then we know the target state,
        so we can be cleverer than the raw remote, and not trigger anything if
        we are already in that state (or heading towards it).
        """
        if self.current_state.value == self.target_state.value:
            return
        if self.current_state.value == OPENING:
            if self.target_state.value == OPEN:
                return
            self.trigger_button()
            time.sleep(1)
        if self.current_state.value == CLOSING and self.target_state.value == CLOSED:
            return
        self.trigger_button()

    def trigger_button(self):
        logger.info('Button pressed')
        self.relay.on()
        time.sleep(1)
        self.relay.off()
        logger.info('Button released')
