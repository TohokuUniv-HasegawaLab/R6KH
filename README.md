=====INTRODUCTION=====

This simulator was developed by Python 3.9.6 64-bit and was confirmed to work with Python 3.9.6 64-bit and 3.13.1 64-bit, by modifig https://github.com/cerob/slicesim.
(Development environment: Apple MacBook Air M2 2022 8GB RAM 256GB SSD, and Apple Mac Studio Apple M1 Ultra 128GB RAM 8TB SSD)

Purpose of this simulator:
By discretely simulating the Integrated Access and Backhaul network applied Network Slicing, 
it analyzes how each base station's bandwidth is utilized under different conditions and how routes from user device to IAB donor are selected

=====SYSTEM REQUIREMENTS=====

Download manually the following packages.
Other packages(listed on "Required packages") will be downloaded automatically.

matplotlib
numpy
opencv-python
pandas
PuLP
PyYAML
randomcolor
rich

To solve the optimization problem, we adopted PuLP as a modeler and CPLEX as a solver.
CPLEX version: IBM(R) ILOG(R) CPLEX(R) Interactive Optimizer 22.1.1.0
We also provide an alternative option to use SCIP as a solver.
However, WE STRONGLY RECOMMEND YOU USING CPLEX, for the optimization problem has not yet been verified to work properly with SCIP, also it may takes much more time solve with a solver other than CPLEX.


Required packages(for Python 3.13.1)    Version
------------------------------------- -----------
contourpy                               1.3.1
cycler                                  0.12.1
fonttools                               4.55.6
kiwisolver                              1.4.8
markdown-it-py                          3.0.0
matplotlib                              3.10.0
mdurl                                   0.1.2
numpy                                   2.2.2
opencv-python                           4.11.0.86
packaging                               24.2
pandas                                  2.2.3
pillow                                  11.1.0
pip                                     25.0
PuLP                                    2.9.0
Pygments                                2.19.1
pyparsing                               3.2.1
python-dateutil                         2.9.0.post0
pytz                                    2024.2
PyYAML                                  6.0.2
randomcolor                             0.4.4.6
rich                                    13.9.4
six                                     1.17.0
tzdata                                  2025.1

=====WAY TO USE THIS SIMULATOR=====
=Setup=
This simulator follows the scinario file(defined in yaml file).
Also the scinario you rewrote could be utilized as well.

Please refer to setting_line.yml if you rewrite the scinario.
There are hints what to describe in the scinario file.

Available links between base stations are defined in basestation_in_range_line.csv.
In Row 1 and Column 1, base stations' name is defined.(In the provided csv, I just defined the name as 1 or 2 and so on.) 
If the link is available between two specific base staions, corresponding cell contains 1; otherwise it contains 0.

=Execution=
To run the simulator, execute SimLauncher.py.
SimLauncher.py reads the scinario file and determines the number of times the scinario should be executed.
The number of executions depends on the number of slice deployment combination.(i.e. if you want to simulate under the condition of 1, 2, 4 slices, then the number of executions would be 3)
You get some logs and graphs after the simulation is complete.
You can customize the format of output logs or graphs as needed.
Outputted files are stored in the directory related to the slice deployment.
The results across all slice counts are stored in the same directory as SimLauncher.py.

If the simulator stops unexpectedly, copy the latest 'futures' in Simlogger.log and paste it into 'futures = []' in SimLauncher.py.
Next, remove the slice numbers for which the simulation has already been completed from S1_quantity_list.
S1_quantity_list is defined in SimLaucher.py.
