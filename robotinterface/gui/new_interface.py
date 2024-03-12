import tkinter as tk
from tkinter import ttk  # Import ttk module for themed widgets
from tkinter import messagebox

class InteractiveWindow:
    def __init__(self, title="Interactive Window"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("900x400")  # Set the initial window size

        #Utils
        self.max_plate_number = 96

        # Create tabs
        self.notebook = ttk.Notebook(self.root) 
        self.notebook.pack(expand=True, fill="both")

        # First tab (Experiments)
        self.tab1 = tk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Experiments")
        self.lines = []
        self.line_count = 0
        self.create_tab1_content()

        # Second tab (Description)
        self.tab2 = tk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Description")
        self.create_tab2_content()

        # Experiment data
        self.experiment_data = []

        # Bind Enter key to start method
        self.root.bind("<Return>", self.start)  

        self.root.mainloop()

    def create_tab1_content(self):
        # Create scrollable canvas
        self.canvas = tk.Canvas(self.tab1)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.tab1, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Add initial lines
        self.add_line()
        self.add_line()
        self.add_line()

        # Create a frame for buttons
        self.button_frame = tk.Frame(self.tab1)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Add button to add new lines
        self.add_button = tk.Button(self.button_frame, text="+ Add Line", command=self.add_line)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=10)  # Properly position the "Add Line" button

        # Add Start button
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.RIGHT, padx=10, pady=10)  # Properly position the "Start" button

        # Add label to display the number of checkboxes checked
        self.checked_label = tk.Label(self.tab1, text="", fg="black")
        self.checked_label.pack()

    def create_tab2_content(self):
        self.description_text = tk.Text(self.tab2, wrap="word")
        self.description_text.pack(fill="both", expand=True)

    def add_line(self):
        self.line_count += 1

        # Create label for the line
        label_text = f"Experiment {self.line_count} name :"
        label = tk.Label(self.scrollable_frame, text=label_text)
        label.grid(row=self.line_count, column=0, sticky="w")

        # Create label for markers
        markers_label = tk.Label(self.scrollable_frame, text="Markers :")
        markers_label.grid(row=self.line_count, column=3, sticky="w")

        # Add space between experiment name and markers
        space_label = tk.Label(self.scrollable_frame, text="       ")
        space_label.grid(row=self.line_count, column=2)

        # Create entry for the line
        entry = tk.Entry(self.scrollable_frame, width=30)
        entry.grid(row=self.line_count, column=1, sticky="w")

        # Create checkboxes for markers
        markers = ["ori", "ble", "bsd", "hyg", "kan", "nat", "pat"]
        checkboxes = []
        for i, marker in enumerate(markers):
            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(self.scrollable_frame, variable=checkbox_var, text=marker,
                                        command=self.check_checkboxes)
            checkbox.grid(row=self.line_count, column=i+4)
            checkboxes.append(checkbox_var)

        self.lines.append((label, entry, checkboxes))

    def check_checkboxes(self):
        total_checked = sum(checkbox_var.get() for _, _, checkboxes in self.lines for checkbox_var in checkboxes)
        if total_checked > self.max_plate_number:
            self.checked_label.config(text=f"Too many plates ({total_checked}/{self.max_plate_number})", fg="red")
        else:
            self.checked_label.config(text=f"{total_checked}/{self.max_plate_number} plates", fg="black")

    def start(self, event=None):
        total_checked = sum(checkbox_var.get() for _, _, checkboxes in self.lines for checkbox_var in checkboxes)
        if total_checked > self.max_plate_number:
            messagebox.showerror("Error", "Maximum number of plates reached ({max})".format(max = self.max_plate_number))
        else:
            for label, entry, checkboxes in self.lines:
                experiment_name = entry.get()
                markers = [marker for marker, checkbox_var in zip(["ori", "ble", "bsd", "hyg", "kan", "nat", "pat"], checkboxes) if checkbox_var.get() == 1]
                self.experiment_data.append((experiment_name, markers))

            print("Experiment data:", self.experiment_data)
            self.root.destroy()  # Close the window

    def get_experiment_data(self):
        '''
        Returns the experiments interactive window data in a list with the format : [(Experiment number, 'Name of experiment', [markers of experiment])]
        '''

        # Add the number of the experiment and remove the empty experiments
        data = [(number+1, experiment[0], experiment[1]) for number, experiment in enumerate(self.experiment_data)]
        data = [data[i] for i in range(len(data)) if data[i][1] != '']
        return data



    
if __name__ == "__main__":

    # Create an instance of the InteractiveWindow class
    experiment_interface = InteractiveWindow(title = "Experiment Interface")
    experiment_data = experiment_interface.get_experiment_data()

    print('outside class', experiment_data)
    print(len(experiment_data))
    for number, experiment in  enumerate(experiment_data) :
        print(f"Experiment {number+1} | Name : {experiment[1]} | Markers : {experiment[2]}")




