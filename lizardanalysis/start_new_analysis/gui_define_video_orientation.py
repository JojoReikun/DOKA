from tkinter import *
from tkinter.ttk import *
import os

current_path = os.getcwd()
print("current path: ", current_path)

# TODO: clicked value not changed accordingly, when button is clicked. Always returns second event...
def btn_on_clicked_1():
    global clicked
    clicked = 'clicked first image'
    # print('clicked: ', clicked)


def btn_on_clicked_2():
    global clicked
    clicked = "clicked second image"
    # print('clicked: ', clicked)


def gui_choose_video_config():
    # creating tkinter window
    window = Tk()
    window.title("Define video orientation of lizard runs")
    window.geometry('740x400')

    # Adding widgets to the root window
    label_intro = Label(window, text='Please check the orientation of the video footage ...\n '
                                     '...and click on the image wich shows the correct configuration for the current species.',
      font=('Verdana', 10))
    label_intro.grid(column=0, row=0, columnspan=2)

    # Creating a photoimage object to use image
    x_up_dir_up = PhotoImage(file=current_path+r'\lizardanalysis\start_new_analysis\GUI_video_config_x_up_dir_up.png')
    x_down_dir_up = PhotoImage(file=current_path+r'\lizardanalysis\start_new_analysis\GUI_video_config_x_down_dir_up.png')

    # create a style for buttons:
    style = Style()
    style.configure('TButton', borderwidth='4')

    # here, image option is used to set image on button
    btn_x_up_dir_up = Button(window, image=x_up_dir_up)
    btn_x_down_dir_up = Button(window, image=x_down_dir_up)
    btn_x_up_dir_up.bind('<Button-1>', btn_on_clicked_1())
    btn_x_down_dir_up.bind('<Button-1>', btn_on_clicked_2())
    btn_x_up_dir_up.grid(column=0, row=1, padx = 10, pady = 10)
    btn_x_down_dir_up.grid(column=1, row=1, padx = 10, pady = 10)


    #set default clicked value for testing:
    clicked = 1
    window.mainloop()

    return clicked