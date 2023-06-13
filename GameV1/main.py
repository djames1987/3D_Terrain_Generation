from util.TerrainManager import *
from config.settings import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import floor


class MyGame(ShowBase):
    def __init__(self):
        super().__init__(self)

        # Player Pos
        self.player_pos = Vec2(floor(self.camera.getPos().x), floor(self.camera.getPos().y))

        # Update Chunk Switch
        self.updateChunks = True

        # Start Terrain Manager
        self.tm = TerrainManager(self, self.player_pos)

        # Create Task Chains
        self.taskMgr.setupTaskChain('update_core', numThreads=1)
        self.taskMgr.setupTaskChain('update_terrain', numThreads=2)

        # Run Tasks
        self.taskMgr.add(self.update, 'update', taskChain='update_core')
        self.taskMgr.add(self.terrain_update, 'terrain_update', taskChain='update_terrain')

        # Render Node
        #self.tm.loadedChunks.reparentTo(self.render)

        self.render.setRenderModeWireframe()

    def update(self, task):
        self.tm.playerPos = Vec2(floor(self.camera.getPos().x), floor(self.camera.getPos().y))
        self.tm.set_players_current_chunk()
        self.tm.update_live_buffered_chunks_list()

        return task.cont

    def terrain_update(self, task):

        if self.updateChunks:
            self.tm.update_chunks()
            #self.updateChunks = False
        else:
            return task.cont

        return task.cont


App = MyGame()
App.run()


