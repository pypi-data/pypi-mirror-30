#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *


class ImageButton(Button):
    """A button with an image

    Options:
      - imgfile --- The image filepath (constructor only)
      - compound --- Image relative position
      - All :code:`Button` widget options (notably width and height)

    Forms of access:
      >>> from tkinter import *
      >>> from tkinter.ttk import *
      >>> btn = ImageButton(imgfile='myicon.gif', compound='top')
    
"""

    def __init__(self, master, imgfile, **kw):
        if 'compound' not in kw:
            kw['compound'] = 'top'
        self._image = PhotoImage(file=imgfile)
        kw['image'] = self._image
        Button.__init__(self, master, **kw)


if __name__ == '__main__':
    root = Tk()
    btn = ImageButton(root, 'tests/document-print.png', text='Allow Access', compound='top')
    btn.pack()
    root.mainloop()
