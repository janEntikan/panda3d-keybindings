panda3d-keybindings
===================

Panda3D comes with a nice API suite to work with input devices. In
particular, it has one for USB HIDs, and one for mouse and keyboard.
What it does not have is a mechanism to build an abstraction over these
devices, so that a developer can define them in terms of a set of
buttons and axes, and it is a matter of configuration how actual inputs
on devices are mapped to those abstract inputs. A game's logic should
not be concerned with details like...

* whether a 2D axis gets its values from a gamepad's stick or its four
  buttons, from WASD, or a dance pad.
* how the player wants the inputs from the devices combined. There may
  be a different list of priorities for different abstract inputs with
  regard what devices should be checked. A player may prefer to control
  character movement on a gamepad, but functions like invoking and
  working in menus with the keyboard.
* how input is preprocessed. Badly manufactured sticks create noise near
  the center, and may require a dead zone. An axis' amplitude may need
  to be scaled or squared.
* devices connecting or disconnecting. From a game developer's
  perspective, these events should be dealt with under the hood.
* how devices are identified. A player may use two flight sticks for a
  space simulator. If they're of different makes, they can be identified
  "uniquely", and should be mappable independent of one another. Even
  with two identical sticks, there should be a way to check which is
  which ("Press trigger on left stick"), and label them accordingly.
  NOTE: Not implemented yet.
* providing an interface to work with the mappings. NOTE: Completely
  inexistent so far.
* if the state, when polled at different times during a frame, is still
  the same; It just should be. This is quite an edge case, but may cause
  hard to reproduce bugs. NOTE: Currently only very partially
  implemented, but the difference between that and the current version
  is, after all, only relevant for that edge case.


Status
------

This project's state is alpha. The polling interface works quite well and is feature-rich.


Installation
------------

`pip install panda3d-keybindings`


Concepts
--------

* A `virtual input` a button or axis (or other) with a semantic to the
  game. It has
  * a type, which is one of
    * `button`: `True` if the button is pressed, `False` otherwise.
    * `trigger`: `True` for the frame in which the button is pressed.
    * `axis`: A `float`.
    * `axis2d`: `panda3d.core.Vec2`.
    * `axis3d`: `panda3d.core.Vec3`.
  * a device order, stating the highest priority to the lowest to check
    for presence and state when reading a context.
  * a sensor definition for each usable device. This defines the
    buttons / axes used, and specifies post-processing that is to be
    done on them.
* A `context` is a set of `virtual input`s that is read together. It is
  an organizational unit to make it easy for the application to activate
  or deactivate parts of the user input interface. For example, opening
  the game's ingame menu may activate the `menu` context, and deactivate
  the `character_movement` one.
* When a device is connected, it is assigned to a `player`, or kept
  unassigned for the time being. Players will only be able to read data
  from devices assigned to them.
  NOTE: Currently only single-player assigners exist off-the-shelf.
* There's a TOML file that defines for each `player` and each `context`
  in what order to check devices for a `virtual input`. If the first
  enumerated device isn't assigned to the `player`, the next one will be
  checked, and so on, until one is found that can be read.
  NOTE: Currently no concept of players exists in the config file.
  * Each entry should contain filterable data like device type, device
    ID, etc.
    NOTE: Utterly unimplemented.


Example
-------

Setting up an application for use with this module is easy:

    from direct.showbase.ShowBase import ShowBase
    from keybindings.device_listener import add_device_listener
    from keybindings.device_listener import SinglePlayerAssigner

    ShowBase()
    add_device_listener(
        config_file='keybindings.toml',
        assigner=SinglePlayerAssigner(),
    )

Now there is a `base.device_listener`.

A keybinding configuration could look like this:

    [demo_context]
    
      [demo_context.demo_button]
      _type = "button"
      _device_order = ["gamepad", "flight_stick", "keyboard"]
      gamepad = "face_a"
      flight_stick = "trigger"
      keyboard = "q"


When the context `demo_context` is read, ...

    base.device_listener.read_context('demo_context')

...the result may look like this:

    {'demo_button': False}

This means that due to the config snippet above, the device listener has
checked whether a gamepad is connected; If so, the state of `face_a` is used, if not, the `flight_stick` is tested next, and so on. In this example, a device has been found and the button has not been pressed.

If no device type is found to be connected, the returned state would be `None`. Do note that if a keyboard is listed as a possible option, it will be assumed to be present.


TODO
----

* Document sensor definitions
  'a', 'left_x,left_y', 'left_x:flip,left_y', 'mouse_pos_delta'
* Sphinx documentation
* Repeating buttons: A trigger that re-Trues every <time_span> as long as the button is pressed.
* Raw keys: `keyboard = "raw-z"`; Requires Panda3D API support.
* If an axis/button is not use, give lower-priority devices a chance to be using it.
* Deadzones and recalibration post-processing for jittery / uncentered devices.


* A GUI for re-use in games that use this package on top of all this config stuff, including device_tester's capabilities.
* Multi-user Assigner
* Throw events
* Freeze whole state each frame (currently only done for `mouse_*`)
  NOTE: Really? I thought I did that.
* Upgrade example
* Add subconsoles for panda3d-cefconsole
  * Configure keybindings
  * Reassign devices
* `setup.py`: Go over `packages=` again.