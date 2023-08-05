#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from numpy.testing import assert_almost_equal
from ppr.util import cp, VirtualArray, VirtualJointSolutions
from ppr.path import TolerancedNumber, TrajectoryPt
from ppr.robot import Robot_2P3R
from ppr.geometry import Rectangle

def test_cp():
  l = [2, 3, 6]
  a = cp(l)
  d = 2*3*6
  assert_almost_equal(a, d)

class TestVirtualArray():
  def test_indexing(self):
    ranges = [np.array([1, 2]),
              np.array([3]),
              np.array([5, 6, 7])]
    va = VirtualArray(ranges)
    ac = [va[i] for i in range(va.total_size)]
    de = [[1, 3, 5],[2, 3, 5],
          [1, 3, 6],[2, 3, 6],
          [1, 3, 7],[2, 3, 7]]
    assert_almost_equal(ac, de)

class TestVirtualJointSolutions():
  # SLOW test (0.2 s)
  def test_all(self):
    # create trajectory point
    x = TolerancedNumber(2, 1, 3, samples=3)
    y = TolerancedNumber(2.5, 2, 3, samples=4)
    tp = TrajectoryPt([x, y, 0])
    
    # create robot and collision scene
    robot1 = Robot_2P3R([1, 1, 2, 1.5, 0.5])
    sc1 = [Rectangle(2, 1, 0.5, 0.5, 0)]
    
    # create the object
    vjs = VirtualJointSolutions(robot1, tp, sc1)
    
    # try to index the whole range
    for i in range(vjs.size): sol = vjs[i]
    