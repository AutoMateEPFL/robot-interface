import tkinter as tk
import numpy as np

class ExperimentInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Experiment Interface")
        self.available_marker_names = ['ble','bsd','hyg','kan','nat','pat']

        self.create_grid_cell_buttons()
        self.create_frames()
        self.create_checkboxes_and_entries()
        self.create_submit_button()
        self.create_indicator_frame()
        self.matrix_experiment_names = [[[],[]],
                                         [[],[]],
                                         [[],[]],
                                         [[],[]]]
        #self.matrix_experiment_names = np.empty((4,2), dtype=np.array)
        self.matrix_marker_names = [[[],[]],
                                         [[],[]],
                                         [[],[]],
                                         [[],[]]]

    def create_frames(self):
        self.frames = []
        for i in range(1, 5):
            frame = tk.Frame(self.root)
            frame.pack(pady=5)
            self.frames.append(frame)

    def create_grid_cell_buttons(self):
        self.grid_cell_frame = tk.Frame(self.root)
        self.grid_cell_frame.pack(side="left", padx=10)
        self.grid_cell_buttons = []
        for i in range(1, 9):
            button = tk.Button(self.grid_cell_frame, text=f"grid_cell {i}", command=lambda num=i: self.validate(num))
            button.grid(row=(i - 1) // 2, column=(i - 1) % 2, padx=5, pady=5)
            self.grid_cell_buttons.append(button)

    def create_submit_button(self):
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10, side="bottom")

    def create_indicator_frame(self):
        self.indicator_frame = tk.Frame(self.root)
        self.indicator_frame.pack(side="left", padx=10)
        self.create_and_place_indicator()

    def create_checkboxes_and_entries(self):
        self.checkbox_vars = []
        self.entry_vars = []

        for i, frame in enumerate(self.frames, start=1):
            entry, checkboxes, checkbox_vars, entry_var = self.create_experiment_line(frame, i)
            self.entry_vars.append(entry_var)
            self.checkbox_vars.extend(checkbox_vars)

            # Trace changes in each checkbox's IntVar to update the indicator
            for checkbox_var in checkbox_vars:
                checkbox_var.trace_add("write", self.update_indicator)

            # Trace changes in each entry's StringVar to update the indicator
            entry_var.trace_add("write", self.update_indicator)

    def create_experiment_line(self, frame, line_number):
        entry_label = tk.Label(frame, text=f"Experiment {line_number} name:")
        entry_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        entry_var = tk.StringVar()
        entry = tk.Entry(frame, width=20, textvariable=entry_var)
        entry.grid(row=0, column=1, padx=5, pady=5)

        checkboxes = []
        checkbox_labels = self.available_marker_names

        checkbox_vars = []
        for i, label in enumerate(checkbox_labels):
            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(frame, text=label, variable=checkbox_var)
            checkbox.grid(row=0, column=i + 2, padx=5, pady=5)
            checkboxes.append(checkbox)
            checkbox_vars.append(checkbox_var)

        return entry, checkboxes, checkbox_vars, entry_var

    def create_and_place_indicator(self):
        self.indicator = tk.Label(self.indicator_frame, text="Indicator", bg="green", width=20)
        self.indicator.pack(pady=10)

    def submit(self):
        # Function to be executed when the submit button is pressed
        # You can access the values of the entries and checkboxes here
        self.root.destroy()
        #pass

    def validate(self,button_number):

        row, col  = (button_number - 1) // 2, (button_number - 1) % 2
        # Function to be executed when a validator button is pressed
        self.grid_cell_buttons[button_number - 1].config(bg="yellow")  # Change color to yellow
        print(f"Validator button {button_number} pressed.")
        grid_cell_buttons = self.grid_cell_buttons[button_number - 1]
        grid_cell_buttons.config(text=grid_cell_buttons.cget('text') + ' FILLED',
                                font='Helvetica 13 bold')  # Change color to yellow

        ## reset to prevent multiple click on same cell:
        self.matrix_experiment_names[row][col] = []
        self.matrix_marker_names[row][col]  = []
        for i in range(0,4):
            experiment_name = self.entry_vars[i].get()
            if experiment_name !='':
                self.matrix_experiment_names[row][col].append(self.entry_vars[i].get())
                self.matrix_marker_names[row][col].append('original')
                for j in range(0,6):
                    if self.checkbox_vars[6*i+j].get() ==1:
                        self.matrix_marker_names[row][col].append(self.available_marker_names[j])
        print("row,col",row,col)
        print("exp", self.matrix_experiment_names[row][col])
        print("markers", self.matrix_marker_names[row][col])
        

    def update_indicator(self, *args):
        # Function to update the indicator based on the checkbox states and non-empty entries
        checked_checkboxes = sum(checkbox_var.get() for checkbox_var in self.checkbox_vars)
        non_empty_entries = sum(bool(entry_var.get()) for entry_var in self.entry_vars)
        threshold = 12  # Set your desired threshold here
        total_petri_dishes = non_empty_entries+checked_checkboxes
        if total_petri_dishes >=threshold :
            self.indicator.config(bg="red")
        else:
            self.indicator.config(bg="green")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentInterface(root)
    root.mainloop()
