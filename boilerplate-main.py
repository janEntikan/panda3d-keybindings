import sys

from direct.showbase.ShowBase import ShowBase


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
    app = Application()
    app.run()
