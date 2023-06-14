# This Class Describes The Player Object
from direct.actor.Actor import Actor
from panda3d.core import BitMask32, WindowProperties, NodePath, PandaNode, Vec2
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import ZUp
from GameTest.config.settings import *
import sys

class playerObj:
    def __init__(self, base, physics_world):

        # Load In ShowBase
        self.base = base

        # Load In Physics
        self.pWorld = physics_world

        # Setup Player
        self.setup_player()
        self.sensitivity = SENSITIVITY
        self.setup_controls()

    def setup_player(self):

        # Create Character
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.characterNP = self.base.render.attachNewNode(self.character)
        self.characterNP.setPos(-2, 0, 30)
        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.pWorld.attachCharacter(self.character)

        self.actorNP = Actor('data/assets/models/ralph.egg', {
            'run': 'data/assets/models/ralph-run.egg',
            'walk': 'data/assets/models/ralph-walk.egg',
            'jump': 'data/assets/models/ralph-jump.egg'})
        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.3048)  # 1ft = 0.3048m
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 0, -1)

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.characterNP)
        self.floater.setZ(2.0)

        self.base.camera.setPos(self.characterNP.getX(), self.characterNP.getY() + 50, 10)

    def getPos(self):
        pos = Vec2(self.characterNP.getX(), self.characterNP.getY())
        return pos

    def setKey(self, key, val):
        self.keymap[key] = val

    def setup_controls(self):

        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)

        self.keymap = {"w": False, "a": False, "s": False, "d": False}

        # Key accepts
        self.base.accept("escape", sys.exit)
        self.base.accept("w", self.setKey, ["w", True])
        self.base.accept("w-up", self.setKey, ["w", False])
        self.base.accept("a", self.setKey, ["a", True])
        self.base.accept("a-up", self.setKey, ["a", False])
        self.base.accept("s", self.setKey, ["s", True])
        self.base.accept("s-up", self.setKey, ["s", False])
        self.base.accept("d", self.setKey, ["d", True])
        self.base.accept("d-up", self.setKey, ["d", False])
        self.base.accept("space", self.doJump)

        self.base.cam.reparentTo(self.floater)

    def doJump(self):
        self.character.setMaxJumpHeight(5.0)
        self.character.setJumpSpeed(8.0)
        self.character.doJump()

    def update(self, task):
        # Mouse controls
        mw = self.base.mouseWatcherNode
        if mw.hasMouse():

            x = mw.getMouseX()
            y = mw.getMouseY()

            if not x == 0:
                self.characterNP.setH(self.characterNP.getH() + (-x) * self.sensitivity)

            if self.base.cam.getP() < 90 and self.base.cam.getP() > -90:
                self.base.cam.setP(self.base.cam.getP() + y * self.sensitivity)
            # If the camera is at a -90 or 90 degree angle, this code helps it not get stuck.
            else:
                if self.base.cam.getP() > 90:
                    self.base.cam.setP(self.base.cam.getP() - 1)
                elif self.base.cam.getP() < -90:
                    self.base.cam.setP(self.base.cam.getP() + 1)

            self.base.win.movePointer(0, int(self.base.win.getProperties().getXSize() / 2),
                                      int(self.base.win.getProperties().getYSize() / 2))
        # Mouse controls

        # Keyboard controls
        if self.keymap["w"]:
            self.characterNP.setY(self.characterNP, 3)

        if self.keymap["a"]:
            self.characterNP.setX(self.characterNP, -2)

        if self.keymap["s"]:
            self.characterNP.setY(self.characterNP, -3)

        if self.keymap["d"]:
            self.characterNP.setX(self.characterNP, 2)

        self.base.camera.lookAt(self.floater)

        return task.cont
