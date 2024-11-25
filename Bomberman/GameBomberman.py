#region Imports
"""
@author  Riccardo Delfrate
@license This software is free - https://opensource.org/license/mit
"""

from random import choice, randint, shuffle, random
from actor import Actor, Arena, Point
from GameSettings import GameSettings
from WinDeathGUI import main as win_death_GUI

#endregion Imports

#region Dinamic Actors

class Ballom(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._x = self._x // TILE * TILE
        self._y = self._y // TILE * TILE
        self._w, self._h = TILE, TILE
        self._speed = BALLOMSPEED*GAME_SPEED
        self._dx, self._dy = 0, 0
        
        # Sprite per il movimento verso destra e verso sinistra
        self._sprite_coordinates = {
            'R': [(0, 240), (16, 240), (32, 240)],  # Right
            'L': [(48, 240), (64, 240), (80, 240)],  # Left
        }

        self._current_sprite = 0
        self._frame_counter = 0
        self._spriteDuration = 7*GAME_SPEED  # Sprite duration in frame
        self._moving_direction = None

    def check_collision(self, actor: Actor) -> bool:
        """Check two actors (args) for mutual collision or contact,
        according to bounding-box collision detection.
        Return True if actors collide but False in case they touch, False otherwise."""
        x1, y1, w1, h1 = self.pos() + self.size()
        x2, y2, w2, h2 = actor.pos() + actor.size()
        return (y2 < y1 + h1 and y1 < y2 + h2 and
                x2 < x1 + w1 and x1 < x2 + w2)

    def detect_collision(self, dx: int, dy: int, arena: Arena) -> bool:
        """Check if proposed movement (dx, dy) would cause a collision with a Wall."""
        original_x, original_y = self._x, self._y

        # Try temporary movement
        self._x += dx
        self._y += dy

        # Check for collision with walls
        for actor in arena.actors():
            if (isinstance(actor, Wall) or isinstance(actor, Bomb)) and self.check_collision(actor):
                # Reset position if collision occurs
                self._x, self._y = original_x, original_y
                return True  # Collision found

        # Reset position
        self._x, self._y = original_x, original_y
        return False  # No collision

    def move(self, arena: Arena):
        if self._x % TILE == 0 and self._y % TILE == 0:
            possible_directions = [(0, -self._speed), (self._speed, 0), (0, self._speed), (-self._speed, 0)]
            shuffle(possible_directions)
            for direction in possible_directions:
                dx, dy = direction
                if not self.detect_collision(dx, dy, arena):
                    self._dx, self._dy = dx, dy
                    self._moving_direction = 'R' if dx > 0 else 'L'  # Determine movement direction
                    break

        self._x += self._dx
        self._y += self._dy

    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

    def sprite(self) -> Point:
        self._frame_counter += 1

        if self._moving_direction is None:
            return (0, 240)

        if self._frame_counter >= self._spriteDuration:
            self._frame_counter = 0
            self._current_sprite = (self._current_sprite + 1) % len(self._sprite_coordinates[self._moving_direction])

        return self._sprite_coordinates[self._moving_direction][self._current_sprite]

class Bomberman(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._dx, self._dy = 0, 0
        self._w, self._h = TILE, TILE
        self._speed = PLAYERSPEED*GAME_SPEED
        self._sprite_coordinates = {
            'U': [(48, 16), (64, 16), (80, 16)],  # Sprite movement "up"
            'D': [(48, 0), (64, 0), (80, 0)],  # Sprite movement "down"
            'L': [(0, 0), (16, 0), (32, 0)],  # Sprite movement "left"
            'R': [(0, 16), (16, 16), (32, 16)],   # Sprite movement "right"
            'Death' : [(0, 32), (32, 32), (48, 32), (64, 32), (80, 32), (96, 32), (96, 16)] # Sprite death
        }
        self._static_sprite = (64, 0)
        self._moving = None 
        self._current_sprite = 0 
        self._frame_counter = 0 
        self._spriteDuration = 3/GAME_SPEED  # Sprite duration in frame
        
        self._hasDied = False
        
        self._bomb_spawned = False
        
    def detect_collision(self, dx: int, dy: int, arena: Arena) -> bool:
        """Check if proposed movement (dx, dy) would cause a collision with a Wall.
        Return True if there is a collision, False otherwise."""
        
        # backup current position
        original_x, original_y = self._x, self._y

        # try temporary movement
        self._x += dx
        self._y += dy

        # check for collision
        for actor in arena.actors():
            if isinstance(actor, Wall) and self.check_collision(actor):
                # reset position
                self._x, self._y = original_x, original_y
                return True  # collision found

        # reset position
        self._x, self._y = original_x, original_y
        return False  # no collision
    
    def detect_ballom_collision(self, arena: Arena) -> bool:
        """Check if there is a collision with a Ballom.
        Return True if there is a collision, False otherwise."""
        
        # check for collision
        for actor in arena.actors():
            if isinstance(actor, Ballom) and self.check_collision(actor):
                return True  # collision found

        return False  # no collision
    
    def detect_win(self, arena: Arena) -> bool:
        """Check if there is a collision with a Door (only overlapping).
        Return True if there is a collision, False otherwise."""
        
        # check for collision
        for actor in arena.actors():
            if isinstance(actor, Door) and self.check_collision(actor):
                return True  # collision found

        return False  # no collision
    
    def check_collision(self, actor: Actor) -> bool:
        """Check two actors (args) for mutual collision or contact,
        according to bounding-box collision detection.
        Return True if actors collide but False in case they touch, False otherwise.
        """
        x1, y1, w1, h1 = self.pos() + self.size()
        x2, y2, w2, h2 = actor.pos() + actor.size()
        return (y2 < y1 + h1 and y1 < y2 + h2 and
                x2 < x1 + w1 and x1 < x2 + w2)

    def move(self, arena: Arena):
        if self._x % TILE == 0 and self._y % TILE == 0:
            self._dx, self._dy = 0, 0
            keys = arena.current_keys()
            if "w" in keys:
                if not self.detect_collision(0, -self._speed, arena):
                    self._dy = -self._speed
                    self._moving = "U"
            elif "s" in keys:
                if not self.detect_collision(0, self._speed, arena):
                    self._dy = self._speed
                    self._moving = "D"
            elif "a" in keys:
                if not self.detect_collision(-self._speed, 0, arena):
                    self._dx = -self._speed
                    self._moving = "L"
            elif "d" in keys:
                if not self.detect_collision(self._speed, 0, arena):
                    self._dx = self._speed
                    self._moving = "R"
            elif "x" in keys and not self._bomb_spawned:
                arena.spawn(Bomb(self.pos(), self), below=True)
                self._bomb_spawned = True  # Mark that a bomb has been spawned

            else:
                self._moving = None
        
        if not self._hasDied:
            self._x += self._dx
            self._y += self._dy
            
        if self.detect_win(arena):
            arena.kill(self)
            win_death_GUI("WIN")
                    
    def bomb_destroyed(self):
        """Call this method when the bomb is destroyed (or timed out) to reset the flag."""
        self._bomb_spawned = False

    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

    def sprite(self) -> Point:
        if not self._hasDied and self.detect_ballom_collision(arena):
            self._hasDied = True
            self._dx, self._dy = 0, 0
            self._moving = None
        
        if self._hasDied:
            death_sprites = self._sprite_coordinates.get('Death', [])
            
            if self._current_sprite < len(death_sprites) - 1:
                self._frame_counter += 1
                if self._frame_counter >= self._spriteDuration:
                    self._frame_counter = 0
                    self._current_sprite += 1
            if self._current_sprite >= len(death_sprites) - 1:
                arena.kill(self)
                win_death_GUI("DEATH")
            return death_sprites[self._current_sprite]
            

        if self._moving not in self._sprite_coordinates:
            self._frame_counter = 0  # Reset counter when character is not moving
            return self._static_sprite

        self._frame_counter += 1

        # Change sprite after reaching specified duration 
        if self._frame_counter >= self._spriteDuration:
            self._frame_counter = 0
            self._current_sprite = (self._current_sprite + 1) % len(self._sprite_coordinates[self._moving])

        return self._sprite_coordinates[self._moving][self._current_sprite]

#endregion Dinamic Actors

#region Static Actors

class Wall(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._w, self._h = TILE, TILE

        self._sprite_coordinates = [
            (64, 48), (80, 48), (96, 48), (112, 48), (128, 48), (144, 48), (160, 48)
        ]
        self._current_sprite = 0
        self._frame_counter = 0
        self._spriteDuration = 2/GAME_SPEED  # Sprite duration in frame
        self._hasBeenDestroyed = False

    def move(self, arena: Arena):
        return

    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

    def sprite(self) -> Point:
        if not self._hasBeenDestroyed:
            return self._sprite_coordinates[0]

        self._frame_counter += 1

        if self._frame_counter >= self._spriteDuration:
            self._frame_counter = 0
            if self._current_sprite < len(self._sprite_coordinates) - 1:
                self._current_sprite += 1
            else:
                # animation ended so Wall is removed from arena
                arena.kill(self)
        
        return self._sprite_coordinates[self._current_sprite]

class BorderWall(Wall):
    def sprite(self) -> Point:
        return 48, 48
    
class Door(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._w, self._h = TILE, TILE

        self._door_sprite_coordinates = (176, 48)

    def move(self, arena: Arena):
        return

    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

    def sprite(self) -> Point:
        return self._door_sprite_coordinates

class Bomb(Actor):
    def __init__(self, pos, bomberman: Bomberman, explosion_range=1):
        self._x, self._y = pos
        self._w, self._h = TILE, TILE
        self._explosion_range = explosion_range
        self._bomberman = bomberman

        self._sprite_coordinates = [
            (16, 48), (0, 48), (32, 48), (16, 48), (0, 48), (32, 48)
        ]
        self._current_sprite = 0
        self._frame_counter = 0
        self._spriteDuration = 11/GAME_SPEED  # Sprite duration in frame
        self._bombDuration = 100/GAME_SPEED  # Bomb ticking time

    def move(self, arena: Arena):
        return

    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

    def sprite(self) -> Point:
        self._frame_counter += 1

        # Cambia sprite in base al tempo trascorso
        if self._frame_counter >= self._spriteDuration:
            self._frame_counter = 0
            self._current_sprite = (self._current_sprite + 1) % len(self._sprite_coordinates)

        # Decrementa il timer della bomba
        self._bombDuration -= 1
        if self._bombDuration <= 0:
            self.explode(arena)
            arena.kill(self)
            self._bomberman.bomb_destroyed()

        return self._sprite_coordinates[self._current_sprite]
    
    def explode(self, arena: Arena):
        """Generates Fire in every direction and destroys blocks and kills enemies."""
        directions = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}
        
        # Create center Fire
        arena.spawn(Fire((self._x, self._y), None, 1))
        
        for direction, (dx, dy) in directions.items():
            for length in range(1, self._explosion_range + 1):
                fx, fy = self._x + dx * TILE * length, self._y + dy * TILE * length
                
                # Flag to indicate whether fire generation should continue
                can_generate_fire = True

                for actor in arena.actors():
                    if isinstance(actor, Wall) and actor.pos() == (fx, fy):
                        if isinstance(actor, BorderWall):
                            # Stop fire if the wall is unbreakable
                            can_generate_fire = False
                            break
                        else:
                            # Destroy Wall and create fire on its position
                            arena.kill(actor)
                            arena.spawn(Fire((fx, fy), direction=direction, length=1))
                            can_generate_fire = False
                            break
                
                if not can_generate_fire:
                    break  # Stop further fire in this direction

                # Generate fire if no walls block the path
                is_end = length == self._explosion_range
                arena.spawn(Fire((fx, fy), direction=direction, length=1 if is_end else 2))

    
class Fire(Actor):
    def __init__(self, pos, direction, length):
        """
        Initialize the fire class.
        :param pos: The position where the fire starts.
        :param direction: The direction of the fire ('U', 'D', 'L', 'R', or None for center).
        :param length: The length of the fire in the specified direction.
        """
        self._x, self._y = pos
        self._direction = direction if direction else 'center'
        self._length = length
        self._w, self._h = TILE, TILE

        self._sprite_coordinates = {
            'center': [(32, 96), (112, 96), (32, 176), (112, 176)],
            'vertical': [(32, 80), (112, 80), (32, 160), (112, 160)],
            'horizontal': [(48, 96), (128, 96), (48, 176), (128, 176)],
            'end_up': [(32, 64), (112, 64), (32, 144), (112, 144)],
            'end_down': [(32, 128), (112, 128), (32, 208), (112, 208)],
            'end_left': [(0, 96), (80, 96), (0, 176), (80, 176)],
            'end_right': [(64, 96), (144, 96), (64, 176), (144, 176)],
        }

        self._current_sprite = 0
        self._frame_counter = 0
        self._spriteDuration = 2/GAME_SPEED  # Duration of each sprite in frame
        self._expired = False  # Determines if the fire animation has ended

    def move(self, arena: Arena):
        """
        Handles the fire's logic during its lifecycle.
        Checks if the fire should destroy walls or other actors.
        """
        if self._expired:
            arena.kill(self)  # Remove the fire from the arena
            return

        # Check for collisions with actors
        for actor in arena.actors():
            if self.check_collision(actor):
                if isinstance(actor, Wall) and not isinstance(actor, BorderWall):
                    actor._hasBeenDestroyed = True  # Mark wall for destruction
                elif isinstance(actor, Ballom):
                    arena.kill(actor)  # Destroy the Ballom
                elif isinstance(actor, Bomberman):
                    actor._hasDied = True  # Mark the Bomberman as dead

    def check_collision(self, actor: Actor) -> bool:
        """
        Check if the fire collides with another actor.
        :param actor: The actor to check collision against.
        :return: True if there is a collision, False otherwise.
        """
        x1, y1, w1, h1 = self.pos() + self.size()
        x2, y2, w2, h2 = actor.pos() + actor.size()
        return (y2 < y1 + h1 and y1 < y2 + h2 and
                x2 < x1 + w1 and x1 < x2 + w2)

    def pos(self) -> Point:
        """Returns the position of the fire."""
        return self._x, self._y

    def size(self) -> Point:
        """Returns the size of the fire."""
        return self._w, self._h

    def sprite(self) -> Point:
        """
        Determines the current sprite of the fire based on its state and direction.
        """
        self._frame_counter += 1

        # Change sprite frame after reaching the duration
        if self._frame_counter >= self._spriteDuration:
            self._frame_counter = 0
            self._current_sprite += 1

            # Check if the animation has finished
            if self._current_sprite >= len(self._sprite_coordinates['center']):
                self._expired = True
                return (64, 128)  # Default sprite for expired fire

        # Map the direction to the appropriate sprite set
        sprites_key = {
            'center': 'center',
            'U': 'end_up' if self._length == 1 else 'vertical',
            'D': 'end_down' if self._length == 1 else 'vertical',
            'L': 'end_left' if self._length == 1 else 'horizontal',
            'R': 'end_right' if self._length == 1 else 'horizontal',
        }.get(self._direction, 'center')

        return self._sprite_coordinates[sprites_key][self._current_sprite]

    
#endregion Static Actors

#region Game Setup

def tick():
    g2d.clear_canvas()
    g2d.set_color((59, 123, 1))
    g2d.draw_rect((0,0),arena.size())

    img = "bomberman.png"
    for a in arena.actors():
        g2d.draw_image(img, a.pos(), a.sprite(), a.size())

    arena.tick(g2d.current_keys())  # Game logic


def main(sett : GameSettings):
    global g2d, arena, settings
    global TILE, BALLOMSPEED, BALLOM_MULTIPLIER, WALLS_PERCENTAGE, PLAYERSPEED, MUTE_MUSIC, VOLUME, GAME_SPEED, mapWidth, mapHeight
    
    import g2d  # game classes do not depend on g2d
    
    settings = sett
    
    #region Game Settings

    TILE = 16
    BALLOMSPEED = settings.BALLOMSPEED
    PLAYERSPEED = settings.PLAYERSPEED
    BALLOM_MULTIPLIER = settings.BALLOM_MULTIPLIER
    WALLS_PERCENTAGE = settings.WALLS_PERCENTAGE

    MUTE_MUSIC = settings.MUTE_MUSIC
    VOLUME = settings.VOLUME

    GAME_SPEED = settings.GAME_SPEED

    # Standard Bomberman map size is 15 x 13
    mapWidth = settings.MAP_WIDTH
    mapHeight = settings.MAP_HEIGHT

    nBalloms = int(((((mapWidth-1) * (mapHeight-1))/2) - (((((mapWidth-1) * (mapHeight-1))/2)/100)*WALLS_PERCENTAGE))/15*BALLOM_MULTIPLIER)

    #endregion Game Settings

    settings = sett
    arena = Arena((TILE*mapWidth, TILE*mapHeight))

    mapGrid = [
            [
                (riga * 16, colonna * 16) for riga in range(mapWidth)
            ]
            for colonna in range(mapHeight)
        ]
    
    
    borders = [
        (riga * 16, colonna * 16)
        for riga in range(mapWidth)
        for colonna in range(mapHeight)
        #-----------GENERATE BORDERS----------#
        if (riga == 0 or riga == mapWidth - 1 or colonna == 0 or colonna == mapHeight - 1)
        #---------GENERATE INNER GRID---------#
        or (riga%2 == 0 and colonna%2 == 0)
    ]
    

    '''for brd in borders:
        arena.spawn(BorderWall(brd))'''

    for i in range(mapHeight):
        for j in range(mapWidth):
            for brd in borders:
                if mapGrid[i][j] == brd:
                    mapGrid[i][j] = BorderWall(mapGrid[i][j])
                #-----------SPAWN TEST BALLOM-----------#
                '''elif mapGrid[i][j]==(16,16):
                    mapGrid[i][j] = Ballom(mapGrid[i][j])'''
                
    #emptyCells = sum(list(map(lambda x: not isinstance(x, tuple), mapGrid)))
    
    # SPAWN RANDOM WALLS
    for i in range(mapHeight):
        for j in range(mapWidth):
            if isinstance(mapGrid[i][j], tuple) and random() < WALLS_PERCENTAGE / 100:
                # Keep corners empty
                if (mapGrid[i][j] != (16, 16) and mapGrid[i][j] != (32, 16) and mapGrid[i][j] != (16, 32)) and \
                (mapGrid[i][j] != (mapWidth * 16 - 32, mapHeight * 16 - 32) and mapGrid[i][j] != (mapWidth * 16 - 48, mapHeight * 16 - 32) and mapGrid[i][j] != (mapWidth * 16 - 32, mapHeight * 16 - 48)) and \
                (mapGrid[i][j] != (16, mapHeight * 16 - 32) and mapGrid[i][j] != (32, mapHeight * 16 - 32) and mapGrid[i][j] != (16, mapHeight * 16 - 48)) and \
                (mapGrid[i][j] != (mapWidth * 16 - 32, 16) and mapGrid[i][j] != (mapWidth * 16 - 48, 16) and mapGrid[i][j] != (mapWidth * 16 - 32, 32)):
                    # Add Wall
                    mapGrid[i][j] = Wall(mapGrid[i][j])
                    
    # SPAWN DOOR IN RANDOM POSITION
    wall_positions = [(i, j) for i in range(mapHeight) for j in range(mapWidth) if isinstance(mapGrid[i][j], Wall) and not isinstance(mapGrid[i][j], BorderWall)]
    
    if wall_positions:
        i, j = choice(wall_positions)
        mapGrid[i][j] = Door(mapGrid[i][j].pos())
    
    #COUNT EMPTY SPACES
    emptySpaces = 0
    for i in range(mapHeight):
        for j in range(mapWidth):
            if isinstance(mapGrid[i][j], tuple):
                if (mapGrid[i][j] != (16,16) and mapGrid[i][j] != (32,16) and mapGrid[i][j] != (16,32)) and (mapGrid[i][j] != (mapWidth*16-32,mapHeight*16-32) and mapGrid[i][j] != (mapWidth*16-48,mapHeight*16-32) and mapGrid[i][j] != (mapWidth*16-32,mapHeight*16-48)) and (mapGrid[i][j] != (16,mapHeight*16-32) and mapGrid[i][j] != (32,mapHeight*16-32) and mapGrid[i][j] != (16,mapHeight*16-48)) and (mapGrid[i][j] != (mapWidth*16-32,16) and mapGrid[i][j] != (mapWidth*16-48,16) and mapGrid[i][j] != (mapWidth*16-32,32)):
                    emptySpaces+=1
    
    #GENERATE BALLOM SPAWN LIST
    ballomSpawnList = [True] * nBalloms + [False] * (emptySpaces - nBalloms)
    shuffle(ballomSpawnList)

    # Seleziona casualmente un elemento e rimuovilo dalla lista
    random_index = randint(0, len(ballomSpawnList) - 1)
    
    #SPAWN RANDOM BALLOMS
    for i in range(mapHeight):
        for j in range(mapWidth):
            if isinstance(mapGrid[i][j], tuple):
                # keep corners empty
                if (mapGrid[i][j] != (16,16) and mapGrid[i][j] != (32,16) and mapGrid[i][j] != (16,32)) and (mapGrid[i][j] != (mapWidth*16-32,mapHeight*16-32) and mapGrid[i][j] != (mapWidth*16-48,mapHeight*16-32) and mapGrid[i][j] != (mapWidth*16-32,mapHeight*16-48)) and (mapGrid[i][j] != (16,mapHeight*16-32) and mapGrid[i][j] != (32,mapHeight*16-32) and mapGrid[i][j] != (16,mapHeight*16-48)) and (mapGrid[i][j] != (mapWidth*16-32,16) and mapGrid[i][j] != (mapWidth*16-48,16) and mapGrid[i][j] != (mapWidth*16-32,32)):
                    # add Ballom
                    random_index = randint(0, len(ballomSpawnList) - 1)
                    spawnBallom = ballomSpawnList.pop(random_index)
                    if spawnBallom:
                        mapGrid[i][j] = Ballom(mapGrid[i][j])
    
    for i in range(mapHeight):
        for j in range(mapWidth):
            if not isinstance(mapGrid[i][j], tuple):
                arena.spawn(mapGrid[i][j])
                if isinstance(mapGrid[i][j], Door):
                    arena.spawn(Wall(mapGrid[i][j].pos()))

    #arena.spawn(Bomb((16, 32)))
    arena.spawn(Bomberman((16, 16)))

    g2d.init_canvas(arena.size(), scale=settings.WINDOW_SCALE)
    g2d.main_loop(tick)

'''if __name__ == "__main__":
    main()'''
    
#endregion Game Setup