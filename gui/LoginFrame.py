try:
    from Tkinter import * ## Python 2.x
except ImportError:
    from tkinter import * ## Python 3.x
import getpass


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.winfo_toplevel().title("Login...")

        self.label_username = Label(self, text="Username")
        self.label_password = Label(self, text="Password")

        self.entry_username = Entry(self)
        self.entry_username.insert(0, getpass.getuser())
        self.entry_password = Entry(self, show="*")

        self.label_username.grid(row=0, sticky=E)
        self.label_password.grid(row=1, sticky=E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.logbtn = Button(self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

        self.entry_password.bind('<Return>', self.OnEnterKeyPressed)

        self.pack()
        self.entry_password.focus_set()

    def _login_btn_clicked(self):
        self.username = self.entry_username.get()
        self.password = self.entry_password.get()
        self.quit()


    def OnEnterKeyPressed(self, event):
        self.logbtn.invoke()
