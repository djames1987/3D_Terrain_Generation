from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask, ClockObject
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import random
import sys
import os
import math
from panda3d.physics import *
from terrain_matrix import *

class Ralph:
    def __init__(self, base, matrix):
        self.matrix = matrix
        self.base = base
        # This is used to store which keys are currently pressed.
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "cam-left": 0, "cam-right": 0}

        # Create the main character, Ralph

        self.ralph = Actor("models/ralph",
                           {"run": "models/ralph-run",
                            "walk": "models/ralph-walk"})
        self.ralph.reparentTo(self.base.render)
        self.ralph.setScale(.2)
        self.ralph.setPos(0, 0, 25)
        node = NodePath("PhysicsNode")
        node.reparentTo(self.base.render)
        an = ActorNode("Ralph")
        anp = node.attachNewNode(an)
        self.base.physicsMgr.attachPhysicalNode(an)
        self.ralph.reparentTo(anp)
        gravityFN = ForceNode('world-forces')
        gravityFNP = self.base.render.attachNewNode(gravityFN)
        gravityForce = LinearVectorForce(0, 0, -9.81)  # gravity acceleration
        gravityFN.addForce(gravityForce)
        self.base.physicsMgr.addLinearForce(gravityForce)

        self.base.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0, 0, 9)
        self.ralphGroundRay.setDirection(0, 0, -1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.ralphGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.base.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)




        # Create a floater object, which floats 2 units above ralph.  We
        # use this as a target for the camera to look at.

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.ralph)
        self.floater.setZ(5.0)

        # Accept the control keys for movement and rotation

        self.base.accept("escape", sys.exit)
        self.base.accept("arrow_left", self.setKey, ["left", True])
        self.base.accept("arrow_right", self.setKey, ["right", True])
        self.base.accept("arrow_up", self.setKey, ["forward", True])
        self.base.accept("a", self.setKey, ["cam-left", True])
        self.base.accept("s", self.setKey, ["cam-right", True])
        self.base.accept("arrow_left-up", self.setKey, ["left", False])
        self.base.accept("arrow_right-up", self.setKey, ["right", False])
        self.base.accept("arrow_up-up", self.setKey, ["forward", False])
        self.base.accept("a-up", self.setKey, ["cam-left", False])
        self.base.accept("s-up", self.setKey, ["cam-right", False])

        self.base.taskMgr.add(self.move, "moveTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera
        self.base.disableMouse()
        self.base.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 10)


    # Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value

        # Accepts arrow keys to move either the player or the menu cursor,
        # Also deals with grid checking and collision detection

    def move(self, task):

        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        ClockObject.getGlobalClock()
        dt = globalClock.getDt()
        self.base.cTrav.traverse(self.base.render)

        if self.ralphGroundHandler.getNumEntries() > 0:
            self.ralphGroundHandler.sortEntries()  # This is to ensure the closest collision is first
            groundEntry = self.ralphGroundHandler.getEntry(0)
            pos = groundEntry.getSurfacePoint(self.base.render)
            self.ralph.setZ(pos.getZ())



        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        if self.keyMap["cam-left"]:
            self.base.camera.setX(self.base.camera, -20 * dt)
        if self.keyMap["cam-right"]:
            self.base.camera.setX(self.base.camera, +20 * dt)

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.

        if self.keyMap["left"]:
            self.ralph.setH(self.ralph.getH() + 300 * dt)
        if self.keyMap["right"]:
            self.ralph.setH(self.ralph.getH() - 300 * dt)
        if self.keyMap["forward"]:
            self.ralph.setY(self.ralph, -300 * dt)
            print(self.ralph.getPos())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if self.keyMap["forward"] or self.keyMap["left"] or self.keyMap["right"]:
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk", 5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - self.base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.base.camera.setPos(self.base.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.base.camera.setPos(self.base.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        self.base.camera.setZ(self.ralph.getZ() + 2.0)

        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        self.base.camera.lookAt(self.floater)

        entries = list(self.ralphGroundHandler.entries)
        entries.sort(key=lambda x: x.getSurfacePoint(self.base.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().name == "terrain":
            self.ralph.setZ(entries[0].getSurfacePoint(self.base.render).getZ())
        else:
            self.ralph.setPos(startpos)


        return task.cont