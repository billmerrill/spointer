from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.gui.DirectGui import *
import math

class ArrowScene(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set up basic environment
        self.setBackgroundColor(0.5, 0.8, 1.0)  # Sky blue background
        
        # Add ground plane
        self.ground = self.loader.loadModel("models/plane")
        self.ground.setScale(100, 100, 1)
        self.ground.setColor(0.6, 0.8, 0.6)  # Green-ish color
        self.ground.reparentTo(self.render)
        self.ground.setPos(0, 0, 0)
        
        # Add directional lighting
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        self.render.setLight(dlnp)
        
        # Add ambient light
        alight = AmbientLight('alight')
        alight.setColor(VBase4(0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Create the arrow
        self.arrow = self.createArrow()
        self.arrow.setPos(0, 0, 10)  # Position arrow 10 units above the ground
        self.arrow.reparentTo(self.render)
        
        # Create the compass rose
        self.compass = self.createCompassRose()
        self.compass.setPos(0, 0, 0.1)  # Position just above the ground
        self.compass.reparentTo(self.render)
        
        # Set up camera
        self.camera.setPos(0, -50, 20)  # Position the camera
        self.camera.lookAt(0, 0, 10)  # Look at the arrow
        
        # Variables to track camera orbit and arrow orientation
        self.cameraOrbitAngle = 0
        self.cameraOrbitRadius = 50
        self.cameraOrbitHeight = 20
        self.arrowHeading = 0
        self.arrowPitch = 0
        
        # Set up controls
        self.setupControls()
        
        # Add instructions
        self.setupInstructions()
        
    def createArrow(self):
        # Create an arrow shape
        arrowRoot = NodePath("ArrowRoot")
        
        # Shaft
        shaft = self.loader.loadModel("models/cylinder")
        shaft.setScale(0.5, 0.5, 5)
        shaft.setPos(0, 0, 2.5)
        shaft.setColor(1, 0, 0)  # Red 
        shaft.reparentTo(arrowRoot)
        
        # Head
        head = self.loader.loadModel("models/cone")
        head.setScale(1.5, 1.5, 2)
        head.setPos(0, 0, 8)
        head.setColor(1, 0, 0)  # Red
        head.reparentTo(arrowRoot)
        
        return arrowRoot
    
    def createCompassRose(self):
        # Create compass rose
        compassRoot = NodePath("CompassRoot")
        
        # Create the cardinal direction lines
        lines = LineSegs()
        lines.setThickness(2)
        
        # North (blue)
        lines.setColor(0, 0, 1, 1)
        lines.moveTo(0, 0, 0)
        lines.drawTo(0, 20, 0)
        
        # East (red)
        lines.setColor(1, 0, 0, 1)
        lines.moveTo(0, 0, 0)
        lines.drawTo(20, 0, 0)
        
        # South (green)
        lines.setColor(0, 1, 0, 1)
        lines.moveTo(0, 0, 0)
        lines.drawTo(0, -20, 0)
        
        # West (yellow)
        lines.setColor(1, 1, 0, 1)
        lines.moveTo(0, 0, 0)
        lines.drawTo(-20, 0, 0)
        
        node = lines.create()
        linesNP = NodePath(node)
        linesNP.reparentTo(compassRoot)
        
        # Add labels for directions
        self.createTextLabel("N", 0, 22, 0).reparentTo(compassRoot)
        self.createTextLabel("E", 22, 0, 0).reparentTo(compassRoot)
        self.createTextLabel("S", 0, -22, 0).reparentTo(compassRoot)
        self.createTextLabel("W", -22, 0, 0).reparentTo(compassRoot)
        
        return compassRoot
    
    def createTextLabel(self, text, x, y, z):
        # Create a TextNode to display a label
        textNode = TextNode('label')
        textNode.setText(text)
        textNode.setTextColor(0, 0, 0, 1)
        textNode.setAlign(TextNode.ACenter)
        
        textNodePath = NodePath(textNode)
        textNodePath.setPos(x, y, z)
        textNodePath.setBillboardPointEye()
        textNodePath.setScale(3)
        
        return textNodePath
    
    def setupControls(self):
        # Set up keyboard controls for camera orbit
        self.accept("arrow_left", self.adjustCameraOrbit, [-5])
        self.accept("arrow_right", self.adjustCameraOrbit, [5])
        self.accept("arrow_up", self.adjustCameraHeight, [2])
        self.accept("arrow_down", self.adjustCameraHeight, [-2])
        
        # Set up keyboard controls for arrow orientation
        self.accept("a", self.adjustArrowHeading, [-5])
        self.accept("d", self.adjustArrowHeading, [5])
        self.accept("w", self.adjustArrowPitch, [5])
        self.accept("s", self.adjustArrowPitch, [-5])
        
        # Controls for camera zoom
        self.accept("=", self.adjustCameraRadius, [-5])
        self.accept("-", self.adjustCameraRadius, [5])
        
    def adjustCameraOrbit(self, delta):
        self.cameraOrbitAngle += delta
        self.updateCameraPosition()
        
    def adjustCameraHeight(self, delta):
        self.cameraOrbitHeight += delta
        self.updateCameraPosition()
    
    def adjustCameraRadius(self, delta):
        self.cameraOrbitRadius += delta
        if self.cameraOrbitRadius < 10:
            self.cameraOrbitRadius = 10
        self.updateCameraPosition()
        
    def updateCameraPosition(self):
        # Calculate camera position based on orbit angle and radius
        angleRadians = math.radians(self.cameraOrbitAngle)
        x = self.cameraOrbitRadius * math.sin(angleRadians)
        y = self.cameraOrbitRadius * -math.cos(angleRadians)
        z = self.cameraOrbitHeight
        
        self.camera.setPos(x, y, z)
        self.camera.lookAt(0, 0, 10)  # Always look at the arrow
        
        # Update status text
        direction = self.getCompassDirection(self.cameraOrbitAngle)
        self.cameraPositionText.setText(f"Camera Position: {direction} (Angle: {self.cameraOrbitAngle}°)")
        
    def adjustArrowHeading(self, delta):
        self.arrowHeading += delta
        self.updateArrowOrientation()
        
    def adjustArrowPitch(self, delta):
        self.arrowPitch += delta
        # Limit pitch to prevent gimbal lock issues
        if self.arrowPitch > 89:
            self.arrowPitch = 89
        elif self.arrowPitch < -89:
            self.arrowPitch = -89
        self.updateArrowOrientation()
        
    def updateArrowOrientation(self):
        # Apply rotations to arrow
        self.arrow.setHpr(self.arrowHeading, self.arrowPitch, 0)
        
        # Update status text
        direction = self.getCompassDirection(self.arrowHeading)
        self.arrowDirectionText.setText(f"Arrow Direction: {direction} (Heading: {self.arrowHeading}°, Pitch: {self.arrowPitch}°)")
        
    def getCompassDirection(self, angle):
        # Convert angle to compass direction
        normalized_angle = angle % 360
        if normalized_angle < 0:
            normalized_angle += 360
            
        if 22.5 <= normalized_angle < 67.5:
            return "NE"
        elif 67.5 <= normalized_angle < 112.5:
            return "E"
        elif 112.5 <= normalized_angle < 157.5:
            return "SE"
        elif 157.5 <= normalized_angle < 202.5:
            return "S"
        elif 202.5 <= normalized_angle < 247.5:
            return "SW"
        elif 247.5 <= normalized_angle < 292.5:
            return "W"
        elif 292.5 <= normalized_angle < 337.5:
            return "NW"
        else:
            return "N"
            
    def setupInstructions(self):
        # Create instruction text
        instructions = """
        Camera Controls:
        - Arrow Keys: Orbit camera around the scene
        - Up/Down: Adjust camera height
        - +/-: Zoom in/out
        
        Arrow Controls:
        - A/D: Rotate arrow left/right (heading)
        - W/S: Tilt arrow up/down (pitch)
        """
        
        instructionText = OnscreenText(text=instructions, 
                                       style=1, 
                                       fg=(1, 1, 1, 1), 
                                       bg=(0, 0, 0, 0.7),
                                       pos=(-1.3, 0.9), 
                                       align=TextNode.ALeft, 
                                       scale=.05)
        
        # Create status text displays
        self.cameraPositionText = OnscreenText(text="Camera Position: ", 
                                              style=1, 
                                              fg=(1, 1, 1, 1), 
                                              pos=(0, -0.9), 
                                              align=TextNode.ACenter, 
                                              scale=.05)
        
        self.arrowDirectionText = OnscreenText(text="Arrow Direction: ", 
                                              style=1, 
                                              fg=(1, 1, 1, 1), 
                                              pos=(0, -0.95), 
                                              align=TextNode.ACenter, 
                                              scale=.05)
        
        # Initial update of status texts
        self.updateCameraPosition()
        self.updateArrowOrientation()

# Run the application
app = ArrowScene()
app.run()
