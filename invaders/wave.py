"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

Luke Griffiths lsg84
Oana Mirestean oam34
12 December 2019
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class are to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    #Attribute _direction: specifies the direction in which the aliens are traveling
    #Invariant: _direction is an int >= -2 and int<= 2
    #
    #Attribute _steps: the randomized number of steps the aliens take before shooting
    #Invariant: _steps is an int >= 1 and int <= BOLT_RATE
    #
    #Attribute _blast1: the sound for when an alien is destroyed
    #Invariant: _blast1 is a .wav file
    #
    #Attribute _blast2: the sound for when an ship is destroyed
    #Invariant: _blast2 is a .wav file
    #
    #Attribute _pew1: the sound for when an ship blast is fired
    #Invariant: _pew1 is a .wav file
    #
    #Attribute _pew2: the sound for when an alien blast is fired
    #Invariant: _pew2 is a .wav file
    #
    #Attribute _rogue: an alien object that is a rogue
    #Invariant: _rogue is a GObject

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getLives(self):
        return self._lives

    def setLives(self, decrease):
        self._lives = self._lives - decrease

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializes the ship, aliens, bolts, and dline.
        """
        self._ship = Ship(x = GAME_WIDTH//2, y = SHIP_BOTTOM+SHIP_HEIGHT//2,
        source = 'ship.png')
        self._aliens = []
        self.draw_table()
        self._direction = 1
        self._time = 0
        self._steps = random.randint(1,BOLT_RATE)
        self._dline = GPath(points = [0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
        linewidth = 1,linecolor = 'gray')
        self._bolts = []
        self._blast1 = Sound('blast1.wav')
        self._pew1 = Sound('pew1.wav')
        self._blast2 = Sound('blast2.wav')
        self._pew2 = Sound('pew2.wav')
        self._lives = 3


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,input,dt):
        """
        Update method for everything in Wave.
        """
        self.ship_update(input)
        self.bolt_update(input)
        self.collision()
        self.shipcollision()
        if not self.player_won():
            if self._time > ALIEN_SPEED:
                self.alien_update()
                self._time = 0
                if self._steps == 0:
                    alien = self.random_alien()
                    self._bolts.append(Bolt(x = alien.x, y = alien.y,
                    vel = -BOLT_SPEED))
                    self._pew2.play()
                    self._steps = random.randint(1,BOLT_RATE)
                else:
                    self._steps = self._steps -1
            else:
                self._time = self._time + dt

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the game objects.

        Every single thing you want to draw in this game is a GObject.

        Many of the GObjects (such as the ships, aliens, and bolts) are
        attributes in Wave. In order to draw them, you either need to add
        getters for these attributes or you need to add a draw method to
        class Wave.  We suggest the latter.  See the example subcontroller.py
        from class.
        """
        for alienrows in self._aliens:
            for alien in alienrows:
                if alien != None:
                    alien.draw(view)
        self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)

    def draw_table(self):
        """
        Creates a table of aliens according to the given constants.
        Table is built from bottom to top.
        """
        x = 0
        y = GAME_HEIGHT - ALIEN_CEILING - (ALIEN_ROWS * (ALIEN_V_SEP + ALIEN_HEIGHT))
        alien_type = 0
        image = ALIEN_IMAGES[alien_type]
        for m in range(1, ALIEN_ROWS + 1):
            columns = []
            for n in range(ALIENS_IN_ROW):
                if n == 0:
                    x = ALIEN_H_SEP + ALIEN_WIDTH//2
                    y = y + ALIEN_HEIGHT//2
                    columns.append(Alien(x = x , y = y , source = ALIEN_IMAGES[alien_type]))
                else:
                    x = x + ALIEN_H_SEP + ALIEN_WIDTH
                    columns.append(Alien(x = x, y = y , source = ALIEN_IMAGES[alien_type]))
            if m % 2 == 0:
                alien_type = alien_type + 1
                alien_type = alien_type % 3
            self._aliens.append(columns)
            y = y + ALIEN_HEIGHT + ALIEN_V_SEP

    def ship_update(self, input):
        """
        Method for updating the ship. Called by update.
        """
        da = 0
        if input.is_key_down('right'):
            da += SHIP_MOVEMENT
        if input.is_key_down('left'):
            da -= SHIP_MOVEMENT
        newpos = self._ship.x + da
        # if newpos > GAME_WIDTH:
        #     newpos = GAME_WIDTH             #Ship does not wrap-around screen
        # if newpos < 0:
        #     newpos = 0
        if newpos > GAME_WIDTH:
            newpos = 0
        if newpos < 0:
            newpos = GAME_WIDTH                     #Ship may wrap-around screen
        self._ship.x = newpos

    def alien_update(self):
        """
        Method for updating the aliens. Called by update.
        """
        lowest = self.lowest_alien()
        if lowest > DEFENSE_LINE + ALIEN_HEIGHT//2:
            rightmost = self.right_alien()
            leftmost = self.left_alien()
            if (rightmost >= GAME_WIDTH - ALIEN_WIDTH // 2 - ALIEN_H_SEP and
            self._direction == 1):
                self._direction = 2
                self.alien_down()
            elif leftmost <= ALIEN_WIDTH // 2 + ALIEN_H_SEP and self._direction  == -1:
                self._direction = -2
                self.alien_down()
            elif self._direction == -2:
                self.alien_right()
            elif rightmost < GAME_WIDTH - ALIEN_WIDTH // 2 - ALIEN_H_SEP and self._direction == 1:
                self.alien_right()
            elif self._direction == 2:
                self.alien_left()
            elif leftmost > ALIEN_WIDTH // 2 + ALIEN_H_SEP and self._direction == -1:
                self.alien_left()

    def alien_right(self):
        """
        Moves the aliens to the right.
        """
        for alien_col in self._aliens:
            for alien in alien_col:
                if alien != None:
                    alien.x = alien.x + ALIEN_H_WALK

    def alien_left(self):
        """
        Moves the aliens to the left.
        """
        for alien_col in self._aliens:
            for alien in alien_col:
                if alien != None:
                    alien.x = alien.x - ALIEN_H_WALK

    def alien_down(self):
        """
        Moves the aliens down.
        """
        for alien_col in self._aliens:
            for alien in alien_col:
                if alien != None:
                    alien.y = alien.y - ALIEN_V_WALK
        if self._direction == 2:
            self._direction = -1
        elif self._direction == -2:
            self._direction = 1

    def right_alien(self):
        """
        Finds the righmost point of the rightmost alien and returns the value.
        """
        max = 0
        for alien_col in self._aliens:
            for alien in alien_col:
                if alien != None:
                    x = alien.x
                    if x >= max:
                        max = x
        return max

    def left_alien(self):
        """
        Finds the leftmost value of the leftmost alien and returns the value.
        """
        min = GAME_WIDTH -1
        for alien_col in self._aliens:
            for alien in alien_col:
                if alien != None:
                    x = alien.x
                    if x <= min:
                        min = x
        return min

    def lowest_alien(self):
        """
        Finds the lowest alien and returns the y-value.
        """
        lowest = GAME_HEIGHT
        for alien_col in self._aliens:
            for alien in alien_col:
                if alien != None:
                    y = alien.y
                    if y <= lowest:
                        lowest = y
        return lowest

    def bolt_update(self, input):
        """
        Updates the bolts.
        """
        if input.is_key_down('spacebar') and self.num_player_bolts() < 1:
            self._bolts.append(Bolt(x = self._ship.x, y = BOLT_HEIGHT//2 + SHIP_HEIGHT
            + SHIP_BOTTOM, vel = BOLT_SPEED))
            self._pew1.play()
        self.player_bolt()
        self.alien_bolt()

    def player_bolt(self):
        """
        Method for updating bolts fired by the player.
        """
        for i in range(len(self._bolts)):
            if self._bolts[i].isPlayerBolt():
                self._bolts[i].y += BOLT_SPEED
        i = 0
        while i < len(self._bolts):
            if (self._bolts[i].y - BOLT_HEIGHT//2) > GAME_HEIGHT:
                del self._bolts[i]
            else:
                i += 1

    def alien_bolt(self):
        """
        Method for updating bolts fired by the aliens.
        """
        for i in range(len(self._bolts)):
            if self._bolts[i].isPlayerBolt() == False:
                self._bolts[i].y -= BOLT_SPEED
        i = 0
        while i < len(self._bolts):
            if (self._bolts[i].y + BOLT_HEIGHT//2) < 0:
                del self._bolts[i]
            else:
                i += 1

    def num_player_bolts(self):
        """
        Returns the number of player bolts in the list.
        """
        num = 0
        for i in self._bolts:
            if i.getVelocity() > 0:
                num = num + 1
        w = num
        num = 0
        return w

    def random_alien(self):
        """
        Finds the random alien to fire the bolt.
        """
        current_aliens = []
        for s in range(ALIENS_IN_ROW):
            no_col_alien = True
            for t in range(ALIEN_ROWS):
                if self._aliens[t][s] is not None and no_col_alien:
                    current_aliens += [self._aliens[t][s]]
                    no_col_alien = False
        return random.choice(current_aliens)

    def collision(self):
        """
        Removes alien if hit by ship bolt
        """
        for bolt in self._bolts:
            for row in range(len(self._aliens)):
                for alien in range(ALIENS_IN_ROW):
                    if self._aliens[row][alien] != None:
                        if self._aliens[row][alien].collides(bolt) and bolt.isPlayerBolt():
                            self._aliens[row][alien] = None
                            self._blast1.play()
                            self._bolts.remove(bolt)

    def shipcollision(self):
        """
        Ship loses life if hit by alien bolt
        """
        for bolt in self._bolts:
            if self._ship.shipcollides(bolt):
                self._blast2.play()
                self._bolts.remove(bolt)
                self.setLives(1)
        if self.lowest_alien() <= DEFENSE_LINE + ALIEN_HEIGHT//2:
            self.setLives(3)

    def player_won(self):
        """
        returns True if the player has won the game
        """
        acc = 0
        for x in self._aliens:
            for y in x:
                if y is not None:
                    acc += 1
        if acc == 0:
            return True
        else:
            return False

    # HELPER METHODS FOR COLLISION DETECTION
