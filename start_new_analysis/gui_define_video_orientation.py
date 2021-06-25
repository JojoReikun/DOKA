from tkinter import *
from tkinter.ttk import *
import os

current_path = os.getcwd()
print("current path: ", current_path)


class Window(Frame):
    def __init__(self, master=None):
        # Define settings upon initialization. Here you can specify
        Frame.__init__(self, master)
        # reference to the master widget, which is the tk window
        self.master = master
        # with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Define video orientation of lizard runs")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # Adding widgets to the root window
        # Adding text labels:
        label_intro = Label(self, text='Please check the orientation of the video footage ...\n '
                                       '...and click on the image which shows the correct configuration for the current species.',
                            font=('Verdana', 10))
        label_intro.grid(column=0, row=0, columnspan=2)

        global label_var
        label_var = StringVar()

        label_config = Label(self, textvariable=label_var,
                             font=('Verdana', 10))
        label_config.grid(column=0, row=2, columnspan=2)
        label_var.set('The default configuration for the analysis is set to 1.')

        # creating image objects to use on button instead of text
        global x_up_dir_up  # make global to retain a reference, otherwise destroyed while __init__() exists
        global x_down_dir_up
        """
        x_up_dir_up = PhotoImage(
            file=os.path.join(current_path, r'lizardanalysis', 'start_new_analysis', 'GUI_video_config_x_up_dir_up.png'))
        x_down_dir_up = PhotoImage(
            file=os.path.join(current_path, r'lizardanalysis', 'start_new_analysis', 'GUI_video_config_x_down_dir_up.png'))
        """

        """
        # works in console only with added 'lizardanlysis' to path explicitly
        
        x_up_dir_up = PhotoImage(
            file=os.path.join(current_path, 'lizardanalysis', 'start_new_analysis', 'GUI_video_config_x_up_dir_up.png'))
        x_down_dir_up = PhotoImage(
            file=os.path.join(current_path, 'lizardanalysis', 'start_new_analysis', 'GUI_video_config_x_down_dir_up.png'))
        """

        x_up_dir_up = PhotoImage(
            file=os.path.join(current_path, 'start_new_analysis', 'GUI_video_config_x_up_dir_up.png'))
        x_down_dir_up = PhotoImage(
            file=os.path.join(current_path, 'start_new_analysis', 'GUI_video_config_x_down_dir_up.png'))

        # creating a button instance
        btn_x_up_dir_up = Button(self, image=x_up_dir_up, command=self.btn_on_clicked_1)
        btn_x_down_dir_up = Button(self, image=x_down_dir_up, command=self.btn_on_clicked_2)

        # placing the button on my window
        btn_x_up_dir_up.grid(column=0, row=1, padx=10, pady=10)
        btn_x_down_dir_up.grid(column=1, row=1, padx=10, pady=10)

    # define the default clicked value
    global clicked
    clicked = '1'

    def btn_on_clicked_1(self):
        global clicked
        clicked = '1'
        label_var.set('Configuration ' + clicked + ' is now set for the analysis. Close the GUI to continue.')
        # print('clicked: ', clicked)

    def btn_on_clicked_2(self):
        global clicked
        clicked = "2"
        label_var.set('Configuration ' + clicked + ' is now set for the analysis. Close the GUI to continue.')
        # print('clicked: ', clicked)


# TODO: add OKAY button to proceed and make X abort


def gui_choose_video_config():
    # creating tkinter window
    root = Tk()

    def on_closing():
        # destroy window when it has fulfilled its purpose
        print("Window destroyed!")
        root.destroy()

    root.geometry("800x450")

    # place the GUI window in front of all other windows.
    root.attributes("-topmost", True)

    # creation of an instance
    app = Window(root)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    # mainloop
    root.mainloop()

    return int(clicked)
