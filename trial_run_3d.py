from plxscripting.easy import *
import subprocess, time

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

s_i.new()

#create rectangular geometry
g_i.SoilContour.initializerectangular(-1,-1,1,1)

#create borehole
g_i.borehole(0, 0)

#create soillayer
g_i.soillayer(2)

#create a sample material
matprop = ['MaterialName', 'SoilModel', 'Gref', 'cref', 'phi', 'gammaUnsat', 'gammaSat', 'nu', 'InterfaceStrength', 'Rinter']
matval = ['Sand', 2, 19230.7692, 5.0, 28.0, 20.0, 20.0, 0.3, 1, 0.667]

material_data = list(zip(matprop, matval))

g_i.soilmat(*material_data)

#set material to soil volume
g_i.setmaterial(g_i.Soillayer_1.Soil, g_i.Sand)

#go to structure mode
g_i.gotostructures()

#define a surface
Polygon_1 = g_i.surface(0.5,0.5,0.0,-0.5,0.5,0.0,-0.5,-0.5,0.0,0.5,-0.5,0.0)

#createsurfacedisplacement
g_i.surfdispl(Polygon_1)

#fix x and y directions
g_i.Polygon_1.SurfaceDisplacement.Displacement_x = 'fixed'
g_i.Polygon_1.SurfaceDisplacement.Displacement_y = 'fixed'

#prescribe z displacement
g_i.Polygon_1.SurfaceDisplacement.Displacement_y = 'Prescribed'

#static component
g_i.Polygon_1.SurfaceDisplacement.uz = -1.0

#dynamic component
DisplacementMultiplier_1 = g_i.displmultiplier()

g_i.Polygon_1.SurfaceDisplacement.SurfaceDisplacement.Multiplierz = DisplacementMultiplier_1

g_i.DisplacementMultiplier_1.Amplitude = 0.025
g_i.DisplacementMultiplier_1.Frequency = 10.0

#create the geophone
g_i.embeddedbeam(0.0,0.0,-1.0,0.0,0.0,-1.04)

#create the geophone material
g_i.embeddedbeammat('MaterialName', 'Geophone2', 'Elasticity', 0, 'BeamType', 0, 'PredefinedBeamType', 0, 'SkinResistance', 0, 'Diameter', 0.03, 'E', 200000000.0, 'w', 76.5, 'Size', 0.03, 'Tstart', 100, 'Tend', 100, 'A', 0.000706858347057703, 'Iyy', 3.97607820219958E-8, 'Izz', 3.97607820219958E-8, 'Iyz', 0)

#assign material to geophone
g_i.setmaterial(g_i.Line_1.EmbeddedBeam, g_i.Geophone2)

#meshing_procedure
g_i.gotomesh()
g_i.mesh("Coarseness", 0.05, "UseEnhancedRefinements", True, "EMRGlobalScale", 1.2, "EMRMinElementSize", 0.005, "UseSweptMeshing", False)
g_i.viewmesh()
g_i.selectmeshpoints()


#add curve points for plotting
g_o.addcurvepoint('Node', 0.0,0.0,0.0)
g_o.addcurvepoint('Node', g_i.EmbeddedBeam_1_1, (0.0, 0.0, -1.03))
g_o.update()

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
g_i.SurfaceDisplacement_1_1.activate(g_i.Phase_2)
g_i.DynSurfaceDisplacement_1_1.activate(g_i.Phase_2)
g_i.Dynamics.BoundaryXMin[g_i.Phase_5] = "None"
g_i.Dynamics.BoundaryYMin[g_i.Phase_5] = "None"
g_i.Dynamics.BoundaryZMin[g_i.Phase_5] = "Viscous"


