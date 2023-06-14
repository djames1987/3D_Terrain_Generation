from panda3d.core import loadPrcFile
loadPrcFile('config/conf.prc')
from util.TerrainEngine import *
from config.settings import *
from lib.WorldObj import *
from lib.PlayerObj import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import floor

PLAYER_MOVE_THRESHOLD = 10.0

class MyGame(ShowBase):
    def __init__(self):
        super().__init__(self)

        # Get World Object
        self.world = WorldObj(self)

        # Get PlayerObj
        self.player = playerObj(self, self.world.pWorld)

        # Player Pos
        self.player_pos = Vec2(floor(self.camera.getPos().x), floor(self.camera.getPos().y))

        # Update Chunk Switch
        self.updateChunks = True

        # Start Terrain Manager
        self.tm = TerrainManager(self, self.player_pos, self.world.pWorld)

        # Create Task Chains
        self.taskMgr.setupTaskChain('update_core', numThreads=1)
        self.taskMgr.setupTaskChain('update_terrain', numThreads=2)

        # Run Tasks
        self.taskMgr.add(self.update, 'update', taskChain='update_core')
        self.taskMgr.add(self.terrain_update, 'terrain_update', taskChain='update_terrain')
        self.taskMgr.add(self.player.update, 'player_update', taskChain='update_core')

        # Enable WireFrame Render
        #self.render.setRenderModeWireframe()

    def update(self, task):
        dt = globalClock.getDt()
        self.world.pWorld.doPhysics(dt)

        new_player_pos = Vec2(floor(self.camera.getPos().x), floor(self.camera.getPos().y))

        if (new_player_pos - self.player_pos).length() > PLAYER_MOVE_THRESHOLD:
            self.updateChunks = True
            self.player_pos = new_player_pos

        self.tm.playerPos = self.player_pos
        self.tm.set_players_current_chunk()
        self.tm.update_live_buffered_chunks_list()

        return task.cont

    def terrain_update(self, task):

        if self.updateChunks:
            self.tm.update_chunks()
            self.updateChunks = False
        else:
            return task.cont

        return task.cont


App = MyGame()
App.run()

