from terrain_matrix import *
from terrain import *
from player import *
from world import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *


class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        #self.render.setRenderModeWireframe()

        # Load in World Settings
        self.world = World(self)

        # Load in terrain
        self.terrain = TerrainManager(self, self.world.physics_world)
        #self.terrain.render_terrain()
        self.terrain.test_load()

        # Load in player
        self.player = Player(self, self.world.physics_world)

        taskMgr.add(self.world.update, 'update')
        taskMgr.add(self.player.update, 'player_update')




app = MyGame()
app.run()
