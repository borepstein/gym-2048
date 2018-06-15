#!/usr/bin/env python

from __future__ import absolute_import
import unittest
import numpy as np

import training_data

class TestTrainingData(unittest.TestCase):
    def test_add(self):
        # Test add without reward
        td = training_data.training_data()
        self.assertTrue(np.array_equal(td.get_x(), np.empty([0, 4, 4], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_y_digit(), np.empty([0, 1], dtype=np.int)))
        td.add(np.ones([1, 4, 4]), 1)
        self.assertTrue(np.array_equal(td.get_x(), np.ones([1, 4, 4], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_y_digit(), np.array([[1]], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_reward(), np.empty([0, 1], dtype=np.int)))

        # Test add with reward
        td = training_data.training_data()
        self.assertTrue(np.array_equal(td.get_x(), np.empty([0, 4, 4], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_y_digit(), np.empty([0, 1], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_reward(), np.empty([0, 1], dtype=np.int)))
        td.add(np.ones([1, 4, 4]), 1, 4)
        self.assertTrue(np.array_equal(td.get_x(), np.ones([1, 4, 4], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_y_digit(), np.array([[1]], dtype=np.int)))
        self.assertTrue(np.array_equal(td.get_reward(), np.array([[4]], dtype=np.int)))

        # Test mixing causes assert
        with self.assertRaises(Exception):
            td.add(np.ones([1, 4, 4]), 1)

    def test_get_n(self):
        # Test add without reward
        td = training_data.training_data()
        td.add(np.ones([4, 4], dtype=np.int), 1)
        td.add(np.zeros([4, 4], dtype=np.int), 2)
        (state, action) = td.get_n(1)
        self.assertTrue(np.array_equal(state, np.zeros([4, 4], dtype=np.int)))
        self.assertEqual(action, 2)

        # Test add with reward
        td = training_data.training_data()
        td.add(np.ones([4, 4]), 1, 4)
        td.add(np.zeros([4, 4]), 2, 8)
        (state, action, reward) = td.get_n(1)
        self.assertTrue(np.array_equal(state, np.zeros([4, 4], dtype=np.int)))
        self.assertEqual(action, 2)
        self.assertEqual(reward, 8)

    def test_hflip(self):
        td = training_data.training_data()
        board1 = np.array([[1, 1, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0]])
        td.add(board1, 1)
        board2 = np.array([[0, 0, 0, 0],
                           [2, 4, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0]])
        td.add(board2, 2)
        td.hflip()
        expected_x = np.array([
            [[0, 0, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 0, 0], [0, 0, 4, 2], [0, 0, 0, 0], [0, 0, 0, 0]]
            ], dtype=np.int)
        expected_y_digit = np.array([
            [3],
            [2]
            ], dtype=np.int)
        self.assertTrue(np.array_equal(td.get_x(), expected_x))
        self.assertTrue(np.array_equal(td.get_y_digit(), expected_y_digit))

    def test_rotate(self):
        td = training_data.training_data()
        board1 = np.array([[1, 1, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0]])
        td.add(board1, 1)
        board2 = np.array([[0, 0, 0, 0],
                           [2, 4, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0]])
        td.add(board2, 2)
        td.rotate(3)
        expected_x = np.array([
            [[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 4, 0, 0], [0, 2, 0, 0]]
            ], dtype=np.int)
        expected_y_digit = np.array([
            [0],
            [1]
            ], dtype=np.int)
        self.assertTrue(np.array_equal(td.get_x(), expected_x))
        self.assertTrue(np.array_equal(td.get_y_digit(), expected_y_digit))

    def test_augment(self):
        td = training_data.training_data()
        initial_board = np.array([[1, 1, 0, 0],
                                  [0, 0, 0, 0],
                                  [0, 0, 0, 0],
                                  [0, 0, 0, 0]])
        td.add(initial_board, 1, 4)
        td.augment()
        self.assertEqual(td.size(), 8)
        expected_x = np.array([
            [[1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 1]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 1]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 0, 0]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
            [[1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            ], dtype=np.int)
        expected_y_digit = np.array([
            [1],
            [3],
            [2],
            [0],
            [3],
            [1],
            [0],
            [2]
            ], dtype=np.int)
        expected_reward = np.array([
            [4],
            [4],
            [4],
            [4],
            [4],
            [4],
            [4],
            [4]
            ], dtype=np.int)
        self.assertTrue(np.array_equal(td.get_x(), expected_x))
        self.assertTrue(np.array_equal(td.get_y_digit(), expected_y_digit))
        self.assertTrue(np.array_equal(td.get_reward(), expected_reward))

    def test_merge(self):
        td = training_data.training_data()
        td.add(np.ones([1, 4, 4]), 1)
        td2 = training_data.training_data()
        td2.add(np.zeros([1, 4, 4]), 2)
        td.merge(td2)
        expected_x = np.array([
            [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            ], dtype=np.int)
        self.assertTrue(np.array_equal(td.get_x(), expected_x))

    def test_split(self):
        td = training_data.training_data()
        td.add(np.ones([1, 4, 4]), 1)
        td2 = training_data.training_data()
        td2.add(np.zeros([1, 4, 4]), 2)
        td.merge(td2)
        a, b = td.split()
        self.assertTrue(np.array_equal(a.get_x(), np.ones([1, 4, 4])))
        self.assertTrue(np.array_equal(a.get_y_digit(), [[1]]))
        self.assertTrue(np.array_equal(b.get_x(), np.zeros([1, 4, 4])))
        self.assertTrue(np.array_equal(b.get_y_digit(), [[2]]))

    def test_size(self):
        td = training_data.training_data()
        self.assertEqual(td.size(), 0)

if __name__ == '__main__':
    unittest.main()
