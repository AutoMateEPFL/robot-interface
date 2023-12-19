import os
import tkinter as tk
from job_library import *
from tkinter import filedialog
from tkinter import ttk


class FolderChooserApp:
    def __init__(self, root,path):
        self.root = root
        self.root.title("Folder Chooser")

        # Set the initial path
        self.initial_path = path # Change this to your desired initial path

        # Create and set the variable for selected folder
        self.selected_folder = tk.StringVar()
        self.selected_folder.set("No folder selected")

        # Create and set the label to display the selected folder
        self.selected_folder_label = tk.Label(root, text="Selected folder:")
        self.selected_folder_label.pack(pady=5)


        # Create the Combobox for folder selection
        self.folder_combobox = ttk.Combobox(root, values=[], state="readonly", postcommand=self.update_folder_combobox)
        self.folder_combobox.pack(pady=10)

        # Create the text "Number of Columns" between the two Comboboxes
        ttk.Label(root, text="Number of Columns").pack(pady=5)

        # Create the Combobox for choosing the number of columns
        self.columns_combobox = ttk.Combobox(root, values=[9, 10], state="readonly")
        self.columns_combobox.set(9)
        self.columns_combobox.pack(pady=10)

        # Create two Checkbuttons
        self.aggregate_var = tk.BooleanVar(value=True)  # Set to True for initial check
        self.aggregate_checkbutton = ttk.Checkbutton(root, text="Aggregate Results", variable=self.aggregate_var)
        self.aggregate_checkbutton.pack(pady=5)

        self.sensitivity_checkbutton = ttk.Checkbutton(root, text="High Sensitivity")
        self.sensitivity_checkbutton.pack(pady=5)

        # Create the "Validate" button
        self.validate_button = tk.Button(root, text="Validate", command=self.validate_selection)
        self.validate_button.pack(pady=10)

        # Update the Combobox with the list of folders initially
        self.update_folder_combobox()

    def update_folder_combobox(self):
        # Get the list of folders in the initial path
        folders = [f for f in os.listdir(self.initial_path) if os.path.isdir(os.path.join(self.initial_path, f))]

        # Sort folders by modification time (most recent first)
        folders.sort(key=lambda f: os.path.getmtime(os.path.join(self.initial_path, f)), reverse=True)

        # Set the Combobox values
        self.folder_combobox["values"] = folders

        # Set the default value
        if folders:
            selected_folder = os.path.join(self.initial_path, folders[0])
            self.folder_combobox.set(folders[0])
            self.selected_folder.set(selected_folder)

        else:
            self.folder_combobox.set("No folders")
            self.selected_folder.set("No folder selected")



    def validate_selection(self):
        # Print all the selected values
        self.selected_folder = self.folder_combobox.get()
        self.num_columns = int(self.columns_combobox.get())
        self.aggregate_results = self.aggregate_checkbutton.instate(['selected'])
        self.high_sensitivity = self.sensitivity_checkbutton.instate(['selected'])

        self.root.destroy()

        print("Selected folder:", self.selected_folder)
        print("Number of columns chosen:", self.num_columns)
        print("Aggregate Results:", self.aggregate_results)
        print("High Sensitivity:", self.high_sensitivity)

if __name__ == "__main__":
    if platform.system() == 'Windows':
        path = "C:/Users/AutoMate EPFL/Documents/GitHub/robot-interface/images"
    else:
        path = "/Users/Etienne/Documents/GitHub/robot-interface/images"
    root = tk.Tk()
    app = FolderChooserApp(root,path)
    root.mainloop()

    analyse_each_image_separately(os.path.join(path,app.selected_folder), auto_offset=True, auto_rotate=False,
                                  num_cols=app.num_columns, aggregation=app.aggregate_results)

    summary_of_all_images(os.path.join(path,app.selected_folder))
