# This file is a mock-up for the device listener's new data structure.


config = {
    'demo_context': {                               # Context.
        'simple_button': (                          # Virtual Input within the context.
            'button', [                             # Input type; Button is True as long as it is pressed, False otherwise.
                ('gamepad',                         # First candidate. Candidates are (device, sensor).
                 (                                  # Sensors consist of one to three axes.
                     [                              # An axis is a list.
                         'face_a'                   # The first element names the controller input to choose
                     ],                             # Further elements are filters, explained below.
                 ),                                 # Don't forget to close the axis tuple...
                 ),                                 # ...and then the sensor tuple.
                ('flight_stick', (['trigger'], )),  # Second candidate
                ('keyboard', (['q'], )),            # Third candidate
            ],
        ),
        'axis_to_button': (
            'button', [                             # Filters are ('name', argument) tuples, with None as argument for filters that don't take args.
                ('gamepad', (['left_x', ('button>', 0.75)], )),
            ],
        ),
        'trigger': (
            'trigger', [                            # Triggers are buttons that fire only in the frame that they are pressed
                ('keyboard', (['q'], )),
            ],
        ),
        'repeater': (
            'repeater:0.5,0.2', [                   # Repeaters are triggers that fire again after an initial / repeating cooldown.
                ('keyboard', (['q'], )),
            ],
        ),
        'yxcvb': (
            'button', [
                ('keyboard', (['y'], )),            # Yes, you can use a device multiple times.
                ('keyboard', (['x'], )),
                ('keyboard', (['c'], )),
                ('keyboard', (['v'], )),
                ('keyboard', (['b'], )),
        ]),
        'demo_axis_full': (
            'axis', [                               # Axes have values from -1 to 1
                ('gamepad', (['left_x'], )),
                ('flight_stick', (['roll'], )),
                ('keyboard', (['a/d'], )),          # An axis input can consist of two input buttons.
            ],
        ),
        'demo_axis_2d': (
            'axis2d', [                             # Two axes
                ('gamepad', (
                    ['left_x', ('exp', 2.0)],
                    ['left_y', ('exp', 0.5)],       # Second axis? Second sensor axis!
                ),
                 ),
                ('keyboard', (
                    ['a/d'],
                    ['s/w'],
                ),
                 ),
            ],
        ),
        'demo_axis_3d': (
            'axis3d', [                             # Three axes
                ('spatial_mouse', (['x'], ['y'], ['z'])),
                ('keyboard', (['a/d'], ['s/w'], ['q/e'])),
            ],
        ),
    },
}
