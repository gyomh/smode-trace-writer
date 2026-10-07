# ------------------------------------------- . ----------------------------------------
# Filename : trace_writer.py                  | Script autonome et reutilisable.        |
#                                              | Launch Mode = "At Every Update"          |
#                                              | (obligatoire - lit une position en       |
#                                              | continu, sinon ne se met jamais a jour). |
#                                              |                                          |
#                                              | Peint une ligne (ShapeLayer avec un       |
#                                              | PathShapeGenerator) a partir de la        |
#                                              | position d'un point mobile (ShapeLayer   |
#                                              | dont le placement.position.x/y bouge).   |
#                                              | Interpole entre l'ancien et le nouvel     |
#                                              | index touche pour ne jamais laisser de   |
#                                              | trous a haute vitesse (developpe pour    |
#                                              | oscilloscope.py, voir ce fichier pour le |
#                                              | contexte audio-reactif complet).          |
#                                              |                                          |
#                                              | UTILISATION :                            |
#                                              | - Si "movingShape"/"lineShape" sont vides|
#                                              |   au premier run : cree automatiquement  |
#                                              |   une DEMO complete (point + ligne +      |
#                                              |   animations X lineaire boucle / Y       |
#                                              |   sinus aller-retour) et se cable dessus.|
#                                              | - Pour reutiliser sur TES propres shapes  |
#                                              |   (ex un point pilote par l'audio) :     |
#                                              |   glisse-les manuellement dans           |
#                                              |   "movingShape"/"lineShape" AVANT le      |
#                                              |   premier run - la demo ne se cree que   |
#                                              |   si les deux sont vides.                |
# Started  : 2026-07-08                        |                                        |
# ------------------------------------------- . ----------------------------------------

movingShape: Oil.createObject("WeakPointer(ShapeLayer)")  # glisser ici le point mobile (optionnel, voir demo auto)
lineShape: Oil.createObject("WeakPointer(ShapeLayer)")    # glisser ici la ligne (optionnel, voir demo auto)
nPoints: Oil.PositiveInteger(1920)  # nombre de points de la ligne, utilise seulement pour la demo auto-creee

lastIdx: Oil.Integer(-1)   # etat interne, ne pas modifier a la main
lastY: Oil.Real(0.5)       # etat interne, ne pas modifier a la main

WRAP_MODE_REPEAT = 1
LAUNCH_MODE_RESTART_WITH_ACTIVATION = 1

# --- Demo auto-creee si rien n'est cable (premiere utilisation, test rapide) ---
if script.movingShape.get() is None or script.lineShape.get() is None:
    N_POINTS = script.nPoints.get()

    demoPoint = Oil.createObject("ShapeLayer")
    demoPoint.label = "Trace Writer Demo Point"
    circleGen = Oil.createObject("CircleShapeGenerator")
    demoPoint.generator = circleGen
    demoPoint.renderer.fill.enabled = False
    demoPoint.renderer.stroke.enabled = True
    demoPoint.renderer.stroke.thickness.set(10.0)
    demoPoint.renderer.placement.position.x = 0.5
    demoPoint.renderer.placement.position.y = 0.5
    script.parentElement.layers.append(demoPoint)

    demoLine = Oil.createObject("ShapeLayer")
    demoLine.label = "Trace Writer Demo Line"
    linePathGen = Oil.createObject("PathShapeGenerator")
    for i in range(N_POINTS):
        cp = Oil.createObject("Path2dControlPoint")
        cp.position.x = i / (N_POINTS - 1)
        cp.position.y = 0.5
        linePathGen.path.points.append(cp)
    demoLine.generator = linePathGen
    demoLine.renderer.fill.enabled = False
    demoLine.renderer.stroke.enabled = True
    demoLine.renderer.stroke.thickness.set(4.0)
    script.parentElement.layers.append(demoLine)

    # Animation X : rampe lineaire en boucle
    xCue = Oil.createObject("FunctionCue(Percentage)")
    xCue.label = "X Linear Loop"
    xShape = Oil.createObject("LinearRampFunctionShape")
    xFunction = Oil.createObject("ParametricScalarFunction({input = Seconds, output = Percentage})")
    xFunction.shape = xShape
    xFunction.parameters.minimum = 0.0
    xFunction.parameters.maximum = 1.0
    xFunction.parameters.period = 4.0
    xFunction.parameters.wrapMode.set(WRAP_MODE_REPEAT)
    xCue.function = xFunction
    xCue.parameters.looping = True
    xCue.parameters.launchMode.set(LAUNCH_MODE_RESTART_WITH_ACTIVATION)
    xCue.transport.length = 4.0
    xTarget = Oil.createObject("ParameterLinkTarget")
    xTarget.target.set(demoPoint.renderer.placement.position.x)
    xCue.targets.append(xTarget)

    # Animation Y : sinus aller-retour
    yCue = Oil.createObject("FunctionCue(Percentage)")
    yCue.label = "Y Sine Back and Forth"
    yShape = Oil.createObject("SineFunctionShape")
    yFunction = Oil.createObject("ParametricScalarFunction({input = Seconds, output = Percentage})")
    yFunction.shape = yShape
    yFunction.parameters.minimum = 0.2
    yFunction.parameters.maximum = 0.8
    yFunction.parameters.period = 2.0
    yFunction.parameters.wrapMode.set(WRAP_MODE_REPEAT)
    yCue.function = yFunction
    yCue.parameters.looping = True
    yCue.parameters.launchMode.set(LAUNCH_MODE_RESTART_WITH_ACTIVATION)
    yCue.transport.length = 2.0
    yTarget = Oil.createObject("ParameterLinkTarget")
    yTarget.target.set(demoPoint.renderer.placement.position.y)
    yCue.targets.append(yTarget)

    demoAnimBank = Oil.createObject("AnimationBank")
    demoAnimBank.label = "Demo Animations"
    demoAnimBank.animations.append(xCue)
    demoAnimBank.animations.append(yCue)
    script.parentElement.tools.append(demoAnimBank)
    xCue.transport.play.trig()
    yCue.transport.play.trig()

    script.movingShape.set(demoPoint)
    script.lineShape.set(demoLine)

    print("Demo auto-creee : point (X boucle lineaire, Y sinus aller-retour) + ligne, cables automatiquement.")

# --- Ecriture de la ligne (a chaque frame) ---
movingShapeElement = script.movingShape.get()
lineShapeElement = script.lineShape.get()

if movingShapeElement is None or lineShapeElement is None:
    print("Aucun ShapeLayer disponible - verifie movingShape/lineShape.")
else:
    px = movingShapeElement.renderer.placement.position.x.get()
    py = movingShapeElement.renderer.placement.position.y.get()

    points = lineShapeElement.generator.path.points
    n = len(points)
    idx = max(0, min(n - 1, int(round(px * (n - 1)))))

    prevIdx = script.lastIdx.get()
    prevY = script.lastY.get()

    if prevIdx < 0 or abs(idx - prevIdx) > n // 2:
        # Premiere execution, ou saut de boucle (retour de fin a debut) : pas d'interpolation
        points[idx].position.y.set(py)
    else:
        step = 1 if idx >= prevIdx else -1
        span = abs(idx - prevIdx)
        for i in range(span + 1):
            t = i / span if span > 0 else 1.0
            y = prevY + (py - prevY) * t
            points[prevIdx + i * step].position.y.set(y)

    script.lastIdx.set(idx)
    script.lastY.set(py)
