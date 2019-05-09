from confluence.ConfLastUpdated import acquire_conf_connection, get_conf_update_information
from gui.LoginFrame import LoginFrame
try:
    import Tkinter as tk ## Python 2.x
except ImportError:
    import tkinter as tk ## Python 3.x

class Application(tk.Frame):
    def __init__(
        self, master=None,
        conf_url='http://localhost:8080',
        conf_space=None,
        conf_theme=None,
        status_threshold=360,
        vorhaben_threshold=360,
        block_threshold=360
    ):
        super().__init__(master)
        self.master = master
        self.conf_url = conf_url
        self.conf_connection = self.connect_to_confluence()
        self.conf_space = conf_space
        self.conf_theme = conf_theme
        self.status_threshold = status_threshold
        self.vorhaben_threshold = vorhaben_threshold
        self.block_threshold = block_threshold
        self.create_widgets()


    def create_widgets(self):
        self.grid_configure(sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.nav_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Programm', menu=self.nav_menu)
        self.nav_menu.add_command(label='Refresh data', command=self.display_conf_update_info, accelerator="Ctrl+R")
        self.nav_menu.add_separator()
        self.nav_menu.add_command(label='Quit', command=self.master.destroy, accelerator="Ctrl+Q")

        self.labelColA = tk.Label(self, text="Page", background='lightblue')
        self.labelColB = tk.Label(self, text="Type", background='lightblue')
        self.labelColC = tk.Label(self, text="Days w/o update", background='lightblue')
        self.labelColA.grid(row=0, column=0)
        self.labelColB.grid(row=0, column=1)
        self.labelColC.grid(row=0, column=2)
        self.labelColA.grid_configure(sticky="ew")
        self.labelColB.grid_configure(sticky="ew")
        self.labelColC.grid_configure(sticky="ew")

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.OnVsb)
        self.colA = tk.Listbox(self, width=50, height=20, yscrollcommand=self.vsb.set, exportselection=0)
        self.colB = tk.Listbox(self, width=50, height=20, yscrollcommand=self.vsb.set, exportselection=0)
        self.colC = tk.Listbox(self, width=50, height=20, yscrollcommand=self.vsb.set, exportselection=0)

        self.vsb.grid(column=3)
        self.colA.grid(row=1, column=0)
        self.colB.grid(row=1, column=1)
        self.colC.grid(row=1, column=2)

        self.vsb.grid_configure(sticky="nsew")
        self.colA.grid_configure(sticky="nsew")
        self.colB.grid_configure(sticky="nsew")
        self.colC.grid_configure(sticky="nsew")

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

        self.display_conf_update_info()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.select_table_row(0)


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


    def scroll_listboxes(self, yFactor):
        # function runs when a listbox has focus and the Up or Down arrow is pressed
        self.colA.yview_scroll(yFactor, "units")
        self.colB.yview_scroll(yFactor, "units")
        self.colC.yview_scroll(yFactor, "units")


    def clear_selection(self):
        self.colA.selection_clear(0, 'end')
        self.colB.selection_clear(0, 'end')
        self.colC.selection_clear(0, 'end')


    def display_conf_update_info(self):
        update_info = get_conf_update_information(self.conf_connection, self.conf_space, self.conf_theme)
        self.delete_table()
        for k, page in update_info.items():
            self.colA.insert("end", page['name'])
            type = []
            if 'is_block' in page.keys():
                type.append('Block')
            if 'is_vorhaben' in page.keys():
                type.append('Vorhaben')
            if 'is_status' in page.keys():
                type.append('Status')
            if 'is_news' in page.keys():
                type.append('News')
            self.colB.insert("end", ', '.join(item for item in type))
            self.colC.insert("end", page['lastUpdated'])
            if 'Block' in type and int(page['lastUpdated']) > self.block_threshold:
                self.colC.itemconfig('end', background='grey')
            if 'Vorhaben' in type and int(page['lastUpdated']) > self.vorhaben_threshold:
                self.colC.itemconfig('end', background='yellow')
            if 'Status' in type and int(page['lastUpdated']) > self.status_threshold:
                self.colC.itemconfig('end', background='red')
            self.colA.config(width=0)
            self.colB.config(width=0)
            self.colC.config(width=15)
            self.winfo_toplevel().wm_geometry("")
        self.select_table_row(0)


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
