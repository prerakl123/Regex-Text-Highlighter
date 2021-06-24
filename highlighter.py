from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import font as tk_font
from tkinter import ttk
from tkinter import colorchooser
import re
import inspect
import os

font = ['Consolas', 11]
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
label_config = {
    'bg': '#040052',
    'fg': '#a8a8a8',
    'font': font
}
checkbtn_config = {
    'relief': GROOVE,
    'onvalue': 1,
    'offvalue': 0,
    'bg': '#040052',
    'fg': '#a8a8a8',
    'anchor': W
}
combo_config = {
    'selectbackground': '#264180',
    'selectforeground': 'white',
    # 'background': '#040052',
    'foreground': '#a8a8a8',
    'fieldbackground': '#040052',
    'insertcolor': 'white',
    'insertwidth': 1,
    'highlightthickness': 1,
    'highlightbackground': 'white',
}
entry_config = {
    'bg': '#040052',
    'fg': '#a8a8a8',
    'selectforeground': 'white',
    'selectbackground': '#264180',
    'insertwidth': 1,
    'insertbackground': 'white',
    'font': font
}


def center_window(win: Tk or Toplevel):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('+{}+{}'.format(x, y))
    win.deiconify()


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
    def __init__(self, master, updatefunc, regex='', description='', value='', config_args='', **kw):
        Frame.__init__(self, master, **kw)
        self.config(highlightthickness=1, highlightbackground='black', **frame_config)

        self.configuration_dict = dict()

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
        self.arg_configuration(config_args)
        print(self.configuration_dict)

    def arg_configuration(self, config_args=''):
        config_args = config_args.split('|')
        for expression in config_args:
            exp_list = expression.split('=')
            self.configuration_dict[exp_list[0]] = int(exp_list[1]) if exp_list[1].isnumeric() else str(exp_list[1])


class RegexEditingFrame(LabelFrame):
    def __init__(self, master, frame, description: bool, **kw):
        LabelFrame.__init__(self, master, **kw)
        self.text = ScrolledText(self, font=font, **text_config)

        if description:
            self.text.insert(1.0, frame.description_entry.get(1.0, END))
        else:
            self.text.insert(1.0, frame.regex_entry.get(1.0, END))

        self.text.pack(expand=True, fill=BOTH, padx=1, pady=1)


class RegexConfigEditingFrame(LabelFrame):
    def __init__(self, master, frame, configurations: dict, **kw):
        LabelFrame.__init__(self, master, **kw)

        self.bold_intvar = IntVar()
        self.italic_intvar = IntVar()
        self.underline_intvar = IntVar()
        self.overstrike_intvar = IntVar()

        combostyle = ttk.Style()

        combostyle.theme_create('combostyle', parent='alt', settings={'TCombobox': {'configure': combo_config}})
        combostyle.theme_use('combostyle')

        self.choose_font_combo = ttk.Combobox(self, text='Choose Font', font=font)
        self.choose_font_combo.option_add('*TCombobox*Listbox.background', '#040052')
        self.choose_font_combo.option_add('*TCombobox*Listbox.font', 'Consolas 9')
        self.choose_font_combo.option_add('*TCombobox*Listbox.foreground', '#a8a8a8')
        self.choose_font_combo.option_add('*TCombobox*Listbox.selectBackground', '#264180')
        self.choose_font_combo.option_add('*TCombobox*Listbox.selectForeground', 'white')
        self.font_size_lbl = Label(self, text='Font Size', **label_config, width=18)
        self.font_size_entry = Entry(self, width=4, **entry_config)
        self.bold_checkbtn = Checkbutton(self, text='Bold', font=font.__add__(['bold']), **checkbtn_config,
                                         variable=self.bold_intvar, width=15)
        self.italic_checkbtn = Checkbutton(self, text='Italic', font=font.__add__(['italic']), **checkbtn_config,
                                           variable=self.italic_intvar, width=15)
        self.underline_checkbtn = Checkbutton(self, text='Underline', font=font.__add__(['underline']),
                                              **checkbtn_config, variable=self.underline_intvar, width=15)
        self.overstrike_checkbtn = Checkbutton(self, text='Overstrike', variable=self.overstrike_intvar,
                                               **checkbtn_config, font=font.__add__(['overstrike']), width=15)
        self.fg_color_lbl = Label(self, text='Foreground Color: ', **label_config)
        self.fg_color = Label(self, text='    ', **label_config)
        self.fg_color.bind('<Enter>', lambda _=None: self.fg_color.config(cursor='hand2'))
        self.fg_color.bind('<Leave>', lambda _=None: self.fg_color.config(cursor=None))
        self.fg_color.bind('<ButtonRelease-1>', lambda _=None: self.show_color_palette(self.fg_color))
        self.bg_color_lbl = Label(self, text='Background Color: ', **label_config)
        self.bg_color = Label(self, text='    ', **label_config)
        self.bg_color.bind('<Enter>', lambda _=None: self.bg_color.config(cursor='hand2'))
        self.bg_color.bind('<Leave>', lambda _=None: self.bg_color.config(cursor=None))
        self.bg_color.bind('<ButtonRelease-1>', lambda _=None: self.show_color_palette(self.bg_color))

        self.choose_font_combo.grid(row=0, column=0, sticky=NSEW, columnspan=3)
        self.font_size_lbl.grid(row=1, column=0, sticky=W, padx=3)
        self.font_size_entry.grid(row=1, column=1, sticky=W, padx=3)
        self.bold_checkbtn.grid(row=2, column=0, sticky=W, padx=3)
        self.italic_checkbtn.grid(row=3, column=0, sticky=W, padx=3)
        self.underline_checkbtn.grid(row=3, column=1, sticky=W, padx=3)
        self.overstrike_checkbtn.grid(row=2, column=1, sticky=W, padx=3)
        self.fg_color_lbl.grid(row=6, column=0, sticky=W, padx=3)
        self.fg_color.grid(row=6, column=1, sticky=W, padx=3)
        self.bg_color_lbl.grid(row=7, column=0, sticky=W, padx=3)
        self.bg_color.grid(row=7, column=1, sticky=W, padx=3)

        font_names = sorted(tk_font.families())
        self.choose_font_combo['values'] = font_names

        self.configure_configurations(configurations)

    def configure_configurations(self, configurations: dict):
        self.font_size_entry.insert(0, configurations.get('size'))
        self.choose_font_combo.set(value=configurations.get('family'))
        self.bold_intvar.set(configurations.get('bold'))
        self.italic_intvar.set(configurations.get('italic'))
        self.underline_intvar.set(configurations.get('underline'))
        self.overstrike_intvar.set(configurations.get('overstrike'))
        self.bg_color.config(bg=configurations.get('bg'))
        self.fg_color.config(bg=configurations.get('fg'))

    def show_color_palette(self, label):
        color = colorchooser.askcolor(label['background'])
        if color == (None, None):
            pass
        else:
            label.config(bg=color[-1])


class RegexTextArea(ScrolledText):
    TAB_LENGTH = 4

    def __init__(self, master, value_list, regex_list, regex_config_args: dict, **kw):
        ScrolledText.__init__(self, master, **kw)

        self.value_list = value_list
        self.regex_list = regex_list
        self.regex_config_args = regex_config_args
        self.textfilter = None

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

        self.config_regex_args()
        self.highlight_current_line()
        self.apply_regex()

    def _any(self, name, alternates):
        """Return a named group pattern matching list of alternates."""
        return "(?P<%s>" % name + "|".join(alternates) + ")"

    def _coordinate(self, start, end, string):
        """Returns indices of the start and end of matched `string`"""
        srow = string[:start].count('\n') + 1
        scolsplitlines = string[:start].split('\n')

        if len(scolsplitlines) != 0:
            scolsplitlines = scolsplitlines[len(scolsplitlines) - 1]

        scol = len(scolsplitlines)
        lrow = string[:end + 1].count('\n') + 1
        lcolsplitlines = string[:end].split('\n')

        if len(lcolsplitlines) != 0:
            lcolsplitlines = lcolsplitlines[len(lcolsplitlines) - 1]

        lcol = len(lcolsplitlines) + 1

        return '{}.{}'.format(srow, scol), '{}.{}'.format(lrow, lcol)

    def apply_regex(self):
        self.textfilter = re.compile(self.create_regex(), re.S)

    def create_regex(self):
        regex_list = []
        for regex, value in zip(self.regex_list, self.value_list):
            regex_list.append(self._any(value, regex))
        return '|'.join(regex_list)

    def config_regex_args(self):
        pass

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
        self.value_list = value_list
        self.regex_list = regex_list
        self.apply_regex()


class RegexAndDescriptionWindow(Toplevel):
    def __init__(self, master, frame_list: list, value_list: list, description=False, **kw):
        Toplevel.__init__(self, master, **kw)
        self.transient(master)
        self.geometry('700x625')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self._save_on_close)

        self.frame_list = frame_list
        self.value_list = value_list
        self.description = description

        self.edit_frame_list = []

        self.frame = ScrollableFrame(self, **frame_config)
        self.widget_frame = self.frame.widget_frame
        self.frame.pack(side=TOP, fill=BOTH, expand=True, padx=3, pady=2)

        self._insert_description_texts()

    def _insert_description_texts(self):
        for frame, value in zip(self.frame_list, self.value_list):
            rdf = RegexEditingFrame(self.widget_frame, frame, self.description, text=f" {value} ", **label_frame_config)
            rdf.pack(side=TOP, expand=True, fill=BOTH, padx=3, pady=2)
            self.edit_frame_list.append(rdf)

        center_window(self)

    def _save_on_close(self):
        for edit_frame, frame in zip(self.edit_frame_list, self.frame_list):
            if self.description:
                frame.description_entry.delete(1.0, END)
                frame.description_entry.insert(1.0, edit_frame.text.get(1.0, END).rstrip())
            else:
                frame.regex_entry.delete(1.0, END)
                frame.regex_entry.insert(1.0, edit_frame.text.get(1.0, END).rstrip())
        self.destroy()


class RegexConfigurationWindow(Toplevel):
    def __init__(self, master, frame_list, value_list, **kw):
        Toplevel.__init__(self, master, **kw)

    def _insert_config_frames(self):
        pass


class Window(Tk):
    VALUE_LIST = []
    REGEX_LIST = []
    FRAME_LIST = []

    def __init__(self):
        Tk.__init__(self)
        self.title('RegexSyntaxHighlighter')
        self.protocol('WM_DELETE_WINDOW', self._save_on_close)
        self.state('zoomed')

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
        self.text_area = RegexTextArea(self.text_area_frame, value_list=self.VALUE_LIST, regex_list=self.REGEX_LIST,
                                       regex_config_args=self._extract_regex_config_args(), font=font, wrap=NONE,
                                       **text_config)

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

    def add_new_regex_frame(self, event=None, regex='', description='', value='', config_args=''):
        rf = RegexFrame(self.widget_frame, self._update, regex, description, value, config_args)
        rf.pack(side=TOP, fill=X, expand=True, pady=1)
        rf.regex_entry.bind('<ButtonRelease-3>', self._r_click)
        rf.description_entry.bind('<ButtonRelease-3>', self._r_click)
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
        args must be lists like ['<REGEX1>', 'DESCRIPTION1', 'VALUE1' [, 'italic'|'bold', etc]],
        ['<REGEX2>', 'DESCRIPTION2', 'VALUE2' [, 'strikethrough'|'bold', etc], etc
        """
        try:
            for reg, desc, val, config_args in args:
                self.add_new_regex_frame(None, reg, desc, val, config_args)
        except ValueError:
            pass

    def _extract_regex_config_args(self) -> dict:
        return_dict = dict()
        for frame, value in zip(self.FRAME_LIST, self.VALUE_LIST):
            return_dict[value] = frame.configuration_dict
        return return_dict

    def _open_file(self):
        file = filedialog.askopenfile(initialdir=os.path.dirname(os.path.abspath(inspect.getsourcefile(self.__class__))
                                                                 ).replace('/', '\\').rstrip('\\'))
        self.text_area.delete(1.0, END)
        self.text_area.insert(1.0, file.read().rstrip())

    def _r_click(self, event: EventType = None):
        def remove(e):
            frame = e.widget.master
            frame.regex_entry.delete(1.0, END)
            frame.description_entry.delete(1.0, END)
            frame.value_entry.delete(1.0, END)

        description = False
        if type(event.widget).__module__ == 'tkinter.scrolledtext':
            description = True

        r_click_menu = Menu(self, tearoff=0)
        r_click_menu.add_command(label='Copy', command=lambda: event.widget.event_generate('<<Copy>>'))
        r_click_menu.add_command(label='Cut', command=lambda: event.widget.event_generate('<<Cut>>'))
        r_click_menu.add_command(label='Paste', command=lambda: event.widget.event_generate('<<Paste>>'))
        r_click_menu.add_separator()
        r_click_menu.add_command(label='Clear', command=lambda: event.widget.delete(1.0, END))
        r_click_menu.add_command(label='Remove', command=lambda: remove(event))
        r_click_menu.add_command(label='Select All', command=lambda: event.widget.event_generate('<<SelectAll>>'))
        r_click_menu.add_separator()
        r_click_menu.add_command(label='Edit in Separate Window', command=lambda: RegexAndDescriptionWindow(
            self, self.FRAME_LIST, self.VALUE_LIST, description))
        r_click_menu.add_command(label='Configure Appearance', command=lambda: RegexConfigurationWindow(
            self, self.FRAME_LIST, self.VALUE_LIST))
        r_click_menu.tk_popup(event.x_root, event.y_root, 0)
        r_click_menu.grab_release()

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
            config_dict_str = ''
            for tup in list(frame.configuration_dict.items()):
                config_dict_str += '='.join([tup[0], str(tup[1])]) + '|'
            config_dict_str = config_dict_str.rstrip('|')
            line_elements.append(config_dict_str)

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
