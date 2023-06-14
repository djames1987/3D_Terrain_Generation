# This Class Defines The World Obj Of The Current World The PLayer Is In
from panda3d.core import AmbientLight, DirectionalLight, Vec3
from panda3d.bullet import *

class WorldObj:
    def __init__(self, base, name='OverWorld', skybox='skybox.egg'):

        # Load In ShowBase
        self.base = base

        # Name Of The Current World
        self.name = name

        # Setup Physics
        self.pWorld = BulletWorld()
        self.pWorld.setGravity(0, 0, -9.81)

        # Physics Debug
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(False)
        debugNode.showNormals(False)
        debugNP = self.base.render.attachNewNode(debugNode)
        debugNP.show()

        self.pWorld.setDebugNode(debugNP.node())

        # Setup Lights
        self.setup_lights()

        # Setup SkyBox
        self.skybox = skybox
        self.setup_skybox()

    def setup_lights(self):
        mainLight = DirectionalLight('main light')
        mainLightNodePath = self.base.render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(30, -60, 0)
        self.base.render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNodePath = self.base.render.attachNewNode(ambientLight)
        self.base.render.setLight(ambientLightNodePath)

    def setup_skybox(self):
        skybox = self.base.loader.loadModel(f'data/assets/skybox/{self.skybox}')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(self.base.render)
