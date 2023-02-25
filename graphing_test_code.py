from plxscripting.easy import *
import subprocess, time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime

#PLAXIS path
PLAXIS_PATH = r'C:\Program Files\Bentley\Geotechnical\PLAXIS 3D CONNECT Edition V21\Plaxis3DInput.exe'

PORT_i = 10000 #defining a port number
PORT_o = 10001 

PASSWORD = 'Pr@bhatASU9#'

#opening PLAXIS 3D
subprocess.Popen([PLAXIS_PATH, f'--AppServerPassword={PASSWORD}', f'--AppServerPort={PORT_i}'], shell=False)

#waiting for PLAXIS 3D to boot
time.sleep(5)

#starting the scripting server
s_i, g_i = new_server('localhost', PORT_i, password = PASSWORD)
s_o, g_o = new_server('localhost', PORT_o, password = PASSWORD)

def initialize(a):
    s_i.new()

    #set project length unit to mm
    g_i.setproperties('UnitLength', 'mm')

    #create rectangular geometry
    g_i.SoilContour.initializerectangular(-a, -a, a, a)

    #create borehole
    g_i.borehole(0, 0)

    #create soillayer
    g_i.soillayer(2*a)
    g_i.set(g_i.Borehole_1.Head, -2*a)

def createsoilmat(matval):
    #create a sample material
    matprop = ['MaterialName', 'SoilModel', 'Gref', 'cref', 'phi', 'gammaUnsat', 'gammaSat', 'nu', 'InterfaceStrength', 'Rinter', 'RayleighAlpha', 'RayleighBeta']
    material_data = list(zip(matprop, matval))
    return g_i.soilmat(*material_data)

def createpointdisp():
    #go to structure mode
    g_i.gotostructures()

    #define a point
    Point_1 = g_i.point(0.0, 0.0, 0.0)

    #createPointDisplacement
    g_i.pointdispl(Point_1)

    #fix x and y directions
    g_i.Point_1.PointDisplacement.Displacement_x = 'fixed'
    g_i.Point_1.PointDisplacement.Displacement_y = 'fixed'

    #prescribe z displacement
    g_i.Point_1.PointDisplacement.Displacement_z = 'Prescribed'

    #static component
    g_i.Point_1.PointDisplacement.uz = -1.0

    #dynamic component
    DisplacementMultiplier_1 = g_i.displmultiplier()

    g_i.Point_1.PointDisplacement.PointDisplacement.Multiplierz = DisplacementMultiplier_1

def setpointdisp(amp,freq): 
    g_i.DisplacementMultiplier_1.Amplitude = amp
    g_i.DisplacementMultiplier_1.Frequency = freq

def creategeophone(mat):
    #create the geophone
    g_i.embeddedbeam(0.0,0.0,-150.0,0.0,0.0,-190.0)

    #create the geophone material
    matprop = ['MaterialName', 'Elasticity', 'BeamType', 'PredefinedBeamType', 'SkinResistance', 'Diameter', 'E', 'w', 'Size', 'Tstart', 'Tend', 'A', 'Iyy', 'Izz', 'Iyz', 'Fmax']
    material = list(zip(matprop, mat))
    g_i.embeddedbeammat(*material)

def createmesh(hz_extents):
    #meshing_procedure
    g_i.gotomesh()
    g_i.set(g_i.Line_1_1.CoarsenessFactor, 0.125)
    g_i.mesh("Coarseness", 0.05, "UseEnhancedRefinements", True, "EMRGlobalScale", 1.2, "EMRMinElementSize", 0.005, "UseSweptMeshing", False)
    g_i.viewmesh()
    g_i.selectmeshpoints()

    #add curve points for plotting
    g_o.addcurvepoint('Node', 0.0,0.0,0.0)
    #g_o.addcurvepoint('Node', g_i.EmbeddedBeam_1_1, (0.0, 0.0, -160.0))
    g_o.addcurvepoint('Node', 0.0, 0.0, -hz_extents)
    g_o.update()

def stagedconstruct():
    #going to structures and assigning materials and assigning surf_displacement
    g_i.gotostructures()
    
    #set material to soil volume
    g_i.setmaterial(g_i.Soillayer_1.Soil, g_i.Sand)

    #set material to geophone
    g_i.setmaterial(g_i.Line_1.EmbeddedBeam, g_i.Geophone)

    #set dynamic multipliers of the displacement
    setpointdisp(amp, freq)
    
    #staged construction and defining initial phases
    g_i.gotostages()
    g_i.phase(g_i.InitialPhase)
    g_i.phase(g_i.Phase_1)
    g_i.phase(g_i.Phase_2)
    
    #defining phase 1
    #g_i.EmbeddedBeam_1_1.activate(g_i.Phase_1)

    #defining phase 2
    g_i.set(g_i.Phase_2.DeformCalcType, 'Dynamic')
    g_i.set(g_i.Phase_2.Deform.TimeIntervalSeconds, 0.5)
    g_i.set(g_i.Phase_2.Deform.ResetDisplacementsToZero, True)
    g_i.set(g_i.Phase_2.Deform.UseDefaultIterationParams, False)
    g_i.set(g_i.Phase_2.Deform.ToleratedError, 0.05)
    g_i.set(g_i.Phase_2.Deform.TimeStepDetermType, 'Manual')
    g_i.PointDisplacement_1_1.activate(g_i.Phase_2)
    g_i.DynPointDisplacement_1_1.activate(g_i.Phase_2)
    g_i.Dynamics.BoundaryXMin[g_i.Phase_2] = "None"
    g_i.Dynamics.BoundaryYMin[g_i.Phase_2] = "None"
    g_i.Dynamics.BoundaryZMin[g_i.Phase_2] = "Viscous"

    #defining phase 3
    g_i.set(g_i.Phase_3.DeformCalcType, 'Dynamic')
    g_i.set(g_i.Phase_3.Deform.TimeIntervalSeconds, 0.5)
    g_i.set(g_i.Phase_3.Deform.UseDefaultIterationParams, False)
    g_i.set(g_i.Phase_3.Deform.ToleratedError, 0.05)
    g_i.set(g_i.Phase_3.Deform.TimeStepDetermType, 'Manual')
    g_i.PointDisplacement_1_1.deactivate(g_i.Phase_3)
    g_i.Dynamics.BoundaryXMin[g_i.Phase_3] = "None"
    g_i.Dynamics.BoundaryYMin[g_i.Phase_3] = "None"
    g_i.Dynamics.BoundaryZMin[g_i.Phase_3] = "Viscous"


def getgraph(node):
    g_i.view(g_i.InitialPhase)

    # Define a list of step names
    step = []
    for i in range(102, 202):
        step.append('Step_' + str(i))
        
    # Generate an array of 100 equally spaced values between 0 and 0.5
    values = np.linspace(0, 0.5, num=100)

    # Create a pandas Series object with the time step values
    timestep = pd.Series(values, index=range(100))

    # Create an empty pandas DataFrame object
    df = pd.DataFrame()

    # Add the time step Series to the DataFrame as a column named 't(sec)'
    df['t (sec)'] = timestep

    # Create an empty list to store the results for each step
    result = []

    # Iterate over each step in the step list
    for i in range(len(step)):
        # Get the attribute for the current step using getattr
        step_attr = getattr(g_o, step[i])
        # Call the getcurveresults method to get the displacement results for the current step
        result.append(g_o.getcurveresults(g_o.curvePoints.Nodes[node], step_attr, g_o.ResultTypes.Soil.Uz))

    # Create a new pandas Series object with the displacement results and add it to the DataFrame as a column named 'z (mm)'
    df['z (mm)'] = pd.Series(result)

    plt.style.reload_library()
    plt.style.use(['grid', 'science', 'notebook'])

    #graphing
    x = df['t (sec)'].tolist()
    y = df['z (mm)'].tolist()

    plt.figure(facecolor = 'white')
    plt.plot(x,y)
    plt.xlabel('Dynamic Time (sec)')
    plt.ylabel('Vertical Displacement, Uz (mm)')

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string in the format YYYY-MM-DD_HH:MM:SS
    date_str = now.strftime("%Y-%m-%d_%H%M")

    # Append "graph_" to the beginning of the date string
    filename = "graph_" + date_str

    # Set the directory for saving the file
    directory = "D:\\Plaxis Automation Codes\\Graphs\\"

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the figure as a PNG file with the specified filename and dpi
    plt.savefig(os.path.join(directory, filename + ".png"), dpi=300)

    plt.show()

def savefile():
      # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string in the format YYYY-MM-DD_HH:MM:SS
    date_str = now.strftime("%Y-%m-%d")

    # Append "graph_" to the beginning of the date string
    filename = "test_" + date_str

    # Set the directory for saving the file
    directory = "D:\\Plaxis Automation Codes\\"

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    g_i.save(os.path.join(directory,filename))

mat = ['Sand', 2, 0.0192307692307692, 5e-6, 28.0, 2e-8, 2e-8, 0.3, 1, 0.667, 3.11, 0.00079577]
geophone_mat = ['Geophone', 0, 0, 0, 0, 30, 200, 7.65e-8, 30, 0.1, 0.1, 706.858347057703, 39760.7820219958, 39760.7820219958, 0, 100]
amp = 25
freq = 10
hor_ext = 2500.0

initialize(hor_ext)
createsoilmat(mat)
createpointdisp()
creategeophone(geophone_mat)
createmesh(hor_ext)
stagedconstruct()
g_i.calculate()
savefile()
getgraph(0)
getgraph(1)