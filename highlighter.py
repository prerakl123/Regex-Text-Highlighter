from tkinter import *
from tkinter.scrolledtext import ScrolledText

font = ('Consolas', 11)


class ScrollableFrame(LabelFrame):
    def __init__(self, master, **kw):
        LabelFrame.__init__(self, master, **kw)
        self.canvas = Canvas(self, highlightthickness=0)
        v_scroll = Scrollbar(self, orient=VERTICAL)
        h_scroll = Scrollbar(self, orient=HORIZONTAL)

        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        self.canvas.pack(side=LEFT, expand=YES, fill=BOTH)

        self.widget_frame = Frame(self.canvas, highlightthickness=0)
        self.canvas.create_window(0, 0, window=self.widget_frame, anchor=NW)

        self.bind('<Configure>', self.on_interior_config)
        self.bind_all('<MouseWheel>', self.on_mouse_wheel)

    @staticmethod
    def pack_multiple_widgets(*widgets, **kwargs):
        if len(kwargs.items()) < 1:
            for i in widgets:
                i.pack()
        else:
            for i in widgets:
                i.pack(**kwargs)

    def on_interior_config(self, event=None):
        self.update_idletasks()
        width, height = self.widget_frame.winfo_reqwidth(), self.widget_frame.winfo_reqheight()
        self.canvas.config(scrollregion=(0, 0, width, height))

    refresh = on_interior_config

    def on_mouse_wheel(self, event=None):
        shift_scroll = (event.state & 0x1) != 0
        scroll = -1 if event.delta > 0 else 1
        if shift_scroll:
            self.canvas.xview_scroll(scroll, 'units')
        else:
            self.canvas.yview_scroll(scroll, 'units')


class RegexFrame(Frame):
    def __init__(self, master, updatefunc, regex='', description='', value='', **kw):
        Frame.__init__(self, master, **kw)
        self.config(highlightthickness=1, highlightbackground='black')

        self.value_entry = Text(self, font=font, height=4, width=20)
        self.regex_entry = Text(self, font=font, height=4, width=20)
        self.description_entry = ScrolledText(self, font=font, wrap=WORD, height=4, width=20)

        self.value_entry.pack(side=LEFT, expand=True, fill=BOTH)
        self.regex_entry.pack(side=LEFT, expand=True, fill=BOTH)
        self.description_entry.pack(side=LEFT, expand=True, fill=BOTH)

        self.value_entry.insert(1.0, value)
        self.regex_entry.insert(1.0, regex)
        self.description_entry.insert(1.0, description)

        # self.value_entry.bind('<FocusOut>', updatefunc)
        # self.description_entry.bind('<FocusOut>', updatefunc)
        # self.regex_entry.bind('<FocusOut>', updatefunc)
        self.bind('<FocusOut>', updatefunc)


class Window(Tk):
    VALUE_LIST = []
    REGEX_LIST = []
    FRAME_LIST = []

    def __init__(self):
        Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self._save_on_close)

        self.buttons_frame = Frame(self)
        self.refresh_btn = Button(self.buttons_frame, text='Refresh', font=font, command=self._refresh, relief=GROOVE)
        self.add_btn = Button(self.buttons_frame, text='Add new field', font=font, command=self.add_new_regex_frame,
                              relief=GROOVE)

        self.buttons_frame.pack(side=TOP)
        self.refresh_btn.pack(side=LEFT)
        self.add_btn.pack(side=LEFT)

        self.frame = ScrollableFrame(self, text='Values, Regexes and Descriptions')
        self.widget_frame = self.frame.widget_frame
        self.frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.text_area = ScrolledText(self, font=font)
        self.text_area.pack(side=RIGHT, fill=BOTH, expand=True)

    def add_new_regex_frame(self, event=None, regex='', description='', value=''):
        rf = RegexFrame(self.widget_frame, self._update, regex, description, value)
        rf.pack(side=TOP, fill=X, expand=True, pady=5)
        self.FRAME_LIST.append(rf)
        self.VALUE_LIST.append(value)
        self.REGEX_LIST.append(value)
        self.frame.refresh()

    def load_all_regex(self) -> list:
        with open('REGEX-History') as regex_read_file:
            regex_list = regex_read_file.readlines()

        for i in range(len(regex_list)):
            regex_list[i] = ''.join([j for j in reversed(regex_list[i][-2::-1])])
            regex_list[i] = regex_list[i].split('<===>')

        return regex_list

    def set_regex_values(self, *args):
        """
        args must be lists like ['<REGEX1>', 'DESCRIPTION1', 'VALUE1'], ['<REGEX2>', 'DESCRIPTION2', 'VALUE2'], etc
        """
        for reg, desc, val in args:
            self.add_new_regex_frame(None, reg, desc, val)

    def _refresh(self, event=None):
        self._update()
        self.widget_frame.update_idletasks()
        self.frame.update_idletasks()
        self.buttons_frame.update_idletasks()
        self.update_idletasks()
        self.frame.refresh()

    def _save_on_close(self):
        line_list = []
        for frame in self.FRAME_LIST:
            line_elements = [frame.regex_entry.get(1.0, END).rstrip('\n').rstrip(),
                             frame.description_entry.get(1.0, END).rstrip('\n').rstrip(),
                             frame.value_entry.get(1.0, END).rstrip('\n').rstrip()]
            if '' in line_elements:
                continue
            line = '<===>'.join(line_elements)
            line_list.append(line)
        file = '\n'.join(line_list)
        with open('REGEX-History', 'w') as regex_file:
            regex_file.write(file + '\n')
        exit()

    def _update(self, event=None):
        for frame, i in zip(self.FRAME_LIST, [_int for _int in range(len(self.FRAME_LIST))]):
            self.VALUE_LIST[i] = frame.value_entry.get(1.0, END)
            self.REGEX_LIST[i] = frame.regex_entry.get(1.0, END)


def main():
    win = Window()
    win.set_regex_values(*win.load_all_regex())
    win.mainloop()


if __name__ == '__main__':
    main()
