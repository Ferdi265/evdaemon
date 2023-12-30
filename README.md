# evdaemon

evdaemon is a rather simple event-based framework for python, initially designed
for my i3 and swaybar configs.

It uses the `os.select()` feature to read from file descriptors and wait for
timeouts in a non-blocking way.

Disclaimer: This is a really hacky project I built in 2017 and which I intend
to replace with an asyncio replacement.

## Installation

evdaemon has no dependencies, just install via `pip install --editable .`.

This installs `evdaemon`, `evdmodule_i3`, and `evdmodule_wm`.

## Simple Usage

Create a daemon with `evdaemon.Daemon()` and register modules that derive from
`evdaemon.Module` on it with `daemon.register(module)`.
Modules can be unregistered again with `daemon.unregister(module)`.

Run the event loop with `daemon.run()`.
Emit toplevel events with `daemon.emit(*args)` (takes an arbitrary event path
and arguments)

## Documentation

### evdaemon.Daemon

For using `evd` modules a daemon instance needs to be created on which modules
can be registered

- `Daemon()`: simple constructor
- `daemon.modules`: dictionary of registered modules
- `daemon.state`: global daemon state
- `daemon.register(module)`: register a module
- `daemon.unregister(module)`: unregister a module
- `daemon.emit(*path)`: emit an event to all modules
- `daemon.run()`: start the event loop. Continues until no timeouts and no
  registered files exist any more.

### evdaemon.Module

Each module in `evd` can emit and listen for events, register files to be read
from asynchronously, set timeouts or intervals, and set a state object that
other modules on the daemon can see and interact with.

- `Module()`: simple constructor
- `module.name`: the name of the module, must be set.
  also used as the name of the attribute in `module.global_state`
- `module.global_state`: a handle to the global state object of the daemon
- `module.state`: this module's state object (identical to
  `getattr(module.global_state, module.name)`)
- `module.register_daemon(daemon)`: called when the module is first registered
  to the daemon. Use this to load dependency daemon modules into the daemon.
  Always call `super().register_daemon(daemon)`.
- `module.unregister_daemon(daemon)`: called when the module is unregistered
  from the daemon. Always call `super().unregister_daemon(daemon)`.
- `module.register_file(file, *path)`: register a file to the daemon. `path` is
  the event path to emit when the file becomes readable. The event is emitted
  privately to this module.
- `module.unregister_file(file)`: unregister a file from the daemon.
- `module.files()`: get all registered files
- `module.trigger_file(file)`: manually trigger a file as if it were ready to be
  read. Used internally by `Daemon` to trigger file events.
- `module.timeouts()`: get all registered timeout listeners
- `module.timeout(secs, fn)`: call `fn` after `secs` seconds
- `module.listen(*path, fn)`: listen for events with `path` and call `fn` with
  the rest arguments.
- `module.listen_once(*path, fn)`: listen for one event with `path` and call `fn`
  with the rest arguments.
- `module.remove(*path)`: remove all listeners from this module that listen for
  `path`.
- `module.emit(*path)`: emit an event with `path` to all deamon modules.
- `module.emit_local(*path)`: emit an event with `path` to only this module.
- `module.listen_private(*path, fn)`: listen privately for one event with `path`
  and call `fn` with the rest arguments. (only for private events from this
  module)
- `module.listen_once_private(*path, fn)`: listen privately for one event with
  `path` and call `fn` with the rest arguments. (only for private events from
  this module)
- `module.remove_private(*path)`: remove all listeners from this module that
  listen privately for `path`.
- `module.emit_private(*path)`: emit an event with `path` to privately listenig
  listeners in this module.

### evdmodule_wm.wmModule

This module represents a window manager and its state. It provides a central
state object where other window manager modules can publish information on the
running window manager.

Not all information must be presented by window manager modules. Missing
information should be `None`.

Events with the prefix `wm` should be used to indicate parts of the state have
been updated. (e.g. "wm", "title" should mean `state.title` has been updated)

- `state.mode`: the current "mode" of the window manager
- `state.title`: the currently active window title
- `state.monitors`: a dictionary of monitor ids to monitors
- `state.workspaces`: a dict of workspace ids to workspaces

#### evdmodule_wm.Monitor

Represents a monitor connected to the system

- `Monitor(rect, name)`: construct a monitor
- `monitor.rect`: the rectangle on the screen filled by the monitor
- `monitor.name`: the name of the monitor
- `monitor.active`: indicates whether the monitor is active
- `monitor.primary`: indicates whether the monitor is the primary monitor
- `monitor.workspaces`: list of all workspaces that belong to this monitor.
  empty if workspaces aren't associated with monitors

#### evdmodule_wm.Workspace

Represents a workspace

- `Workspace(rect, name, num)`: construct a workspace
- `ws.rect`: the rectangle on the screen filled by this workspace
- `ws.name`: the name of this workspace
- `ws.num`: the number of this workspace
- `ws.visible`: indicates whether this workspace is visible
- `ws.focused`: indicates whether this workspace is focused
- `ws.urgent`: indicates whether there are urgent hints in this workspace
- `ws.monitor`: the monitor this workspace is currently on
- `ws.windows`: the list of windows in this workspace

#### evdmodule_wm.Window

Represents a window

- `Window(wid)`: construct a window
- `win.wid`: the Xorg window id

#### evdmodule_wm.Rect

Represents a rectangle on the screen

- `Rectangle(x, y, w, h)`: construct a rectangle
- `rect.x`: get x position
- `rect.y`: get y position
- `rect.width`: get width
- `rect.height`: get height

### evdmodule_i3.i3Module

A module for the i3 or sway window manager. Communicates using the i3 IPC
protocol.

- `i3Module(events = ["workspace", "output", "mode", "window", "shutdown"], ipc= None)`:
  construct an i3 module. `events` lists the i3 events to subscribe to, ipc is
  optionally an instance of `i3ipcModule`. An `i3ipcModule` will be created and
  registered if none is given.

This module emits `wm` events and adjusts `wm` state.

### evdmodule_i3.i3ipcModule

A module for interacting with the i3 IPC.

- `i3ipcModule()`: construct an i3 ipc module
- `ipc.send_cmd(cmd, payload)`: send a message (any from `evdmodule_i3.ipc.MSG`)
  with an optional payload. `payload` can be a string or an object that is
  serialized as JSON.

This module sends "i3ipc" events, with the second parameter as "reply" or
"event", the third parameter as the message type, and the last parameter as the
deserialized payload.

#### evdmodule_i3.ipc

Contains a dictionary MSG with all possible message types, REPLY with all
possible reply types, and EVENT with all possible event types.
