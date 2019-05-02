from confluence.ConfLastUpdated import acquire_conf_connection, get_conf_update_information
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
        self.conf_connection = acquire_conf_connection(self.conf_url)
        self.conf_space = conf_space
        self.conf_theme = conf_theme
        self.status_threshold = status_threshold
        self.vorhaben_threshold = vorhaben_threshold
        self.block_threshold = block_threshold
        self.grid()
        self.create_widgets()


    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Refresh data"
        self.hi_there["command"] = self.display_conf_update_info
        self.hi_there.grid(row=0, column=0, sticky=tk.W)

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.grid(row=0, column=3, sticky=tk.E)

        tk.Frame(self, height=5, bd=1, relief=tk.SUNKEN).grid(row=2, columnspan=4, sticky=tk.E+tk.W)

        self.labelColA = tk.Label(self, text="Page", background='lightblue')
        self.labelColB = tk.Label(self, text="Type", background='lightblue')
        self.labelColC = tk.Label(self, text="Days w/o update", background='lightblue')
        self.labelColA.grid(row=3, column=0, sticky=tk.E+tk.W)
        self.labelColB.grid(row=3, column=1, sticky=tk.E+tk.W)
        self.labelColC.grid(row=3, column=2, sticky=tk.E+tk.W)

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.OnVsb)
        self.colA = tk.Listbox(self, yscrollcommand=self.vsb.set, exportselection=0)
        self.colB = tk.Listbox(self, yscrollcommand=self.vsb.set, exportselection=0)
        self.colC = tk.Listbox(self, yscrollcommand=self.vsb.set, exportselection=0)

        self.vsb.grid(column=3, sticky=tk.N+tk.S)
        self.colA.grid(row=4, column=0)
        self.colB.grid(row=4, column=1)
        self.colC.grid(row=4, column=2)

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

        self.colA.focus_set()
        self.colA.activate(0)
        self.colA.select_set(0)
        self.colB.select_set(0)
        self.colC.select_set(0)


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
                self.colA.select_set(index)
            if index != int(self.colB.curselection()[0]):
                self.colB.selection_clear(0, 'end')
                self.colB.select_set(index)
            if index != int(self.colC.curselection()[0]):
                self.colC.selection_clear(0, 'end')
                self.colC.select_set(index)
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
        

    def end_pressed(self, event):
        lbox_size = self.colA.size()
        self.colA.see(lbox_size)
        self.colA.activate(lbox_size)
        self.colB.see(lbox_size)
        self.colB.activate(lbox_size)
        self.colC.see(lbox_size)
        self.colC.activate(lbox_size)
        self.clear_selection()
        

    def pgup_pressed(self, event):
        self.colA.yview_scroll(-(self.colA["height"]), "units")
        self.colB.yview_scroll(-(self.colB["height"]), "units")
        self.colC.yview_scroll(-(self.colC["height"]), "units")
        self.clear_selection()
        return "break"
        

    def pgdown_pressed(self, event):
        self.colA.yview_scroll(self.colA["height"], "units")
        self.colB.yview_scroll(self.colB["height"], "units")
        self.colC.yview_scroll(self.colC["height"], "units")
        self.clear_selection()
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
            type = ''
            if 'is_block' in page.keys():
                type = 'Block'
            if 'is_vorhaben' in page.keys():
                type = 'Vorhaben'
            if 'is_status' in page.keys():
                type = 'Status'
            self.colB.insert("end", type)
            self.colC.insert("end", page['lastUpdated'])
            if type == 'Status' and int(page['lastUpdated']) > self.status_threshold:
                self.colC.itemconfig('end', background='red')
            if type == 'Vorhaben' and int(page['lastUpdated']) > self.vorhaben_threshold:
                self.colC.itemconfig('end', background='yellow')
            if type == 'Block' and int(page['lastUpdated']) > self.block_threshold:
                self.colC.itemconfig('end', background='grey')
            self.colA.config(width=0)
            self.colB.config(width=0)
            self.colC.config(width=15)
            self.winfo_toplevel().wm_geometry("")
            

    def delete_table(self):
        self.colA.delete(0,'end')
        self.colB.delete(0,'end')
        self.colC.delete(0,'end')
