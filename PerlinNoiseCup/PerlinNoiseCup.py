#Author-Jotaro Shigeyama
#Description-Cup made by code.

import adsk.core, adsk.fusion, adsk.cam, traceback

import math #math functions 
import os, sys # system modules
from .Modules import noise as noise

def sweepNormalToSpline(spline,radius,rootComp):    
    path = rootComp.features.createPath(spline)
    # create construction plane normal to the spline
    planes = rootComp.constructionPlanes
    planeInput = planes.createInput()
    planeInput.setByDistanceOnPath(path, adsk.core.ValueInput.createByReal(0))
    plane = planes.add(planeInput)
    
    sketches = rootComp.sketches
    sketch = sketches.add(plane)
    
    center = plane.geometry.origin
    center = sketch.modelToSketchSpace(center)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
    profile = sketch.profiles[0]
    
    # Create a sweep input
    sweeps = rootComp.features.sweepFeatures
    sweepInput = sweeps.createInput(profile,path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    sweepInput.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
    
    # Create the sweep.
    sweep = sweeps.add(sweepInput)
    return sweep
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
        comp = design.rootComponent
        
        sketch = comp.sketches.add(comp.xYConstructionPlane)
        points = adsk.core.ObjectCollection.create()
        
        #Object parameters
        height = 15.0
        theta_steps = 30
        height_steps = 30
        noise_scale = 0.072
        radius_scale = 1.8
        radius_bottom = 2.5
        radius_pipe = 0.25
        for i in range(theta_steps):
            theta = i * 2 * math.pi / float(theta_steps)
            for j in range(height_steps):
                # R= radius_bottom + j*radius_scale/float(height_steps);
                R = radius_bottom + 0.013 * (height/height_steps*j) * (height/height_steps*j)
                print(R);
                points.add(adsk.core.Point3D.create(R*math.cos(theta+ noise.pnoise1(j*noise_scale + 100 * i)),
                                                    height/height_steps*j,
                                                    R*math.sin(theta+noise.pnoise1(j*noise_scale + 100 *i))));
            spline = sketch.sketchCurves.sketchFittedSplines.add(points)
            sweep = sweepNormalToSpline(spline, radius_pipe, comp)
            points = adsk.core.ObjectCollection.create()
            
        app.activeViewport.refresh()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
