import os, sys, json
from gui import MainWindow as mw
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

if __name__ == '__main__':
    vers_num = 0.7
    try:
        url, space, theme, status_threshold, vorhaben_threshold, block_threshold = sys.argv[1:]
    except ValueError as err:
        try:
            with open(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    *('config','config.json')
                ), 'r'
            ) as config_file:
                config = json.load(config_file)
                url = config['CONNECT']['conf_url']
                space = config['CONNECT']['conf_space']
                theme = config['CONNECT']['conf_theme']
                thresholds = config['THRESHOLDS']
                categories = config['CATEGORY']
        except BaseException as err:
        	msg = """You need to specify six parameters:
    1. url e.g. 'http://localhost:8080/'
    2. space
    3. theme i.e. basic label
    Thresholds for:
        4. Status
        5. Vorhaben
        6. Blocks"""
        	print(msg)
        	print("Alternatively, you could also define a 'config.json' configuration file")
        	print(err)
        	sys.exit()

    root = tk.Tk()
    root.title("Confluence Monitor v{}".format(vers_num))

    w = 600 # width for the Tk root
    h = 200 # height for the Tk root
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    # calculate x and y coordinates for the Tk root window
    dimensioner = 3
    x = (ws/dimensioner) - (w/dimensioner)
    y = (hs/dimensioner) - (h/dimensioner)
    # set the dimensions of the screen
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    app = mw.Application(
        master=root,
        conf_url=url,
        conf_space=space,
        conf_theme=theme,
        conf_categories=categories,
        thresholds=thresholds
    )
    app.mainloop()
