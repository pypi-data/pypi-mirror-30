from uiutil import BaseFrame, standalone, RadioBox, Label, Position


class MyFrame(BaseFrame):
    def __init__(self,
                 **kwargs):
        super(MyFrame, self).__init__(**kwargs)

        self.radio = RadioBox(title="Pick One",
                              options={"First":  type,
                                       "Second": 2,
                                       "Third":  "Third"},
                              command=self.set_label)

        self.label = Label(row=Position.NEXT,
                           value="")
        self.set_label()

    def set_label(self):
        self.label.value = "{value} selected".format(value=self.radio.value)


standalone(frame=MyFrame,
           title="Welcome to UI Util app")
