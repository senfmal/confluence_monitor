
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
        self.pack()
        self.create_widgets()


    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Refresh data\n(click me)"
        self.hi_there["command"] = self.display_conf_update_info
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom")


    def display_conf_update_info(self):
        update_info = get_conf_update_information(acquire_conf_connection(url), space, theme)
        self.table = st.SimpleTable(self, len(update_info)+1, 3)
        self.table.pack(fill="x")
        self.table.set(0,0,"Page")
        self.table.set(0,1, "Type")
        self.table.set(0,2, "Days w/o update")        


if __name__ == '__main__':
    try:
        url, space, theme = sys.argv[1:]
    except ValueError as err:
        print("You need to specify three parameters:\n\t1. url e.g. 'http://localhost:8080/'\n\t2. space\n\t3. theme i.e. basic label")
        sys.exit()

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
