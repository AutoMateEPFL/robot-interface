import tkinter as tk

# --- classes ---

class Experiment:
    def __init__(self, name=""):
        self.name = name
        self.question_list = []
        self.marker_list = []

    def load_external_window(self, external_window):
        self.root = external_window
        self.root.title("Experiment entry")
        self.root.geometry("200x720")
        self.window = ExperimentFrame(self.root)
        self.window.pack(expand=True, fill='both')

    def launch_registration(self):
        self.root = tk.Tk()
        self.root.title("Experiment entry")
        self.root.geometry("200x700")

        self.window = ExperimentFrame(self.root)
        self.window.pack(expand=True, fill='both')

    def update_name(self,newname):
        self.name = newname


class ExperimentFrame(tk.Frame):
    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)

        # canvas for inner frame
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=0, column=0, sticky='news')  # changed

        # create right scrollbar and connect to canvas Y
        # self._vertical_bar = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        # if vertical:
        #     self._vertical_bar.grid(row=0, column=1, sticky='ns')
        # self._canvas.configure(yscrollcommand=self._vertical_bar.set)

        # create bottom scrollbar and connect to canvas X
        # self._horizontal_bar = tk.Scrollbar(self, orient='horizontal', command=self._canvas.xview)
        # if horizontal:
        #     self._horizontal_bar.grid(row=1, column=0, sticky='we')
        # self._canvas.configure(xscrollcommand=self._horizontal_bar.set)

        # inner frame for widgets
        self.inner = tk.Frame(self._canvas, bg='red')
        self._window = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')

        # autoresize inner frame
        self.columnconfigure(0, weight=1)  # changed
        self.rowconfigure(0, weight=1)  # changed

        # resize when configure changed
        #self.inner.bind('', self.resize)
        #self._canvas.bind('', self.frame_width)


    def frame_width(self, event):
        # resize inner frame to canvas size
        canvas_width = event.width
        self._canvas.itemconfig(self._window, width=canvas_width)

    def resize(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def close_registration(self):
        print('CLOSSEEEE')
        self.root.close()
        #self.window.close()


class Question:

    def __init__(self, parent, question):
        self.parent = parent
        self.question = question
        self.create_widgets()
        self.answer = ""

    def button_function(self):
        value = str(self.entry.get())
        print(str(self.entry.get()))
        self.answer =value

    def create_widgets(self):
        self.labelframe = tk.LabelFrame(self.parent, text="Marker (empty if not used) :")
        self.labelframe.pack(fill="both", expand=True)

        self.label = tk.Label(self.labelframe, text= self.question)
        self.label.pack(expand=True, fill='both')

        self.entry = tk.Entry(self.labelframe)
        self.entry.pack()

        self.button = tk.Button(self.labelframe, text="Validate", command=lambda : self.button_function())
        self.button.pack()

class Question_setup:

    def __init__(self, parent, question, tkinter_window):
        self.parent = parent
        self.tkinter_window = tkinter_window
        self.question = question
        self.create_validator()
        self.create_widgets()
        self.answer = ""

    def button_function(self):
        value = str(self.entry.get())
        print(str(self.entry.get()))
        self.answer =value

    def validate_function(self):
        self.tkinter_window.destroy()
        #self.tkinter_window.close_registration()

    def create_widgets(self):
        self.label = tk.Label(self.labelframe, text= self.question)
        self.label.pack(expand=True, fill='both')

        self.entry = tk.Entry(self.labelframe)
        self.entry.pack()

        self.button = tk.Button(self.labelframe, text="Validate", command=lambda : self.button_function())
        self.button.pack()

    def create_validator(self):
        self.labelframe = tk.LabelFrame(self.parent)
        self.labelframe.pack(fill="both", expand=True)
        self.button = tk.Button(self.labelframe, text="OK", command=self.tkinter_window.destroy)
        #self.button = tk.Button(self.labelframe, text="OK", command=lambda : self.validate_function())
        self.button.pack()

