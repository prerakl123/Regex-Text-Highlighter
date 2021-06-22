from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import re
import inspect
import os

font = ('Consolas', 11)
label_frame_config = {
    'bg': '#000033',
    'fg': '#d6d6d6'
}
frame_config = {
    'bg': '#000033'
}
canvas_config = {
    'highlightthickness': 0,
    'bg': '#000033'
}
text_config = {
    'bg': '#040052',
    'fg': '#a8a8a8',
    'insertbackground': 'white',
    'insertwidth': 1,
    'selectbackground': '#264180',
    'selectforeground': 'white'
}
button_config = {
    'bg': '#040050',
    'fg': '#ffffff'
}


class ScrollableFrame(LabelFrame):
    def __init__(self, master, **kw):
        LabelFrame.__init__(self, master, **kw)
        self.canvas = Canvas(self, **canvas_config)
        v_scroll = Scrollbar(self, orient=VERTICAL)
        h_scroll = Scrollbar(self, orient=HORIZONTAL)

        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        self.canvas.pack(side=LEFT, expand=YES, fill=BOTH)

        self.widget_frame = Frame(self.canvas, **frame_config)
        self.canvas.create_window(0, 0, window=self.widget_frame, anchor=NW)

        self.bind('<Configure>', self.on_interior_config)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

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

    def on_enter(self, event=None):
        self.master.bind('<MouseWheel>', self.on_mouse_wheel)

    def on_leave(self, event=None):
        self.master.unbind('<MouseWheel>')


class RegexFrame(Frame):
    def __init__(self, master, updatefunc, regex='', description='', value='', **kw):
        Frame.__init__(self, master, **kw)
        self.config(highlightthickness=1, highlightbackground='black', **frame_config)

        self.value_entry = Text(self, font=font, height=4, width=20, **text_config)
        self.regex_entry = Text(self, font=font, height=4, width=20, **text_config)
        self.description_entry = ScrolledText(self, font=font, wrap=WORD, height=4, width=20, **text_config)

        self.value_entry.pack(side=LEFT, expand=True, fill=BOTH, padx=1, pady=1)
        self.regex_entry.pack(side=LEFT, expand=True, fill=BOTH, padx=1, pady=1)
        self.description_entry.pack(side=LEFT, expand=True, fill=BOTH, padx=1, pady=1)

        self.value_entry.insert(1.0, value)
        self.regex_entry.insert(1.0, regex)
        self.description_entry.insert(1.0, description)

        # self.value_entry.bind('<FocusOut>', updatefunc)
        # self.description_entry.bind('<FocusOut>', updatefunc)
        # self.regex_entry.bind('<FocusOut>', updatefunc)
        self.bind('<FocusOut>', updatefunc)


class RegexTextArea(ScrolledText):
    TAB_LENGTH = 4

    def __init__(self, master, **kw):
        ScrolledText.__init__(self, master, **kw)

        self.custom_tags = ['active_line', 'similar_selection']

        self.bind('<KeyPress-BackSpace>', self.on_bkspace)
        self.bind('<KeyPress-braceleft>', lambda a: self.autocomplete(val='{'))
        self.bind('<KeyPress-braceright>', lambda a: self.autocomplete(val='}'))
        self.bind('<KeyPress-bracketleft>', lambda a: self.autocomplete(val='['))
        self.bind('<KeyPress-bracketright>', lambda a: self.autocomplete(val=']'))
        self.bind('<KeyPress-colon>', lambda a: self.autocomplete(val=':'))
        self.bind('<KeyPress-less>', lambda a: self.autocomplete(val='<'))
        self.bind('<KeyPress-greater>', lambda a: self.autocomplete(val='>'))
        self.bind('<KeyPress-parenleft>', lambda a: self.autocomplete(val='('))
        self.bind('<KeyPress-parenright>', lambda a: self.autocomplete(val=')'))
        self.bind('<KeyPress-quoteright>', lambda a: self.autocomplete(val="'"))
        self.bind('<KeyPress-quotedbl>', lambda a: self.autocomplete(val='"'))
        self.bind('<Return>', self.on_return)

        self.highlight_current_line()

    def _any(self, name, alternates):
        """Return a named group pattern matching list of alternates."""
        return "(?P<%s>" % name + "|".join(alternates) + ")"

    def autocomplete(self, val):
        if val == '(':
            self.insert(INSERT, ')')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == '{':
            self.insert(INSERT, '}')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == '[':
            self.insert(INSERT, ']')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        # elif val == '<':
        # self.insert(INSERT, '>')
        # self.mark_set(INSERT,
        # f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == ')':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ')':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return ')'
            return 'break'

        elif val == '}':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '}':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return '}'
            return 'break'

        elif val == ']':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ']':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return ']'
            return 'break'

        # elif val == '>':
        # if self.get(self.index(INSERT),
        # f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '>':
        # self.mark_set(INSERT,
        # f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")

        # else:
        # return '>'

        # return 'break'

        elif val == '"':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '"':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'

            elif self.get(self.index(INSERT + ' -2c'), self.index(INSERT)) == '""':
                self.insert(INSERT, '""""')
                self.mark_set(INSERT, self.index(INSERT + ' -3c'))
                return 'break'

            else:
                if self.get(f"{int(self.index(INSERT).split('.')[0])}."
                            f"{int(self.index(INSERT).split('.')[1]) - 1}",
                            self.index(INSERT)) in ['', ' ', '(', '[', '{', '=', ',', 'B', 'br', 'Br', 'bR', 'BR',
                                                    'rb', 'rB', 'Rb', 'RB', 'r', 'u', 'R', 'U', 'f', 'F', 'fr',
                                                    'Fr', 'fR', 'FR', 'rf', 'rF', 'Rf', 'RF']:
                    self.insert(INSERT, '"')
                    self.mark_set(
                        INSERT, f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == "'":
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == "'":
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'

            elif self.get(self.index(INSERT + ' -2c'), self.index(INSERT)) == "''":
                self.insert(INSERT, "''''")
                self.mark_set(INSERT, self.index(INSERT + ' -3c'))
                return 'break'

            else:
                if self.get(f"{int(self.index(INSERT).split('.')[0])}."
                            f"{int(self.index(INSERT).split('.')[1]) - 1}",
                            self.index(INSERT)) in ['', ' ', '(', '[', '{', '=', ',', 'B', 'br', 'Br', 'bR', 'BR',
                                                    'rb', 'rB', 'Rb', 'RB', 'r', 'u', 'R', 'U', 'f', 'F', 'fr',
                                                    'Fr', 'fR', 'FR', 'rf', 'rF', 'Rf', 'RF']:
                    self.insert(INSERT, "'")
                    self.mark_set(
                        INSERT, f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == ':':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ":":
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'
        return

    def find_indent(self, string, value=4) -> dict:
        """returns indent level and spaces for single line `string` value"""
        indent_spaces = 0
        for i in string:
            if i.isspace():
                indent_spaces += 1
            elif not i.isspace():
                break
        return {'spaces': indent_spaces, 'level': indent_spaces // value}

    def on_bkspace(self, event):
        """:params event: parameter for backspace event list"""
        if self.tag_ranges(SEL) != ():
            return
        cur_ind = str(self.index(INSERT))
        one_less_char = self.get(f"{cur_ind} -1c", cur_ind)
        one_more_char = self.get(cur_ind, f"{cur_ind} +1c")
        three_less_char = self.get(f"{cur_ind} -3c", cur_ind)
        three_more_char = self.get(cur_ind, f"{cur_ind} +3c")

        one_less_char_ind = self.index(f"{cur_ind} -1c")
        one_more_char_ind = self.index(f"{cur_ind} +1c")
        three_less_char_ind = self.index(f"{cur_ind} -3c")
        three_more_char_ind = self.index(f"{cur_ind} +3c")
        open_bracs, close_bracs = ['{', '[', '('], ['}', ']', ')']

        if three_less_char in ['"""', "'''"]:
            if three_more_char == three_less_char:
                self.delete(three_less_char_ind, three_more_char_ind)
        elif one_less_char in ['"', "'"]:
            if one_more_char == one_less_char:
                self.delete(cur_ind, one_more_char_ind)
        elif one_less_char in open_bracs:
            if one_more_char == close_bracs[open_bracs.index(one_less_char)]:
                self.delete(cur_ind, one_more_char_ind)

        if one_less_char.isspace():
            target_ind = f"{cur_ind} -4c"
            del_chars = 0
            for i in self.get(target_ind, cur_ind):
                if i.isspace():
                    del_chars += 1
                elif i.isalnum():
                    del_chars -= 1
            if del_chars <= 0:
                del_chars = 1
            self.delete(f"{cur_ind} -{del_chars}c", self.index(INSERT))
            return 'break'
        else:
            return

    def on_return(self, event=None):
        prev_line = self.get(INSERT + ' linestart', INSERT)
        prev_indent = int(self.find_indent(prev_line, value=self.TAB_LENGTH)['spaces'])
        # print('"' + prev_line + '"\n', prev_indent)

        if prev_line.rstrip('\t').rstrip(' ').endswith(':') and not prev_line.rstrip('\t').rstrip(' ').startswith('#'):
            self.insert(INSERT, '\n')
            self.insert(INSERT + ' linestart',
                        ' ' * (prev_indent + self.TAB_LENGTH))
            self.see(INSERT)
            return 'break'

        elif len(prev_line) > 0 and prev_line[-1] in ['(', '[', '{']:

            if self.get(INSERT, INSERT + ' +1c') in [')', ']', '}']:
                self.insert(INSERT, '\n')
                self.insert(INSERT, ' ' * (prev_indent + self.TAB_LENGTH))
                self.insert(INSERT, '\n')
                self.insert(INSERT, ' ' * prev_indent)
                self.mark_set(INSERT, f"{int(self.index(INSERT).split('.')[0]) - 1}.0 lineend")
            else:
                self.insert(INSERT, '\n')
                self.insert(f"{int(self.index(INSERT).split('.')[0])}.0",
                            ' ' * (prev_indent + self.TAB_LENGTH))
                if self.get(self.index('insert lineend-1c'), self.index('insert lineend')) in [')', '}', ']']:
                    self.insert(self.index('insert lineend-1c'), '\n')
                    self.insert(self.index('insert lineend+1c'), ' ' * prev_indent)
            self.see(INSERT)
            return 'break'

        elif len(prev_line) > 0 and prev_line.rstrip().rstrip('\t') != '':
            if prev_line.rstrip()[-1] in [',', '\\']:
                ind = prev_line.rfind('(')
                if ind < 0:
                    ind = prev_line.rfind('[')
                    if ind < 0:
                        ind = prev_line.rfind('{')
                if ind > 0:
                    self.insert(INSERT, '\n')
                    space_strip_text = self.get(INSERT, 'insert lineend')
                    self.delete(INSERT, 'insert lineend')
                    self.insert(INSERT, ' ' * (ind + 1) + space_strip_text.lstrip())
                    self.mark_set(INSERT, f'insert linestart+{ind + 1}c')
                else:
                    self.insert(INSERT, '\n')
                    space_strip_text = self.get(INSERT, 'insert lineend')
                    self.delete(INSERT, 'insert lineend')
                    self.insert(INSERT, ' ' * prev_indent + space_strip_text.lstrip())
                    self.mark_set(INSERT, f'insert linestart+{prev_indent}c')
                self.see(INSERT)
            else:
                self.insert(INSERT, '\n')
                self.insert(f"{int(self.index(INSERT).split('.')[0])}.0", ' ' * (prev_indent))
                self.see(INSERT)
            return 'break'

        elif 'return' in prev_line or 'pass' in prev_line or 'continue' in prev_line or \
                'yield' in prev_line or 'break' in prev_line:
            self.insert(INSERT, '\n')
            self.insert(f"{int(self.index(INSERT).split('.')[0])}.0",
                        ' ' * (prev_indent - self.TAB_LENGTH))
            self.see(INSERT)
            return 'break'

        # elif self.check_paren(prev_line) is True:
        #     self.insert(INSERT, '\n')
        #     self.insert(f"{int(self.index(INSERT).split('.')[0])}.0", ' '*(prev_indent))
        #     self.see(INSERT)
        #     return 'break'

        else:
            self.insert(INSERT, '\n')
            self.insert(f"{int(self.index(INSERT).split('.')[0])}.0", ' ' * (prev_indent))
            self.see(INSERT)
            return 'break'

    def toggle_highlight(self, event=None):
        select = self.tag_ranges(SEL)
        if len(select) > 0:
            self.highlight_current_line(False)
            return
        self.highlight_current_line(True)

    def highlight_current_line(self, event=None):
        if event is True:
            self.tag_remove('active_line', '1.0', END)
            self.tag_add('active_line', 'insert linestart', 'insert lineend+1c')
            self.tag_config(
                'active_line', background='#1d1d5e')
            self.after(25, self.toggle_highlight)
        else:
            self.tag_remove('active_line', 1.0, END)
            self.after(25, self.toggle_highlight)

    def refresh(self, value_list, regex_list):
        pass

    def set_values(self, *values):
        pass


class Window(Tk):
    VALUE_LIST = []
    REGEX_LIST = []
    FRAME_LIST = []

    def __init__(self):
        Tk.__init__(self)
        self.title('RegexSyntaxHighlighter')
        self.protocol('WM_DELETE_WINDOW', self._save_on_close)

        # ------------------------- WIDGETS ------------------------- #
        self.buttons_frame = Frame(self, **frame_config)
        self.frame = ScrollableFrame(self, text='Values, Regexes and Descriptions', **label_frame_config)
        self.widget_frame = self.frame.widget_frame
        self.text_area_frame = LabelFrame(self, text='Text Area', **label_frame_config)

        self.refresh_btn = Button(self.buttons_frame, text='Refresh', font=font, command=self._refresh, relief=GROOVE,
                                  **button_config)
        self.add_btn = Button(self.buttons_frame, text='Add new field', font=font, command=self.add_new_regex_frame,
                              relief=GROOVE, **button_config)
        self.open_file_btn = Button(self.buttons_frame, text='Open File', font=font, command=self._open_file,
                                    relief=GROOVE, **button_config)
        self.text_area = RegexTextArea(self.text_area_frame, font=font, wrap=NONE, **text_config)

        # --------------------- PACKING WIDGETS --------------------- #
        self.buttons_frame.pack(side=TOP, anchor=W, fill=X, padx=2, pady=2)
        self.frame.pack(side=LEFT, fill=BOTH, expand=True, padx=3)
        self.text_area_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        self.refresh_btn.pack(side=LEFT, padx=1, pady=1)
        self.add_btn.pack(side=LEFT, padx=1, pady=1)
        self.open_file_btn.pack(side=LEFT, padx=1, pady=1)
        self.text_area.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=1)

        # ------------------------ BINDINGS ------------------------ #
        self.refresh_btn.bind('<Enter>', lambda _=None: [
            self.refresh_btn.config(cursor='hand2', fg='#ffff66', bg='#2f0040')
        ])
        self.refresh_btn.bind('<Leave>', lambda _=None: [
            self.refresh_btn.config(cursor=None, fg='#ffffff', bg='#040050')
        ])
        self.add_btn.bind('<Enter>', lambda _=None: [
            self.add_btn.config(cursor='hand2', fg='#ffff66', bg='#2f0040')
        ])
        self.add_btn.bind('<Leave>', lambda _=None: [
            self.add_btn.config(cursor=None, fg='#ffffff', bg='#040050')
        ])
        self.open_file_btn.bind('<Enter>', lambda _=None: [
            self.open_file_btn.config(cursor='hand2', fg='#ffff66', bg='#2f0040')
        ])
        self.open_file_btn.bind('<Leave>', lambda _=None: [
            self.open_file_btn.config(cursor=None, fg='#ffffff', bg='#040050')
        ])

        with open('TEXT-History', 'r') as text_file:
            self.text_area.insert(1.0, text_file.read().rstrip())

    def add_new_regex_frame(self, event=None, regex='', description='', value=''):
        rf = RegexFrame(self.widget_frame, self._update, regex, description, value)
        rf.pack(side=TOP, fill=X, expand=True, pady=1)
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

    def _open_file(self):
        file = filedialog.askopenfile(initialdir=os.path.dirname(os.path.abspath(inspect.getsourcefile(self.__class__))
                                                                 ).replace('/', '\\').rstrip('\\'))
        self.text_area.delete(1.0, END)
        self.text_area.insert(1.0, file.read().rstrip())

    def _refresh(self, event=None):
        self._update()
        self.widget_frame.update_idletasks()
        self.frame.update_idletasks()
        self.buttons_frame.update_idletasks()
        self.update_idletasks()
        self.frame.refresh()
        self.text_area.refresh(value_list=self.VALUE_LIST, regex_list=self.REGEX_LIST)

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
        with open('REGEX-History', 'w') as regex_file, open('TEXT-History', 'w') as text_file:
            regex_file.write(file + '\n')
            text_file.write(self.text_area.get(1.0, END) + '\n')
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
