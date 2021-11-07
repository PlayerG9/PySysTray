# PySysTray
add custom systray-icons to your project (**modified version if [moses-palmer/pystray](https://github.com/moses-palmer/pystray)**)

To make it clear: **this package is a modified version of [moses-palmer/pystray](https://github.com/moses-palmer/pystray)**.
it is intended to be more plexible and for gui-packages.
you need to create menus etc. on your own

<pre>
(☞ﾟヮﾟ)☞        I NEED YOUR HELP        ☜(ﾟヮﾟ☜)  
Please help me by implementing the other platforms
</pre>

# Supported platforms [^1]

| Platform     | Supported | Tested |
| ------------ | --------- | ------ |
| Windows      | ✓         | ✓     |
| Linux/Xorg   | ✕         | ✕     |
| Linux/GNOME  | ✕         | ✕     |
| Linux/Ubuntu | ✕         | ✕     |
| macOS        | ✕         | ✕     |

[^1]: I need tester. please report bugs etc. under your platform  


# Example usage
```python
import pysystray
from PIL import Image


def left_click():
    print("Left Click")


def right_click():
    print("Right Click")


icon = pysystray.Icon(
    name="<custom-app-name>",  # "unique" name of your app
    icon=Image.open('./Python.png'),  # the icon that should be used
    title="Your-App",  # title that should be displayed on mouse-hovering
    left_click=left_click,  # event that is called on left-click
                            # for example: focus on window
    right_click=right_click  # event that is called on right-click
                             # for example: open menu
)

icon.run()
```

# Advaned example (with tkinter)
```python
import tkinter as tk
from tkinter.constants import *

import pysystray

from PIL import Image


def left_click():
    root.deiconify()  # show window
    root.focus_set()  # set focus to app


def right_click():
    menu = tk.Toplevel(root)  # create custom window for settings or so
    menu.overrideredirect(1)  # remove border of window
    menu.geometry('50x50-0-50')  # bottom right corner
    menu.bind('<FocusOut>', lambda e: menu.destroy())

    tk.Button(menu, text="Quit", command=stop).place(relwidth=1.0, relheight=1.0)

    menu.focus_force()  # set window-focus to window


def stop():
    root.destroy()  # optional
    root.quit()  # stop tkinter-loop
    icon.stop()  # remove icon


root = tk.Tk()

tk.Label(root, text="My App").pack()

root.wm_protocol('WM_DELETE_WINDOW', root.withdraw)  # hide window on close-button

icon = pysystray.Icon(
    name="<custom-app-name>",
    icon=Image.open('./Python.png'),
    title="Your-App",
    left_click=left_click,
    right_click=right_click
)

icon.run_detached()
```
