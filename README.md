panda3d-keybindings
-------------------

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
  regard what devices should be checked. A player may prefer to cotrol
  character movement on a gamepad, but functions like invoking and
  working in menus with the keyboard.
* how imput is preprocessed. Badly manufactured sticks create noise near
  the center, and may require a dead zone. An axis' amplitude may need
  to be squared.
* devices connecting or disconnecting. From a game developer's
  perspective, these events should be dealt with under the hood.
* how devices are identified. A player may use two flight sticks for a
  space simulator. If they're of different makes, they can be identified
  "uniquely", and should be mappable independent of one another. Even
  with two identical sticks, there should be a way to check which is
  which ("Press trigger on left stick"), and label them accordingly.
* providing an interface to work with the mappings.

This project's state is pre-alpha. I've barely defined how things will
work. The rough shape is:

* A `context` is a set of `virtual input`s.
* A `virtual input` a button or axis (or other) with a semantic to the
  game.
* When a device is connected, it is assigned to a `player`, or kept
  unassigned for the time being. Players will only be able to read data
  from devices assigned to them.
* There's a TOML file that defines for each `player` and each `context`
  in what order to check devices for a `virtual input`. If the first
  enumerated device isn't assigned to the `player`, the next one will be
  checked, and so on, until one is found that can be read.
  * Each entry should contain filterable data like device type, device
    ID, etc.
* When a context's state is polled, the check outlined above happens,
  then the configured `mapping transformation` is applied, and the read
  state is added to the poll. At the end, the gathered results are
  returned.


TODO
----

* Everything
