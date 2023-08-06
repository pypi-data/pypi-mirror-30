import subprocess

from .base import Service, characteristic


def get_display_state():
    result = subprocess.check_output(['pmset', '-g', 'powerstate', 'IODisplayWrangler'])
    return int(result.strip().split(b'\n')[-1].split()[1]) >= 4


def set_display_state(state):
    if state:
        subprocess.call(['caffeinate', '-u', '-t', '1'])
    else:
        subprocess.call(['pmset', 'displaysleepnow'])


class DisplaySwitch(Service):
    service = 'Switch'

    @characteristic
    def display(self):
        return 'On'

    def run(self, sentinel):
        self.display.setter_callback = self.set_display

        while not sentinel.wait(1):
            state = get_display_state()
            if self.display.value != state:
                self.display.value = state
                self.display.notify()

    def set_display(self, state):
        if get_display_state() != state:
            set_display_state(state)
