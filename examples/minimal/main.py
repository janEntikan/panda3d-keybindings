import sys

import toml

from panda3d.core import NodePath
from panda3d.core import TextNode
from panda3d.core import TextFont

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectLabel
from direct.gui.DirectGui import DirectFrame

from keybindings.device_listener import add_device_listener
from keybindings.device_listener import SinglePlayerAssigner

from metagui.gui import SizeSpec
from metagui.gui import WholeScreen
from metagui.gui import ScrollableFrame
from metagui.gui import HorizontalFrame
from metagui.gui import VerticalFrame
from metagui.gui import Element
from metagui.gui import spacer
from metagui.gui import spacer_factory
from metagui.gui import filler
from metagui.tools import intersperse


class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Basics
        base.disable_mouse()

        # Escape for Quit
        base.accept('escape', sys.exit)

        # F10 for frame rate meter
        base.frame_rate_meter_visible = False
        base.set_frame_rate_meter(base.frame_rate_meter_visible)
        def toggle_frame_rate_meter():
            base.frame_rate_meter_visible = not base.frame_rate_meter_visible
            base.set_frame_rate_meter(base.frame_rame_meter_visible)
        base.accept('f10', toggle_frame_rate_meter)

        # F11 for debug
        def debug():
            import pdb; pdb.set_trace()
        base.accept('f11', debug)


if __name__ == '__main__':
    from keybindings_config import config
    #from panda3d.core import load_prc_file_data
    #load_prc_file_data("", "text-pixels-per-unit 90")
    #load_prc_file_data("", "text-page-size 1024 1024")

    Application()
    add_device_listener(
        assigner=SinglePlayerAssigner(),
        config=config,
    )
    context = base.device_listener.read_context('demo_context')

    # Text representation
    for context_name, context in config.items():
        for virtual_input_name, (virtual_input_type, sensors) in context.items():
            print(f'> {context_name}.{virtual_input_name}:{virtual_input_type}')
            for device, axes in sensors:
                axes_strings = []
                for axis in axes:
                    axis_strings = [axis[0]]
                    for (flag, arg) in axis[1:]:
                        if arg is None:
                            axis_strings.append(flag)
                        else:
                            axis_strings.append('='.join([flag, str(arg)]))
                    axis_string = ':'.join(axis_strings)
                    axes_strings.append(axis_string)
                print("{}: {}".format(device, ','.join(axes_strings)))
            print()

    # GUI representation
    # Text styles
    font = base.loader.load_font('fonts/OpenSans-Regular.ttf')
    #font.setRenderMode(TextFont.RMSolid)
    #font.setPixelsPerUnit(90)
    #font.setPageSize(512, 512)
    text_title_style = dict(
        text_font=font,
        text_pos=(0.01, -0.015),
        text_scale=0.05,
        text_align=TextNode.ALeft,
    )
    text_centered_box_style = dict(
        text_font=font,
        text_pos=(0.0, -0.015),
        text_scale=0.05,
        text_align=TextNode.ACenter,
    )
    text_left_box_style = dict(
        text_font=font,
        text_pos=(0.015, -0.015),
        text_scale=0.05,
        text_align=TextNode.ALeft,
    )

    # Widget styles
    context_title_style = dict(
        text_font=font,
        text_pos=(0.02, -0.03),
        text_scale=0.1,
        text_align=TextNode.ACenter,
        text_fg=(0.1, 0.1, 0.1, 1),
        frameColor=(0.7, 0.7, 0.7, 1),
    )
    virtual_input_title_style = dict(
        text_fg=(0.9, 0.9, 0.9, 1),
        frameColor=(0.5, 0.5, 0.5, 1),
        **text_title_style,
    )
    device_style = dict(
        text_fg=(0.9, 0.9, 0.9, 1),
        frameColor=(0.3, 0.3, 0.3, 1),
        **text_left_box_style,
    )
    sensor_box_style = dict(
        text_fg=(1, 1, 1, 1),
        frameColor=(0, 0, 0, 1),
        **text_centered_box_style,
    )
    filter_box_style = dict(
        text_fg=(0.9, 0.9, 0.9, 1),
        frameColor=(0.15, 0.15, 0.15, 1),
        **text_centered_box_style,
    )

    debug_style = dict(
        #frameColor=(0.47, 0.19, 0.33, 1),
        frameColor=(0.9, 0.9, 0.9, 1),
        **text_centered_box_style,
    )

    input_visual_style = dict(
        frameColor=(1.0, 1.0, 1.0, 1),
        **text_centered_box_style,
    )

    # Widget sizes
    mini_spacer_width = dict(w_min=0.01, w_weight=0.0)
    spacer_width = dict(w_min=0.03, w_weight=0.0)
    double_spacer_width = dict(w_min=0.06, w_weight=0.0)
    maxi_spacer_width = dict(w_min=0.12, w_weight=0.0)

    text_line_height = dict(h_min=0.06, h_weight=0.0)
    mini_spacer_height = dict(h_min=0.01, h_weight=0.0)
    spacer_height = dict(h_min=0.03, h_weight=0.0)

    context_height = dict(h_min=0.12, h_weight=0.0)
    filter_width = dict(w_min=0.4, w_weight=0.0)
    device_width = dict(w_min=0.4, w_weight=0.0)
    input_visual_size = dict(w_min=0.3, w_weight=0.0, h_min=0.3, h_weight=0.0)

    # Widgets
    def filter_frame(filter_spec):
        name, arg = filter_spec
        if arg is None:
            filter_text = name
        else:
            filter_text = name + '=' + str(arg)
        return Element(
            DirectLabel,
            kwargs=dict(text=filter_text, **filter_box_style),
            size_spec=SizeSpec(**filter_width, **text_line_height),
        )

    def sensor_axis_frame(sensor_axis):
        sensor_input, *filters = sensor_axis
        return HorizontalFrame(
            # Sensor
            Element(
                DirectLabel,
                kwargs=dict(text=sensor_input, **sensor_box_style),
                size_spec=SizeSpec(**filter_width, **text_line_height),
            ),
            spacer(mini_spacer_width),
            # Filters
            *intersperse(
                [filter_frame(filter_spec) for filter_spec in filters],
                spacer_factory(mini_spacer_height),
            ),
            # Filler
            spacer(text_line_height),
        )

    def candidate_frame(candidate):
        """A device (keyboard, gamepad or other) and its configuration."""
        device, sensor_axes = candidate
        return HorizontalFrame(
            # Device
            Element(
                DirectLabel,
                kwargs=dict(text=device, **device_style),
                size_spec=SizeSpec(**device_width, **text_line_height),
            ),
            # Spacer
            spacer(maxi_spacer_width),
            # Sensor axes
            VerticalFrame(
                *intersperse(
                    [sensor_axis_frame(sensor_axis) for sensor_axis in sensor_axes],
                    spacer_factory(mini_spacer_height),
                ),
            ),
            weight=0.0,
        )

    def virtual_input_frame(virtual_input_name, virtual_input):
        virtual_input_type, candidates = virtual_input
        return VerticalFrame(
            # Virtual input name and type
            Element(
                DirectLabel,
                kwargs=dict(text=f"{virtual_input_name} ({virtual_input_type})", **virtual_input_title_style),
                size_spec=SizeSpec(**text_line_height),
            ),
            HorizontalFrame(
                # Left-side spacer for candidates
                spacer(double_spacer_width),
                # Candidates
                VerticalFrame(
                    spacer(spacer_height),
                    *intersperse(
                        [candidate_frame(candidate) for candidate in candidates],
                        spacer_factory(mini_spacer_height),
                        first=False, last=False,
                    ),
                    spacer(spacer_height),
                    filler(),
                    weight=0.0,
                ),
                filler(),
                # Visualizer
                VerticalFrame(
                    spacer(spacer_height),
                    Element(
                        DirectLabel,
                        kwargs=dict(text='', **input_visual_style),
                        size_spec=SizeSpec(**input_visual_size),
                    ),
                    spacer(spacer_height),
                    filler(),
                    weight=0.0,
                ),
                # Right-side spacer
                spacer(double_spacer_width),
            ),
        )

    def context_frame(context_name, context):
        return VerticalFrame(
            spacer(spacer_height),
            # Context name
            Element(
                DirectLabel,
                kwargs=dict(text=context_name, **context_title_style),
                size_spec=SizeSpec(**context_height),
            ),
            spacer(spacer_height),
            HorizontalFrame(
                # Left-hand spacer
                spacer(double_spacer_width),
                # Virtual inputs
                VerticalFrame(
                    *[virtual_input_frame(virtual_input_name, virtual_input)
                      for virtual_input_name, virtual_input in context.items()],
                ),
                # Spacer
                spacer(double_spacer_width),
            ),
        )

    gui = WholeScreen(
        ScrollableFrame(
            HorizontalFrame(
                spacer(double_spacer_width),
                VerticalFrame(
                    spacer(spacer_height),
                    *[context_frame(context_name, context)
                      for context_name, context in config.items()],
                    spacer(spacer_height),
                ),
                spacer(double_spacer_width),
            ),
        ),
    )
    gui.create()

    base.run()
