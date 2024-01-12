import tkinter as tk

def submit():
    # Function to be executed when the submit button is pressed
    # You can access the values of the entries and checkboxes here
    pass

def validate(button_number):
    # Function to be executed when a validator button is pressed
    validator_buttons[button_number - 1].config(bg="yellow")  # Change color to yellow
    print(f"Validator button {button_number} pressed.")
    validator_button = validator_buttons[button_number - 1]
    validator_button.config(text=validator_button.cget('text') + ' FILLED', font='Helvetica 13 bold')  # Change color to yellow



def update_indicator(*args):
    # Function to update the indicator based on the checkbox states and non-empty entries
    checked_checkboxes = sum(checkbox_var.get() for checkbox_var in checkbox_vars)
    non_empty_entries = sum(bool(entry_var.get()) for entry_var in entry_vars)
    threshold = 3  # Set your desired threshold here

    if checked_checkboxes >= threshold or non_empty_entries > 0:
        indicator.config(bg="red")
    else:
        indicator.config(bg="green")

# Create the main Tkinter window
root = tk.Tk()
root.title("Experiment Interface")

# Function to create a line with an entry, labels, and 6 checkboxes
def create_line(frame, line_number):
    entry_label = tk.Label(frame, text=f"Experiment {line_number} name:")
    entry_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    entry_var = tk.StringVar()  # Use StringVar for Entry
    entry = tk.Entry(frame, width=20, textvariable=entry_var)
    entry.grid(row=0, column=1, padx=5, pady=5)

    checkboxes = []
    checkbox_labels = ['ble','bsd','hyg','kan','nat','pat']

    checkbox_vars = []
    for i, label in enumerate(checkbox_labels):
        checkbox_var = tk.IntVar()
        checkbox = tk.Checkbutton(frame, text=label, variable=checkbox_var)
        checkbox.grid(row=0, column=i+2, padx=5, pady=5)
        checkboxes.append(checkbox)
        checkbox_vars.append(checkbox_var)

    return entry, checkboxes, checkbox_vars, entry_var

# Create a frame for each line
frame1 = tk.Frame(root)
frame2 = tk.Frame(root)
frame3 = tk.Frame(root)
frame4 = tk.Frame(root)

# Create lines with entry, labels, and checkboxes
entry1, checkboxes1, checkbox_vars1, entry_var1 = create_line(frame1, 1)
entry2, checkboxes2, checkbox_vars2, entry_var2 = create_line(frame2, 2)
entry3, checkboxes3, checkbox_vars3, entry_var3 = create_line(frame3, 3)
entry4, checkboxes4, checkbox_vars4, entry_var4 = create_line(frame4, 4)

# Create a matrix of validator buttons
validator_frame = tk.Frame(root)
validator_frame.pack(side="left", padx=10)
validator_matrix = []
validator_buttons = []  # List to keep track of validator buttons

for i in range(4):
    row_buttons = []
    for j in range(2):
        button_number = i * 2 + j + 1
        button = tk.Button(validator_frame, text=f"Pile {i},{j}", command=lambda num=button_number: validate(num))
        button.grid(row=i, column=j, padx=5, pady=5)
        row_buttons.append(button)
        validator_buttons.append(button)
    validator_matrix.append(row_buttons)

# Create and place a submit button
submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.pack(pady=10, side="bottom")

# Pack frames into the main window
frame1.pack(pady=5)
frame2.pack(pady=5)
frame3.pack(pady=5)
frame4.pack(pady=5)

# Create an indicator frame
indicator_frame = tk.Frame(root)
indicator_frame.pack(side="left", padx=10)

# Create checkboxes and associated IntVars
all_checkboxes = checkboxes1 + checkboxes2 + checkboxes3 + checkboxes4
checkbox_vars = checkbox_vars1 + checkbox_vars2 + checkbox_vars3 + checkbox_vars4

# Create entries and associated StringVars
all_entries = [entry1, entry2, entry3, entry4]
entry_vars = [entry_var1, entry_var2, entry_var3, entry_var4]

# Create and place an indicator
indicator = tk.Label(indicator_frame, text="Max number of Petri dishes reached", bg="green", width=30)
indicator.pack(pady=10)

# Trace changes in each checkbox's IntVar to update the indicator
for checkbox_var in checkbox_vars:
    checkbox_var.trace_add("write", update_indicator)

# Trace changes in each entry's StringVar to update the indicator
for entry_var in entry_vars:
    entry_var.trace_add("write", update_indicator)

# Initialize the indicator
update_indicator()

# Start the Tkinter event loop
root.mainloop()
