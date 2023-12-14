import tkinter as tk
from job_library import *
import glob
import platform
# --- classes ---
## TODO ADD COMMENT
## FOR NOW ONE EXPERIMENT IS ASSOCIATED TO ONE PLATE HOLDER IS IT NEEDED TO DO 2 CLASSES?
class Experiment:
    """
    This class represents an experiment to be filled out.

    Args:
        name: Empty first, filled out by tkinter then
        question_list: Question on the markers
        marker_list: Answers on the questions once filled out
    """
    def __init__(self, name=""):
        self.name = name
        self.question_list = []
        self.marker_list = []

    def launch_registration(self):
        """Launch registration of experiment/marker names"""
        self.root = tk.Tk()
        self.root.title("Image analysis")
        self.root.geometry("200x230")
        self.window = ExperimentFrame(self.root)
        self.window.pack(expand=True, fill='both')

    def update_name(self, newname):
        self.name = newname

class ExperimentFrame(tk.Frame):
    """
    This class represents a tkinter frame to fill informations on an experiment.

    Args:
        name: Empty first, filled out by tkinter then

    """
    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)

        # canvas for inner frame
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=0, column=0, sticky='news')  # changed

        # inner frame for widgets
        self.inner = tk.Frame(self._canvas, bg='red')
        self._window = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')

        # autoresize inner frame
        self.columnconfigure(0, weight=1)  # changed
        self.rowconfigure(0, weight=1)  # changed

    def frame_width(self, event):
        # resize inner frame to canvas size
        canvas_width = event.width
        self._canvas.itemconfig(self._window, width=canvas_width)

    def resize(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))


class Question:
    """
    This class represents question on experiment name.

    Args:
        name: Empty first, filled out by tkinter then

    """
    def __init__(self, parent, question, tkinter_window, answer="", setup_question=False):
        self.parent = parent
        self.tkinter_window = tkinter_window
        self.question = question
        self.labelframe = tk.LabelFrame(self.parent)
        self.labelframe.pack(fill="both", expand=True)
        if setup_question:
            self.create_validator()
        self.create_widgets()
        self._answer = answer

    def button_function(self):
        value = str(self.entry.get())
        print(str(self.entry.get()))
        self._answer =value

    def validate_function(self):
        self.tkinter_window.destroy()

    def create_widgets(self):
        self.label = tk.Label(self.labelframe, text= self.question)
        self.label.pack(expand=True, fill='both')

        self.entry = tk.Entry(self.labelframe)
        self.entry.pack()

        self.button = tk.Button(self.labelframe, text="Validate", command=lambda : self.button_function())
        self.button.pack()

    def create_validator(self):
        self.button = tk.Button(self.labelframe, text="OK", command=self.tkinter_window.destroy)
        self.button.pack()


if __name__ == "__main__":
    path = os.path.join("..","robot-interface","images","*")
    print("PATH",path)
    #list_of_folders = glob.glob( "../images/*")
    list_of_folders=glob.glob(path)
    print("list_of_folders",list_of_folders)
    list_of_folders.sort(key=os.path.getmtime)
    if platform.system() == 'Windows':
        list_of_experiments = [folder.split("\\")[-1] for folder in list_of_folders]
    else :
        list_of_experiments = [folder.split("/")[-1] for folder in list_of_folders]

    ThisExperiment = Experiment(name="")
    ThisExperiment.launch_registration()
    # Setup questions
    ExperimentNameQuestion = Question(ThisExperiment.window.inner, "Name of the experiment ",
                                      ThisExperiment.root, answer=list_of_experiments[-1], setup_question=True)
    ExperimentNameQuestion.entry.insert(0, list_of_experiments[-1])

    NumberOfColsQuestion = Question(ThisExperiment.window.inner, "Number of cols (9 or 10)", ThisExperiment.root,
                                    answer="9",setup_question=False)
    NumberOfColsQuestion.entry.insert(0, "9")

    to_aggregate = tk.IntVar()
    tk.Checkbutton(ThisExperiment.window.inner, text='Aggregate results', variable=to_aggregate, onvalue=0, offvalue=1).pack()

    ThisExperiment.update_name(ExperimentNameQuestion._answer)

    ThisExperiment.root.mainloop()
    if platform.system() == 'Windows':
        path = os.path.join('images', ExperimentNameQuestion._answer)
    else:
        path = os.path.join('images',ExperimentNameQuestion._answer)
        #"\\nasdcsr.unil.ch\RECHERCHE\FAC\FBM\CIG\avjestic\zygoticfate\D2c\Lab_AutoMate_results"
        path = os.path.join('images',ExperimentNameQuestion._answer)
    #path = "../images/"+str(ExperimentNameQuestion._answer)
    print("path",path)
    analyse_each_image_separately(path, auto_offset=True, auto_rotate=False,
                                   num_cols=int(NumberOfColsQuestion._answer),aggregation = True)
    print("summary")
    summary_of_all_images(path)
