from __future__ import print_function

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np

import argparse
import itertools
import logging
import random

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

class IllegalMove(Exception):
    pass

class Game2048Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # Definitions for game
        self.w = 4
        self.h = 4

        # Members for gym implementation
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(0, 16384, (self.w * self.h, ))

        # Reset ready for a game
        self._reset()

    # Implement gym interface
    def _step(self, action):
        """Perform one step of the game. This involves moving and adding a new tile."""
        logging.debug("Action {}".format(action))
        score = 0
        done = None
        try:
            score = float(self.move(action))
            self.add_tile()
            done = self.isend()
        except IllegalMove as e:
            logging.debug("Illegal move, done.")
            done = True

        #print("Am I done? {}".format(done))
        observation = np.array(self.Matrix).flatten()
        reward = float(score)
        info = dict()
        return observation, reward, done, info
        # Return observation (board state), reward, done and info dict

    def _reset(self):
        self.Matrix = [[0 for x in range(self.w)] for y in range(self.h)]
        self.score = 0

        logging.debug("Adding tiles")
        self.add_tile()
        self.add_tile()

        return np.array(self.Matrix).flatten()

    def _render(self, mode='human', close=False):
        s = 'Score: {}\n'.format(self.score)
        s += 'Highest: {}\n'.format(self.highest())
        for y in range(self.h):
            for x in range(self.w):
                s += '{0:5d}'.format(self.get(x, y))
            s += '\n'
        print(s)

    # Implement 2048 game
    def add_tile(self):
        """Add a tile, probably a 2 but maybe a 4"""
        val = 0
        if random.random() > 0.8:
            val = 4
        else:
            val = 2
        empties = self.empties()
        assert empties
        empty = random.choice(empties)
        logging.debug("Adding %s at %s", val, (empty[0], empty[1]))
        self.set(empty[0], empty[1], val)

    def get(self, x, y):
        """Return the value of one square."""
        return self.Matrix[x][y]

    def set(self, x, y, val):
        """Set the value of one square."""
        self.Matrix[x][y] = val

    def empties(self):
        """Return a list of tuples of the location of empty squares."""
        empties = list()
        for y in range(self.h):
            for x in range(self.w):
                if self.get(x, y) == 0:
                    empties.append((x, y))
        return empties

    def highest(self):
        """Report the highest tile on the board."""
        highest = 0
        for y in range(self.h):
            for x in range(self.w):
                highest = max(highest, self.get(x, y))
        return highest

    def move(self, direction, trial=False):
        """Perform one move of the game. Shift things to one side then,
        combine. directions 0, 1, 2, 3 are left, up, right, down.
        Returns the score that [would have] got."""
        if not trial:
            if direction == 0:
                logging.debug("Left")
            elif direction == 1:
                logging.debug("Up")
            elif direction == 2:
                logging.debug("Right")
            elif direction == 3:
                logging.debug("Down")

        changed = False
        move_score = 0
        dir_mod_two = direction % 2
        dir_div_two = int(direction / 2) # 0 for towards up left, 1 for towards bottom right

        # Construct a range for extracting row/column into a list
        rx = range(self.w)
        ry = range(self.h)

        if dir_mod_two == 0:
            # Up or down, split into columns
            for x in range(self.w):
                old = [self.get(x, y) for y in ry]
                (new, ms) = self.shift(old, dir_div_two)
                move_score += ms
                if old != new:
                    changed = True
                    if not trial:
                        for y in ry:
                            self.set(x, y, new[y])
        else:
            # Left or right, split into rows
            for y in range(self.h):
                old = [self.get(x, y) for x in rx]
                (new, ms) = self.shift(old, dir_div_two)
                move_score += ms
                if old != new:
                    changed = True
                    if not trial:
                        for x in rx:
                            self.set(x, y, new[x])
        if changed != True:
            raise IllegalMove

        if not trial:
            # Update score
            self.score += move_score

        return move_score

    def combine(self, shifted_row):
        """Combine same tiles when moving to one side. This function always
           shifts towards the left. Also count the score of combined tiles."""
        move_score = 0
        combined_row = [0] * 4
        skip = False
        output_index = 0
        for p in pairwise(shifted_row):
            if skip:
                skip = False
                continue
            combined_row[output_index] = p[0]
            if p[0] == p[1]:
                combined_row[output_index] += p[1]
                move_score += p[0] + p[1]
                # Skip the next thing in the list.
                skip = True
            output_index += 1
        if not skip:
            combined_row[output_index] = shifted_row[-1]

        return (combined_row, move_score)

    def shift(self, row, direction):
        """Shift one row left (direction == 0) or right (direction == 1), combining if required."""
        length = len(row)
        assert length == 4
        assert direction == 0 or direction == 1

        # Shift all non-zero digits up
        shifted_row = [i for i in row if i != 0]

        # Reverse list to handle shifting to the right
        if direction:
           shifted_row.reverse()

        # fill with 0s
        zero_count = length - len(shifted_row)
        shifted_row += [0] * zero_count

        (combined_row, move_score) = self.combine(shifted_row)

        # Reverse list to handle shifting to the right
        if direction:
            combined_row.reverse()

        assert len(combined_row) == 4
        return (combined_row, move_score)

    def isend(self):
        """Has the game ended. Game ends if there are no legal moves.
        If there are empty spaces then there must be legal moves."""

        actions = list()
        for direction in range(4):
            try:
                self.move(direction, trial=True)
                actions.append(direction)
            except IllegalMove:
                pass

        legal_moves = len(actions)
        logging.debug("Legal moves %s", legal_moves)
        return not bool(legal_moves)

    def get_board(self):
        """Retrieve the whole board, useful for testing."""
        return self.Matrix

    def set_board(self, new_board):
        """Retrieve the whole board, useful for testing."""
        self.Matrix = new_board

