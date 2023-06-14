# The Terrain Manager Is Used To Control The Spawning Of Terrain Around The Player
from GameTest.config.settings import *
from GameTest.lib.ChunkObj import *
from panda3d.core import Vec2, NodePath


class TerrainManager:
    def __init__(self, base, player_pos, world_physics):

        # Load In ShowBase from Main
        self.base = base

        # Load In Physics
        self.pWorld = world_physics

        # Current Player Position
        self.playerPos = Vec2(player_pos.x, player_pos.y)

        # Current Chunk Player Is In
        self.playerChunk = Vec2(0, 0)

        # List Of Chunks In Range
        self.chunksInRange = []

        # Live List Of Chunks In Range
        self.liveChunksInRange = []

        # List Of Chunks In Buffer Range
        self.chunksInBufferRange = []

        # Live List Of Chunks In Buffer Range
        self.liveChunksInBufferRange = []

        # NodePath For Loaded Chunks
        self.loadedChunks = NodePath('loadedChunks')

        # Node For Buffered Chunks
        self.bufferedChunks = NodePath('bufferedChunks')

        if self.loadedChunks:
            self.loadedChunks.reparentTo(self.base.render)

    def set_players_current_chunk(self):
        x = self.playerPos.x // CHUNKSIZE
        y = self.playerPos.y // CHUNKSIZE

        self.playerChunk = Vec2(x, y)

    def update_live_chunks(self):
        x = self.playerChunk.x
        y = self.playerChunk.y

        chunkList = [(x-2, y+2),(x-1, y+2),(x, y+2),(x+1, y+2),(x+2, y+2),
                    (x-2, y+1),(x-1, y+1),(x, y+1),(x+1, y+1),(x+2, y+1),
                    (x-2, y),(x-1, y),(x, y),(x+1, y),(x+2, y),
                    (x-2, y-1),(x-1, y-1),(x, y-1),(x+1, y-1),(x+2, y-1),
                    (x-2, y-2),(x-1, y-2),(x, y-2),(x+1, y-2),(x+2, y-2)]

        return chunkList

    def update_live_buffered_chunks_list(self):
        x = self.playerChunk.x
        y = self.playerChunk.y

        bufferedChunks = [(x-4, y+4),(x-3, y+4),(x-2, y+4),(x-1, y+4),(x, y+4),(x+1, y+4),(x+2, y+4),(x+3, y+4),(x+4, y+4),
                        (x-4, y+3),(x-3, y+3),(x-2, y+3),(x-1, y+3),(x, y+3),(x+1, y+3),(x+2, y+3),(x+3, y+3),(x+4, y+3),
                        (x-4, y+2),(x+4, y+2),(x-4, y+1),(x+4, y+1),(x-4, y),(x+4, y),(x-4, y-1),(x+4, y-1),(x-4, y-2),(x+4, y-2),
                        (x-4, y-3),(x-3, y-3),(x-2, y-3),(x-1, y-3),(x, y-3),(x+1, y-3),(x+2, y-3),(x+3, y-3),(x+4, y-3),
                        (x-4, y-4),(x-3, y-4),(x-2, y-4),(x-1, y-4),(x, y-4),(x+1, y-4),(x+2, y-4),(x+3, y-4),(x+4, y-4)]

        return bufferedChunks

    def load_chunk(self, x, y):
        pos = Vec2(x, y)
        chunk = ChunkObj(self.base, pos, self.pWorld)
        chunk.chunk.reparentTo(self.loadedChunks)
        self.pWorld.attachRigidBody(chunk.chunk_collision)

    def buffer_chunk(self, chunk):
        chunk.chunk.reparentTo(self.bufferedChunks)

    def unload_chunk(self, chunk):
        chunk.chunk.removeNode()
        #self.pWorld.removeRigidBody(chunk.chunk_collision)
        del chunk

    def update_chunks(self):
        # Update the current player chunk
        self.set_players_current_chunk()

        # Update the list of live chunks and buffered chunks
        new_live_chunks = self.update_live_chunks()
        new_buffered_chunks = self.update_live_buffered_chunks_list()

        # Convert ChunkObj's to tuples for comparison
        current_live_chunks = [chunk.chunkPos for chunk in self.chunksInRange]
        current_buffered_chunks = [chunk.chunkPos for chunk in self.chunksInBufferRange]

        # Find the chunks that are no longer in the live range, move them to the buffer
        for chunk in self.chunksInRange:
            if chunk.chunkPos not in new_live_chunks:
                self.buffer_chunk(chunk)
                self.chunksInBufferRange.append(chunk)
                self.chunksInRange.remove(chunk)

        # Find the chunks that are no longer in the buffer range, unload them
        for chunk in self.chunksInBufferRange:
            if chunk.chunkPos not in new_buffered_chunks:
                self.unload_chunk(chunk)
                self.chunksInBufferRange.remove(chunk)

        # Find the buffered chunks that are now in the live range, move them to the live chunks
        for chunk in self.chunksInBufferRange:
            if chunk.chunkPos in new_live_chunks:
                self.load_chunk(chunk.chunkPos.x, chunk.chunkPos.y)
                self.chunksInRange.append(chunk)
                self.chunksInBufferRange.remove(chunk)

        # Load in any new chunks in the live range
        for pos in new_live_chunks:
            if pos not in current_live_chunks:
                self.load_chunk(pos[0], pos[1])
                self.chunksInRange.append(ChunkObj(self.base, Vec2(pos[0], pos[1]), self.pWorld))

        # Buffer any new chunks in the buffer range
        for pos in new_buffered_chunks:
            if pos not in current_buffered_chunks:
                self.buffer_chunk(ChunkObj(self.base, Vec2(pos[0], pos[1]), self.pWorld))
                self.chunksInBufferRange.append(ChunkObj(self.base, Vec2(pos[0], pos[1]), self.pWorld))

    def update_live_lists(self):
        self.update_live_chunks()
        self.update_live_buffered_chunks_list()