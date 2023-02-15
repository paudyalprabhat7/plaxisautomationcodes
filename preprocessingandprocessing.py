from plxscripting.easy import *
import subprocess, time
import pandas as pd

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

def initialize():
    s_i.new()

    #set project length unit to mm
    g_i.setproperties('UnitLength', 'mm')

    #create rectangular geometry
    g_i.SoilContour.initializerectangular(-150,-150, 150, 150)

    #create borehole
    g_i.borehole(0, 0)

    #create soillayer
    g_i.soillayer(300)
    g_i.set(g_i.Borehole_1.Head, -300.0)

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

def createmesh():
    #meshing_procedure
    g_i.gotomesh()
    g_i.set(g_i.Line_1_1.CoarsenessFactor, 0.125)
    g_i.mesh("Coarseness", 0.05, "UseEnhancedRefinements", True, "EMRGlobalScale", 1.2, "EMRMinElementSize", 0.005, "UseSweptMeshing", False)
    g_i.viewmesh()
    g_i.selectmeshpoints()

    #add curve points for plotting
    g_o.addcurvepoint('Node', 0.0,0.0,0.0)
    g_o.addcurvepoint('Node', g_i.EmbeddedBeam_1_1, (0.0, 0.0, -160.0))
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
    g_i.EmbeddedBeam_1_1.activate(g_i.Phase_1)

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

mat = ['Sand', 2, 0.0192307692307692, 5e-6, 28.0, 2e-8, 2e-8, 0.3, 1, 0.667, 3.11, 0.00079577]
geophone_mat = ['Geophone', 0, 0, 0, 0, 30, 200, 7.65e-8, 30, 0.1, 0.1, 706.858347057703, 39760.7820219958, 39760.7820219958, 0, 100]
amp = 25
freq = 10

initialize()
createsoilmat(mat)
createpointdisp()
creategeophone(geophone_mat)
createmesh()
stagedconstruct()
g_i.save('D:\Plaxis Automation Codes\preprocessingexample')

#startcalculation
#g_i.calculate()

'''
#export calculation
A = g_o.getsingleresult(g_o.Phase_2, g_o.ResultTypes.Soil.Uz, (0,0,0))
print(A)
'''

