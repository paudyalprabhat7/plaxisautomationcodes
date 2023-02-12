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

    #create rectangular geometry
    g_i.SoilContour.initializerectangular(-1,-1,1,1)

    #create borehole
    g_i.borehole(0, 0)

    #create soillayer
    g_i.soillayer(2)

def createsoilmat(matval):
    #create a sample material
    matprop = ['MaterialName', 'SoilModel', 'Gref', 'cref', 'phi', 'gammaUnsat', 'gammaSat', 'nu', 'InterfaceStrength', 'Rinter']
    material_data = list(zip(matprop, matval))
    return g_i.soilmat(*material_data)

mat = ['Sand', 2, 19230.7692, 5.0, 28.0, 20.0, 20.0, 0.3, 1, 0.667]


'''
#set material to soil volume
g_i.setmaterial(g_i.Soillayer_1.Soil, g_i.Sand)
'''

def createpointdisp(amp, freq):
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

    g_i.DisplacementMultiplier_1.Amplitude = amp
    g_i.DisplacementMultiplier_1.Frequency = freq

def creategeophone(mat):
    #create the geophone
    g_i.embeddedbeam(0.0,0.0,-1.0,0.0,0.0,-1.04)

    #create the geophone material
    matprop = ['MaterialName', 'Elasticity', 'BeamType', 'PredefinedBeamType', 'SkinResistance', 'Diameter', 'E', 'w', 'Size', 'Tstart', 'Tend', 'A', 'Iyy', 'Izz', 'Iyz']
    material = list(zip(matprop, mat))
    g_i.embeddedbeammat(*material)

geophone_mat = ['Geophone', 0, 0, 0, 0, 0.03, 200000000.0, 76.5, 0.03, 100, 100, 0.000706858347057703, 3.97607820219958E-8, 3.97607820219958E-8, 0.0]

'''
#assign material to geophone
g_i.setmaterial(g_i.Line_1.EmbeddedBeam, g_i.Geophone2)
'''
def createmesh():
    #meshing_procedure
    g_i.gotomesh()
    g_i.set(g_i.Line_1_1.CoarsenessFactor, 0.125)
    g_i.mesh("Coarseness", 0.05, "UseEnhancedRefinements", True, "EMRGlobalScale", 1.2, "EMRMinElementSize", 0.005, "UseSweptMeshing", False)
    g_i.viewmesh()
    g_i.selectmeshpoints()

    #add curve points for plotting
    g_o.addcurvepoint('Node', 0.0,0.0,0.0)
    g_o.addcurvepoint('Node', g_i.EmbeddedBeam_1_1, (0.0, 0.0, -1.03))
    g_o.update()

initialize()
createsoilmat(mat)
createpointdisp(0.025,10.0)
creategeophone(geophone_mat)
createmesh()

'''
#staged construction and defining initial phases
g_i.gotostages()
g_i.phase(g_i.InitialPhase)
g_i.phase(g_i.Phase_1)

#defining phase 1
g_i.EmbeddedBeam_1_1.activate(g_i.Phase_1)

#defining phase 2
g_i.set(g_i.Phase_2.DeformCalcType, 'Dynamic')
g_i.set(g_i.Phase_2.Deform.TimeIntervalSeconds, 0.5)
g_i.set(g_i.Phase_2.Deform.ResetDisplacementsToZero, True)
g_i.set(g_i.Phase_2.Deform.UseDefaultIterationParams, False)
g_i.set(g_i.Phase_2.Deform.TimeStepDetermType, 'Manual')
g_i.PointDisplacement_1_1.activate(g_i.Phase_2)
g_i.DynPointDisplacement_1_1.activate(g_i.Phase_2)
g_i.Dynamics.BoundaryXMin[g_i.Phase_2] = "None"
g_i.Dynamics.BoundaryYMin[g_i.Phase_2] = "None"
g_i.Dynamics.BoundaryZMin[g_i.Phase_2] = "Viscous"

#startcalculation
g_i.calculate()
g_i.view(g_i.Phase_2)

#export calculation
A = g_o.getsingleresult(g_o.Phase_2, g_o.ResultTypes.Soil.Uz, (0,0,0))
print(A)

'''
