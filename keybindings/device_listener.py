from collections import OrderedDict

from pathlib import Path

import toml

from panda3d.core import InputDevice
from panda3d.core import ButtonRegistry
from panda3d.core import Vec2
from panda3d.core import Vec3

from direct.showbase.DirectObject import DirectObject


axis_names = [axis.name for axis in InputDevice.Axis]


class Sensor:
    mouse_sensors = [
        "mouse_x",
        "mouse_y",
        "mouse_x_delta",
        "mouse_y_delta",
    ]
    delta_sensors = [
        "mouse_x_delta",
        "mouse_y_delta",
    ]

    def __init__(self, config):
        sensor, _, flags = config.partition(':')

        self.sensor = sensor
        if self.sensor in axis_names:
            self.axis = True
        else:
            self.axis = False
        self.mouse_pos = None
        self.mouse_delta = None

        if flags == '':
            flags = []
        else:
            flags = flags.split(':')
        self.flags = OrderedDict()
        for flag in flags:
            name, _, arg = flag.partition('=')
            assert name in ['flip', 'scale', 'button<', 'button>', 'exp']
            if name in ['scale', 'button<', 'button>', 'exp']:
                arg = float(arg)
            else:
                assert arg == ''
                arg = None
            self.flags[name] = arg
        
    def get_config(self):
        result = self.sensor
        for name, arg in self.flags.items():
            result += ":" + name
            if arg is not None:
                result+= "=" + str(arg)
        return result

    def read(self, device):
        if not device is None:  # Not a keyboard
            if self.axis:
                axis = device.find_axis(InputDevice.Axis[self.sensor])
                state = axis.value
            else:
                button = device.find_button(self.sensor)
                state = button.pressed
        else:  # Keyboard
            if self.sensor in self.mouse_sensors:
                if self.sensor in self.delta_sensors:
                    if self.mouse_delta is None:
                        state = None
                    else:
                        if self.sensor == "mouse_x_delta":
                            state = self.mouse_delta.x
                        else:
                            state = self.mouse_delta.y
                else:
                    if self.mouse_pos is None:
                        state = None
                    else:
                        if self.sensor == "mouse_x":
                            state = self.mouse_pos.x
                        else:
                            state = self.mouse_pos.y
            else:
                button = ButtonRegistry.ptr().find_button(self.sensor)
                state = base.mouseWatcherNode.is_button_down(button)

        for name, arg in self.flags.items():
            if name == 'flip':
                state *= -1
            elif name == 'scale':
                state *= arg
            elif name == 'button<':
                state = state <= arg
            elif name == 'button>':
                state = state >= arg
            elif name == 'exp':
                state = (abs(state) ** arg) * (state / abs(state))

        return state

    def push_events(self, device):
        if self.sensor in self.mouse_sensors:
            if base.mouseWatcherNode.has_mouse():
                mouse_pos = base.mouseWatcherNode.get_mouse()
                if self.mouse_pos is not None:
                    self.mouse_delta = mouse_pos - self.mouse_pos
                else:
                    self.mouse_delta = None
                self.mouse_pos = Vec2(mouse_pos)
            else:
                self.mouse_pos = None
                self.mouse_delta = None


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

    def push_events(self, device):
        for sensor in self.sensors:
            sensor.push_events(device)


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

        self.last_state = None
        self.triggered = None

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

    def get_device_and_mapping(self, devices):
        for candidate in self.device_order:
            if candidate in devices:
                device = devices[candidate]
                mapping = self.mappings[candidate]
                return (device, mapping)
            if candidate == 'keyboard':
                mapping = self.mappings[candidate]
                return (None, mapping)
        return None

    def read_raw(self, devices):
        thing = self.get_device_and_mapping(devices)
        if thing is not None:
            device, mapping = thing
            input_state = mapping.read(device)
            return input_state
        return None

    def read(self, devices):
        input_state = self.read_raw(devices)
        if input_state is not None:
            if all(s is None for s in input_state):
                input_state = None
            elif self.type == 'button':
                if len(input_state) == 1 and isinstance(input_state[0], bool):
                    input_state = input_state[0]
                else:
                    raise Exception("Uninterpretable virtual state")
            elif self.type == 'trigger':
                input_state = self.triggered
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

    def push_events(self, devices):
        thing = self.get_device_and_mapping(devices)
        if thing is not None:
            device, mapping = thing
            mapping.push_events(device)

        input_state = self.read_raw(devices)
        if self.type == 'trigger':
            if input_state is not None:
                input_state = input_state[0]
                if input_state and not self.last_state:
                    self.triggered = True  # Trigger has been pressed
                elif input_state and self.last_state:
                    self.triggered = False  # Trigger held pressed
                elif not input_state:
                    self.triggered = False  # Trigger released or idle
        self.last_state = input_state


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

    def push_events(self, devices):
        for _name, virtual_input in self.virtual_inputs.items():
            virtual_input.push_events(devices)
        

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

    def get_users(self):
        return [None]


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

    def get_users(self):
        return [None]


class DeviceListener(DirectObject):
    """
    Receives connection / disconnection events and informs the assigner

    :assigner:
        FIXME
    :debug:
        FIXME
    :config_module:
        If provided, the Listener will try to read the config file from that module.
    :config_file:
        The name of the config file in which the keybindings reside, by default keybindings.toml
    :task:
        Creates a task on creation (at sort -10) that calls push_device_events... FIme: ...which does what?
    :task_args:
        FIXME: Apparently these do not even make sense, as they are not expected?
    """
    def __init__(self, assigner, debug=False, config_module=None, config_file="keybindings.toml", task=True, task_args=None):
        self.debug = debug
        self.read_config(config_module, config_file)

        self.assigner = assigner
        self.accept("connect-device", self.connect)
        self.accept("disconnect-device", self.disconnect)

        if task:
            if task_args is None:
                task_args = dict(sort=-10)
            base.task_mgr.add(self.push_device_events, "device_listener", **task_args)

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

    def read_config(self, config_module, config_file_name):
        if config_module is None:
            # FIXME: This is old code that worked directly on paths. It
            # should probably be ripped out.
            main_dir = Path(base.main_dir)
            config_file = Path(config_file_name)
            with open(main_dir / config_file, 'r') as f:
                config = toml.loads(f.read(), _dict=OrderedDict)
        else:
            config = toml.loads(
                importlib.resources.read_text(
                    config_module,
                    config_file_name,
                ),
                _dict=OrderedDict,
            )
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
        devices = self.assigner.get_devices(user)
        return self.contexts[context].read(devices)

    def push_device_events(self, task):
        users = self.assigner.get_users()
        contexts = self.contexts.keys()
        for user in users:
            devices = self.assigner.get_devices(user)
            for context in contexts:
                self.contexts[context].push_events(devices)
        return task.cont


def add_device_listener(assigner=None, debug=False, config_module=None, config_file="keybindings.toml"):
    if assigner is None:
        assigner = LastConnectedAssigner()
    base.device_listener = DeviceListener(
        assigner,
        debug=debug,
        config_module=None,
        config_file=config_file,
    )
