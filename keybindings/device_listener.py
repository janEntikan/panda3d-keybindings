from collections import OrderedDict

import toml

from panda3d.core import InputDevice
from panda3d.core import ButtonRegistry
from panda3d.core import Vec2
from panda3d.core import Vec3

from direct.showbase.DirectObject import DirectObject


axis_names = [axis.name for axis in InputDevice.Axis]


class Sensor:
    def __init__(self, config):
        self.name = config
        if self.name in axis_names:
            self.axis = True
        else:
            self.axis = False

    def get_config(self):
        return self.name

    def read(self, device):
        if not device is None:  # Not a keyboard
            if self.axis:
                axis = device.find_axis(InputDevice.Axis[self.name])
                return axis.value
            else:
                button = device.find_button(self.name)
                return button.pressed
        else:  # Keyboard
            button = ButtonRegistry.ptr().find_button(self.name)
            return base.mouseWatcherNode.is_button_down(button)


class Mapping:
    def __init__(self, config):
        sensor_configs = config.split(',')
        self.sensors = [Sensor(s_config) for s_config in sensor_configs]

    def get_config(self):
        s = ','.join(sensor.get_config() for sensor in self.sensors)
        return s

    def read(self, device):
        states = [sensor.read(device) for sensor in self.sensors]
        return states


class VirtualInput:
    def __init__(self, config):
        self.type = config['_type']
        self.device_order = config['_device_order']
        devices = [k for k in config.keys() if not k.startswith('_')]
        self.mappings = {
            device: Mapping(config[device])
            for device in devices
        }
        assert all(device in self.mappings for device in devices)

    def get_config(self):
        config = OrderedDict([
            ('_type', self.type),
            ('_device_order', self.device_order),
        ])
        config.update(OrderedDict([
            (name, mapping.get_config())
            for name, mapping in self.mappings.items()
        ]))
        return config

    def read_raw(self, devices):
        for candidate in self.device_order:
            if candidate in devices:
                device = devices[candidate]
                mapping = self.mappings[candidate]
                input_state = mapping.read(device)
                return input_state
            if candidate == 'keyboard':
                mapping = self.mappings[candidate]
                input_state = mapping.read(None)
                return input_state
        return None

    def read(self, devices):
        input_state = self.read_raw(devices)
        if input_state is not None:
            if self.type == 'button':
                if len(input_state) == 1 and isinstance(input_state[0], bool):
                    input_state = input_state[0]
                else:
                    raise Exception("Uninterpretable virtual state")
            elif self.type == 'axis':
                if len(input_state) == 1 and isinstance(input_state[0], float):
                    input_state = input_state[0]
                elif isinstance(input_state, list):
                    # [bool, bool] -> float
                    assert len(input_state) == 2
                    assert all(isinstance(e, bool) for e in input_state)
                    v = 0
                    if input_state[0]:
                        v -= 1
                    if input_state[1]:
                        v += 1
                    input_state = v
                else:
                    raise Exception("Uninterpretable virtual state")
            elif self.type == 'axis2d':
                if len(input_state) == 2:
                    input_state = Vec2(*input_state)
                elif len(input_state) == 4:
                    assert all(isinstance(e, bool) for e in input_state)
                    x, y = 0, 0
                    if input_state[0]:
                        x -= 1
                    if input_state[1]:
                        x += 1
                    if input_state[2]:
                        y -= 1
                    if input_state[3]:
                        y += 1
                    input_state = Vec2(x, y)
                else:
                    raise Exception("Uninterpretable virtual state")
            elif self.type == 'axis3d':
                if len(input_state) == 3:
                    input_state = Vec3(*input_state)
                elif len(input_state) == 6:
                    assert all(isinstance(e, bool) for e in input_state)
                    x, y,z = 0, 0, 0
                    if input_state[0]:
                        x -= 1
                    if input_state[1]:
                        x += 1
                    if input_state[2]:
                        y -= 1
                    if input_state[3]:
                        y += 1
                    if input_state[4]:
                        z -= 1
                    if input_state[5]:
                        z += 1
                    input_state = Vec3(x, y, z)
                else:
                    raise Exception("Uninterpretable virtual state")
            else:
                raise Exception("Uninterpretable virtual state")
        return input_state


class Context:
    def __init__(self, config):
        self.virtual_inputs = {
            input_name: VirtualInput(config[input_name])
            for input_name in config.keys()
        }

    def get_config(self):
        config = OrderedDict([
            (name, virtual_input.get_config())
            for name, virtual_input in self.virtual_inputs.items()
        ])
        return config

    def read(self, devices):
        result = {
            name: virtual_input.read(devices)
            for name, virtual_input in self.virtual_inputs.items()
        }
        return result


class LastConnectedAssigner:
    def __init__(self):
        self.device = None
        
    def connect(self, device):
        if self.device is None:
            self.device = device
            base.attach_input_device(device, prefix="")
            print("Assigned {}".format(device))

    def disconnect(self, device):
        if device == self.device:
            self.device = None
            base.detach_input_device(device)
            print("No assigned devices")

    def get_devices(self, user=None):
        if self.device is None:
            return [] # FIXME: keyboard
        else:
            full_id = self.device.device_class.name                
            return {full_id: self.device}


class SinglePlayerAssigner:
    def __init__(self):
        self.devices = {}
        for device in base.devices.get_devices():
            self.connect(device)
        
    def connect(self, device):
        dev_class = device.device_class.name
        if dev_class in self.devices:
            self.disconnect(self.devices[dev_class])
        base.attach_input_device(device, prefix="")
        self.devices[dev_class] = device

    def disconnect(self, device):
        dev_class = device.device_class.name
        print(dev_class, self.devices[dev_class])
        if device == self.devices[dev_class]:
            base.detach_input_device(device)
            del self.devices[dev_class]
        from pprint import pprint
        pprint(self.devices)

    def get_devices(self, user=None):
        return self.devices


class DeviceListener(DirectObject):
    def __init__(self, assigner, debug=False, config_file="keybindings.toml"):
        self.debug = debug
        self.read_config(config_file)

        self.assigner = assigner
        self.accept("connect-device", self.connect)
        self.accept("disconnect-device", self.disconnect)

    def connect(self, device):
        """Event handler that is called when a device is discovered."""

        if self.debug:
            print("{} found".format(device.device_class.name))
        self.assigner.connect(device)

    def disconnect(self, device):
        """Event handler that is called when a device is removed."""

        if self.debug:
            print("{} disconnected".format(device.device_class.name))
        self.assigner.disconnect(device)

    def read_config(self, config_file):
        with open(config_file, 'r') as f:
            config = toml.loads(f.read(), _dict=OrderedDict)
        self.contexts = {
            context_name: Context(config[context_name])
            for context_name in config.keys()
        }

    def get_config(self):
        config = OrderedDict([
            (name, context.get_config())
            for name, context in self.contexts.items()
        ])
        return config

    def read_context(self, context, user=None):
        assert context in self.contexts
        devices = self.assigner.get_devices(user=user)
        return self.contexts[context].read(devices)


def add_device_listener(assigner=None, debug=False):
    if assigner is None:
        assigner = LastConnectedAssigner()
    base.device_listener = DeviceListener(assigner, debug=debug)
