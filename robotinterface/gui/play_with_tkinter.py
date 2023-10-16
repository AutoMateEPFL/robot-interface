from experiment_tkinter import *


ThisExperiment =Experiment(name="")
ThisExperiment.launch_registration()
ExperimentNameQuestion = Question(ThisExperiment.window.inner, "Name of the experiment ")

ThisExperiment.update_name(ExperimentNameQuestion.answer)

print(ThisExperiment.name)
for i in range(6):
    ThisExperiment.marker_list.append(Question(ThisExperiment.window.inner, "Name of the marker " + str(i + 1)))

print(ThisExperiment.marker_list[0].answer)
ThisExperiment.root.mainloop()
