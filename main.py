
import pprint
import sys
from ConfLastUpdated import acquire_conf_connection, get_conf_update_information
import tkinter as tk
import tkinter.ttk as ttk
import SimpleTable as st

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
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
        self.colA = tk.Listbox(self, yscrollcommand=self.vsb.set)
        self.colB = tk.Listbox(self, yscrollcommand=self.vsb.set)
        self.colC = tk.Listbox(self, yscrollcommand=self.vsb.set)

        self.vsb.grid(column=3, sticky=tk.N+tk.S)
        self.colA.grid(row=4, column=0)
        self.colB.grid(row=4, column=1)
        self.colC.grid(row=4, column=2)

        self.colA.bind("<MouseWheel>", self.OnMouseWheel)
        self.colB.bind("<MouseWheel>", self.OnMouseWheel)
        self.colC.bind("<MouseWheel>", self.OnMouseWheel)


    def OnVsb(self, *args):
        self.colA.yview(*args)
        self.colB.yview(*args)
        self.colC.yview(*args)

    def OnMouseWheel(self, event):
        self.colA.yview("scroll", event.delta*-1, "units")
        self.colB.yview("scroll", event.delta*-1, "units")
        self.colC.yview("scroll", event.delta*-1, "units")
        return "break"


    def display_conf_update_info(self):
        update_info = get_conf_update_information(acquire_conf_connection(url), space, theme)
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
            self.colA.config(width=0)
            self.colB.config(width=0)
            self.colC.config(width=15)
            self.winfo_toplevel().wm_geometry("")


if __name__ == '__main__':
    try:
        url, space, theme = sys.argv[1:]
    except ValueError as err:
        print("You need to specify three parameters:\n\t1. url e.g. 'http://localhost:8080/'\n\t2. space\n\t3. theme i.e. basic label")
        sys.exit()

    root = tk.Tk()
    root.title("Confluence Monitor v0.1")
    app = Application(master=root)
    app.mainloop()
