from confluence.ConfLastUpdated import acquire_conf_connection, get_conf_update_information
from gui.LoginFrame import LoginFrame
import pandas as pd
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

class Application(tk.Frame):
    def __init__(
        self, master=None,
        conf_url='http://localhost:8080',
        conf_space=None,
        conf_theme=None,
        conf_categories={},
        thresholds={}
    ):
        super().__init__(master)
        self.master = master
        self.conf_url = conf_url
        self.conf_connection = self.connect_to_confluence()
        self.conf_space = conf_space
        self.conf_theme = conf_theme
        self.conf_categories = conf_categories
        self.thresholds = thresholds
        self.sorting, self.ascending = self.get_sorting(self.conf_categories)
        self.config_environ()
        self.create_widgets()


    def config_environ(self):
        self.update_info = None
        self.search_terms = None
        self.var_filters = {}
        for category in self.conf_categories.keys():
            self.var_filters[category] = tk.IntVar(value=1)


    def create_widgets(self):
        self.grid_configure(sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.build_menu()
        self.build_search()
        self.add_separator(**{'row': 1, 'columnspan': 5, 'sticky': 'ew'})
        self.build_filter()
        self.add_separator(**{'row': 3, 'columnspan': 5, 'sticky': 'ew'})
        self.build_table()
        self.attach_bindings()

        self.display_conf_update_info()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.select_table_row(0)


    def build_menu(self):
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.nav_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Programm', menu=self.nav_menu)
        self.nav_menu.add_command(label='Refresh data', command=self.display_conf_update_info, accelerator="Ctrl+R")
        self.nav_menu.add_separator()
        self.nav_menu.add_command(label='Quit', command=self.master.destroy, accelerator="Ctrl+Q")


    def build_search(self):
        self.search_frame = tk.Frame(self)
        self.search_frame.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.label_search = tk.Label(self.search_frame, text="Suche:")
        self.entry_search = tk.Entry(self.search_frame, width=100)
        self.btn_search = tk.Button(self.search_frame, text="Go", command=self.btn_search_clicked)
        self.label_search.grid(row=0, column=0, sticky='w')
        self.entry_search.grid(row=0, column=1, columnspan=3, sticky='ew')
        self.btn_search.grid(row=0, column=4, sticky='e')


    def add_separator(self, parent=None, **kwargs):
        parent = self if parent is None else parent
        tk.Frame(parent, height=5, bd=1, relief=tk.SUNKEN).grid(kwargs)


    def build_filter(self):
        self.filter_frame = tk.Frame(self)
        self.filter_buttons = []
        for key in self.conf_categories.keys():
            self.filter_buttons.append(
                tk.Checkbutton(
                    self.filter_frame,
                    text=key,
                    variable=self.var_filters[key],
                    command=self.cb_clicked
                )
            )
        self.filter_frame.grid(row=2, column=0, columnspan=len(self.filter_buttons), sticky='nsew')
        self.filter_label = tk.Label(self.filter_frame, text='Filter nach:')
        self.add_separator(parent=self.filter_frame, **{'row':1, 'column':0, 'columnspan':len(self.filter_buttons), 'sticky': 'ew'})
        self.filter_label.grid(row=0, column=0, columnspan=len(self.filter_buttons), sticky='ew')
        col = 0
        for btn in self.filter_buttons:
            btn.grid(row=2, column=col, sticky='nsew')
            col += 1


    def build_table(self):
        self.table_frame = tk.Frame(self)
        self.table_frame.grid(row=4, column=0, columnspan=5, sticky="nsew")
        self.labelColA = tk.Label(self.table_frame, text="Page", background='lightblue')
        self.labelColB = tk.Label(self.table_frame, text="Type", background='lightblue')
        self.labelColC = tk.Label(self.table_frame, text="Days w/o update", background='lightblue')
        self.labelColA.grid(row=0, column=0, sticky="ew")
        self.labelColB.grid(row=0, column=1, sticky="ew")
        self.labelColC.grid(row=0, column=2, sticky="ew")

        self.vsb = tk.Scrollbar(self.table_frame, orient="vertical", command=self.OnVsb, takefocus=tk.NO)
        self.colA = tk.Listbox(self.table_frame, width=50, height=20, yscrollcommand=self.vsb.set, exportselection=0)
        self.colB = tk.Listbox(self.table_frame, width=50, height=20, yscrollcommand=self.vsb.set, exportselection=0)
        self.colC = tk.Listbox(self.table_frame, width=50, height=20, yscrollcommand=self.vsb.set, exportselection=0)

        self.vsb.grid(column=3, sticky="nsew")
        self.colA.grid(row=1, column=0, sticky="nsew")
        self.colB.grid(row=1, column=1, sticky="nsew")
        self.colC.grid(row=1, column=2, sticky="nsew")


    def attach_bindings(self):
        self.master.bind('<Control-q>', lambda event: self.master.destroy())
        self.master.bind('<Control-r>', lambda event: self.display_conf_update_info())
        self.colA.bind('<Up>', lambda event: self.scroll_listboxes(-1))
        self.colB.bind('<Up>', lambda event: self.scroll_listboxes(-1))
        self.colC.bind('<Up>', lambda event: self.scroll_listboxes(-1))

        self.colA.bind('<Down>', lambda event: self.scroll_listboxes(1))
        self.colB.bind('<Down>', lambda event: self.scroll_listboxes(1))
        self.colC.bind('<Down>', lambda event: self.scroll_listboxes(1))

        self.colA.bind('<End>', self.end_pressed)
        self.colB.bind('<End>', self.end_pressed)
        self.colC.bind('<End>', self.end_pressed)

        self.colA.bind('<Home>', self.home_pressed)
        self.colB.bind('<Home>', self.home_pressed)
        self.colC.bind('<Home>', self.home_pressed)

        self.colA.bind('<Next>', self.pgdown_pressed)
        self.colB.bind('<Next>', self.pgdown_pressed)
        self.colC.bind('<Next>', self.pgdown_pressed)

        self.colA.bind('<Prior>', self.pgup_pressed)
        self.colB.bind('<Prior>', self.pgup_pressed)
        self.colC.bind('<Prior>', self.pgup_pressed)

        self.colA.bind("<MouseWheel>", self.OnMouseWheel)
        self.colB.bind("<MouseWheel>", self.OnMouseWheel)
        self.colC.bind("<MouseWheel>", self.OnMouseWheel)

        self.colA.bind('<<ListboxSelect>>', self.OnSelectionChanged)
        self.colB.bind('<<ListboxSelect>>', self.OnSelectionChanged)
        self.colC.bind('<<ListboxSelect>>', self.OnSelectionChanged)

        self.entry_search.bind('<Return>', self.OnEnterKeyPressed)


    def select_table_row(self, index):
        self.colA.focus_set()
        self.colA.activate(index)
        self.colA.select_set(index)
        self.colB.select_set(index)
        self.colC.select_set(index)


    def OnVsb(self, *args):
        self.colA.yview(*args)
        self.colB.yview(*args)
        self.colC.yview(*args)


    def OnMouseWheel(self, event):
        if event.num == 5 or event.delta == -120:
            yFactor = 1
        else:
            yFactor = -1
        self.colA.yview("scroll", yFactor, "units")
        self.colB.yview("scroll", yFactor, "units")
        self.colC.yview("scroll", yFactor, "units")
        return "break"


    def OnSelectionChanged(self, event):
        w = event.widget
        try:
            index = int(w.curselection()[0])
            if index != int(self.colA.curselection()[0]):
                self.colA.selection_clear(0, 'end')
            if index != int(self.colB.curselection()[0]):
                self.colB.selection_clear(0, 'end')
            if index != int(self.colC.curselection()[0]):
                self.colC.selection_clear(0, 'end')
            self.select_table_row(index)
        except IndexError:
            return "break"
        return "break"


    def home_pressed(self, event):
        self.colA.see(0)
        self.colA.activate(0)
        self.colB.see(0)
        self.colB.activate(0)
        self.colC.see(0)
        self.colC.activate(0)
        self.clear_selection()
        self.select_table_row(0)


    def end_pressed(self, event):
        lbox_size = self.colA.size()
        self.colA.see(lbox_size)
        self.colA.activate(lbox_size)
        self.colB.see(lbox_size)
        self.colB.activate(lbox_size)
        self.colC.see(lbox_size)
        self.colC.activate(lbox_size)
        self.clear_selection()
        self.select_table_row(tk.END)


    def pgup_pressed(self, event):
        self.colA.yview_scroll(-(self.colA["height"]), "units")
        self.colB.yview_scroll(-(self.colB["height"]), "units")
        self.colC.yview_scroll(-(self.colC["height"]), "units")
        current_select = int(self.colA.curselection()[0])
        if current_select - self.colA['height'] < 0:
            current_select = self.colA['height']
        self.clear_selection()
        self.select_table_row(current_select - self.colA['height'])
        return "break"


    def pgdown_pressed(self, event):
        self.colA.yview_scroll(self.colA["height"], "units")
        self.colB.yview_scroll(self.colB["height"], "units")
        self.colC.yview_scroll(self.colC["height"], "units")
        current_select = int(self.colA.curselection()[0])
        if current_select + self.colA['height'] > self.colA.size():
            current_select = self.colA.size() - self.colA['height'] - 1
        self.clear_selection()
        self.select_table_row(current_select + self.colA['height'])
        return "break"


    def OnEnterKeyPressed(self, event):
        self.btn_search.invoke()


    def scroll_listboxes(self, yFactor):
        # function runs when a listbox has focus and the Up or Down arrow is pressed
        self.colA.yview_scroll(yFactor, "units")
        self.colB.yview_scroll(yFactor, "units")
        self.colC.yview_scroll(yFactor, "units")


    def clear_selection(self):
        self.colA.selection_clear(0, 'end')
        self.colB.selection_clear(0, 'end')
        self.colC.selection_clear(0, 'end')


    def get_Type(self, page):
        cat_type = []
        bgcolor = self['bg']
        for category in self.conf_categories.keys():
            if page.iloc[0][category]:
                cat_type.append(category)
        for threshold in self.thresholds.keys():
            if page.iloc[0][threshold] and int(page.iloc[0]['last_updated']) > self.thresholds[threshold]['limit']:
                bgcolor = self.thresholds[threshold]['bgcolor']
        return cat_type, bgcolor


    def display_conf_update_info(self,
        search_terms = None,
        update=True,
        sorting=['inactive'],
        ascending=[1]
    ):
        self.search_terms = search_terms if search_terms is not None else self.search_terms
        if update == True:
            self.update_info = get_conf_update_information(
                self.conf_connection,
                self.conf_space,
                self.conf_theme,
                self.conf_categories
            )
        filtered_info = []
        for category in self.conf_categories.keys():
            if self.var_filters[category].get() == 1:
                filtered_info.append(self.update_info[(self.update_info[category]==True) &
                    (self.update_info['inactive']==False)
            ])
            if category == 'inactive':
                if self.var_filters[category].get() == 1:
                    filtered_info.append(self.update_info[self.update_info[category]==True])
        if filtered_info:
            filtered_update = pd.concat(filtered_info)
            if self.search_terms is not None:
                for term in self.search_terms:
                    filtered_update = filtered_update[filtered_update['name'].str.contains(term)]
            sorted_info = filtered_update.sort_values(self.sorting, ascending=self.ascending)
            self.delete_table()
            for item in list(sorted_info['name']):
                page = sorted_info[sorted_info['name']==item]
                self.colA.insert("end", item)
                cat_type, bgcolor = self.get_Type(page)
                self.colB.insert("end", ', '.join(item for item in cat_type))
                self.colC.insert("end", page.iloc[0]['last_updated'])
                if not page.iloc[0]['inactive']:
                    self.colC.itemconfig('end', background=bgcolor)
                else:
                    self.colA.itemconfig('end', foreground='gray')
                    self.colB.itemconfig('end', foreground='gray')
                    self.colC.itemconfig('end', foreground='gray')
                self.colA.config(width=0)
                self.colB.config(width=0)
                self.colC.config(width=15)
                self.winfo_toplevel().wm_geometry("")
            self.select_table_row(0)
        else:
            self.delete_table()


    def delete_table(self):
        self.colA.delete(0,'end')
        self.colB.delete(0,'end')
        self.colC.delete(0,'end')


    def connect_to_confluence(self):
        login = tk.Tk()
        login.lift()
        login.attributes("-topmost", True)
        lf = LoginFrame(login)
        login.mainloop()
        connection = acquire_conf_connection(self.conf_url, username=lf.username, password=lf.password)
        login.destroy()
        return connection


    def get_sorting(self, categories):
        sort_cat = []
        ascending = []
        for i in range(len(categories)):
            for category, attributes in categories.items():
                if attributes['sorting']['priority']==i and i > 0:
                    sort_cat.append(category)
                    ascending.append(attributes['sorting']['asc'])
        return sort_cat, ascending


    def btn_search_clicked(self):
        self.display_conf_update_info(update=False, search_terms=self.entry_search.get().split())


    def cb_clicked(self):
        self.display_conf_update_info(update=False)
