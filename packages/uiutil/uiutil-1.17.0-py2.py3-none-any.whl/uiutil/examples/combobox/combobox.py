from uiutil import BaseFrame, standalone, Combobox, Position
from collections import OrderedDict


class MyFrame(BaseFrame):

    VALUES = ["First",
              "Second",
              "Third",
              "Fourth",
              "Fifth",
              "Sixth",
              "Seventh"]

    def __init__(self,
                 **kwargs):
        super(MyFrame, self).__init__(**kwargs)

        self.cb1 = Combobox(values=self.VALUES,
                            sort=False)

        self.cb2 = Combobox(values=self.VALUES,
                            sort=True,
                            row=Position.NEXT)

standalone(frame=MyFrame)
