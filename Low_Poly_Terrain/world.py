from panda3d.core import DirectionalLight, AmbientLight, Vec3
from panda3d.bullet import *


class World:
    def __init__(self, base):

        # Load in ShowBase
        self.base = base

        # Create BulletWorld
        self.physics_world = BulletWorld()

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
        skybox = self.base.loader.loadModel('models/skybox/skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(self.base.render)

    def setup_physics(self):
        self.physics_world.setGravity(Vec3(0, 0, -9.81))

    def update(self, task):
        dt = globalClock.getDt()
        self.physics_world.doPhysics(dt)
        return task.cont
