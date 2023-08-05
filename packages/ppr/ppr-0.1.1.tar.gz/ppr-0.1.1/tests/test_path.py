#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import numpy as np
import matplotlib.pyplot as plt
from numpy.testing import assert_almost_equal
from ppr.geometry import Rectangle
from ppr.path import TolerancedNumber, TrajectoryPt
from ppr.path import cart_to_joint, get_shortest_path
from ppr.robot import Robot_3R, Robot_2P

class TestTolerancedNumber():
    def test_nominal_outside_bounds_error(self):
        with pytest.raises(ValueError) as info:
            a = TolerancedNumber(1.5, 0, 1)
        # check whether the error message is present
        msg = "nominal value must respect the bounds"
        assert(msg in str(info))

class TestTrajectoryPt():
    def test_plot(self):
        x = TolerancedNumber(1.5, 1.0, 2.0)
        y = TolerancedNumber(3.0, 2.9, 3.2)
        angle = TolerancedNumber(np.pi / 8, 0.0, np.pi / 4)
        tp = TrajectoryPt([x, y, angle])
        fig, ax = plt.subplots()
        plt.axis([0, 4, 0, 4])
        tp.plot(ax)

def test_cart_to_joint():
    robot2p = Robot_2P([1, 1])
    x = TolerancedNumber(2, 1, 3, samples=3)
    path = [TrajectoryPt([x, 1.0, 0]),
            TrajectoryPt([x, 1.5, 0]),
            TrajectoryPt([x, 2.0, 0])]
    actual = cart_to_joint(robot2p, path)
    desired = [np.array([[1, 1],
                         [2, 1],
                         [3, 1]]),
               np.array([[1, 1.5],
                         [2, 1.5],
                         [3, 1.5]]),
               np.array([[1, 2],
                         [2, 2],
                         [3, 2]])]
    assert(len(actual) == len(desired))
    for i in range(3):
        assert_almost_equal(actual[i], desired[i])

def test_cart_to_joint_no_scene():
    robot2p = Robot_2P([1, 1])
    path = []
    with pytest.raises(ValueError) as info:
        cart_to_joint(robot2p, path, check_collision=True)
    # check whether the error message is present
    msg = "scene is needed for collision checking"
    assert(msg in str(info))

def test_cart_to_joint_with_check_collision():
    robot2p = Robot_2P([1, 1])
    x = TolerancedNumber(2, 1, 3, samples=3)
    path = [TrajectoryPt([x, 1.0, 0]),
            TrajectoryPt([x, 1.5, 0]),
            TrajectoryPt([x, 2.0, 0])]
    scene = [Rectangle(0, 1.5, 1, 1, 0)]
    actual = cart_to_joint(robot2p, path, check_collision=True, scene=scene)
    desired = [np.array([[1, 1],
                         [2, 1],
                         [3, 1]]),
               np.array([[2, 1.5],
                         [3, 1.5]]),
               np.array([[2, 2],
                         [3, 2]])]
    assert(len(actual) == len(desired))
    for i in range(3):
        assert_almost_equal(actual[i], desired[i])

def test_get_shortest_path():
    Q = [np.array([[0, 0]]),
         np.array([[1, -1], [1, 0], [1, 1]]),
         np.array([[0, 2], [2, 2]])]
    res = get_shortest_path(Q)
    actual1 = res['success']
    actual2 = res['path']
    desired1 = True
    desired2 = [Q[0][0], Q[1][1], Q[2][0]]
    assert actual1 == desired1
    assert_almost_equal(actual2, desired2)

def test_get_shortest_path_failed():
    Q = [np.array([[0, 0]]),
         np.array([[1, -1], [1, 0], [1, 1]]),
         np.array([]),
         np.array([[0, 2], [2, 2]])]
    res = get_shortest_path(Q)
    assert res['success'] == False
    with pytest.raises(KeyError):
         res['path']
    