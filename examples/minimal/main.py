import sys

from direct.showbase.ShowBase import ShowBase

from keybindings.device_listener import add_device_listener
from keybindings.device_listener import SinglePlayerAssigner


class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Basics
        base.disable_mouse()

        # Escape for Quit
        base.accept('escape', sys.exit)

        # F10 for frame rate meter
        base.frame_rame_meter_visible = False
        base.set_frame_rate_meter(base.frame_rame_meter_visible)
        def toggle_frame_rate_meter():
            base.frame_rame_meter_visible = not base.frame_rame_meter_visible
            base.set_frame_rate_meter(base.frame_rame_meter_visible)
        base.accept('f10', toggle_frame_rate_meter)

        # F11 for debug
        def debug():
            import pdb; pdb.set_trace()
        base.accept('f11', debug)
        

if __name__ == '__main__':
    Application()
    add_device_listener(debug=True, assigner=SinglePlayerAssigner())
    from pprint import pprint
    pprint(base.device_listener.get_config())
    def print_context():
        pprint(base.device_listener.read_context('demo_context'))
    base.accept('p', print_context)
    base.run()


# base.attach_input_device(device, prefix="foo-")
# base.detach_input_device(device)

# from panda3d.core import ButtonRegistry
# button_handle = ButtonRegistry.ptr().find_button(button_name)
# button_handle.get_name() == 'none'

# InputDevice.Axis
# InputDevice.find_axis(InputDevice.Axis[axis_name])
