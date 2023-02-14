# plaxisautomationcodes
I will add PLAXIS automation codes, including subroutines in this repo.

A Python script using PLAXIS 3D scripting interface to create a soil-structure model consisting of a sand soil layer and a rigid surface representing a foundation. The foundation is subjected to a dynamic vertical load by prescribing a time-dependent displacement history. A geophone is embedded in the soil to monitor the ground motion. The script also includes meshing the model and defining a staged construction with two phases, where the second phase includes dynamic analysis. Finally, the script adds curve points for plotting the recorded data. 

The following is the step-by-step detail of the code: 

Import necessary modules: plxscripting.easy and subprocess. 

Define the path to the PLAXIS application: PLAXIS_PATH. 

Define the port number for input and output connections: PORT_i and PORT_o. 

Set the password for connecting to the application server: PASSWORD. 

Open the PLAXIS application using the subprocess module with the Popen method, passing the application path and the input port, password as arguments. 

Wait for the PLAXIS application to boot up by using time.sleep. 

Create input and output servers for PLAXIS using the new_server method from the plxscripting.easy module, passing the server IP address, port, and password. 

Create a new PLAXIS project using the new method on the input server object. 

Create a rectangular soil contour using the initializerectangular method. 

Create a borehole using the borehole method, and a soil layer using the soillayer method. 

Create a sample material using the soilmat method with the specified material properties and values. 

Assign the material to the soil volume using the setmaterial method. 

Switch to the structure mode using the gotostructures method. 

Define a surface using the surface method, passing the coordinates of four points that define a square. 

Create a point displacement at the surface using the surfdispl method. 

Fix the x and y direction of the surface using the PointDisplacement.Displacement_x and PointDisplacement.Displacement_y attributes of the surface object. 

Prescribe the z-direction displacement using the PointDisplacement.uz attribute of the surface object. 

Define a displacement multiplier using the displmultiplier method. 

Set the amplitude and frequency of the displacement multiplier using the DisplacementMultiplier.Amplitude and DisplacementMultiplier.Frequency attributes of the displacement multiplier object. 

Create a geophone using the embeddedbeam method, passing the coordinates of two points that define a line segment. 

Create a geophone material using the embeddedbeammat method, specifying the material properties and values. 

Assign the geophone material to the geophone using the setmaterial method. 

Switch to the mesh mode using the gotomesh method. 

Generate a mesh using the mesh method, specifying the coarseness, enhanced refinement, and swept meshing parameters. 

View the mesh using the viewmesh method. 

Select mesh points using the selectmeshpoints method. 

Add curve points for plotting using the addcurvepoint method on the output server object. 

Define initial phases using the gotostages and phase methods. 

Define phase 1 by activating the geophone using the activate method. 

Define phase 2 by setting various parameters, such as deform calculation type, time interval, iteration parameters, and boundary conditions. Then activate the point displacement and dynamic point displacement objects. 

Run the simulation using the calculate method. 

 

 

 

 

 
