import os, sys, json
from gui import MainWindow as mw
try:
    import Tkinter as tk ## Python 2.x
except ImportError:
    import tkinter as tk ## Python 3.x

if __name__ == '__main__':
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
                status_threshold = config['THRESHOLDS']['status']
                vorhaben_threshold = config['THRESHOLDS']['vorhaben']
                block_threshold = config['THRESHOLDS']['block']
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
    root.title("Confluence Monitor v0.1")

    w = 600 # width for the Tk root
    h = 500 # height for the Tk root
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    # set the dimensions of the screen
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    app = mw.Application(
        master=root,
        conf_url=url,
        conf_space=space,
        conf_theme=theme,
        status_threshold=status_threshold,
        vorhaben_threshold=vorhaben_threshold,
        block_threshold=block_threshold
    )
    app.mainloop()
