#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ppr.geometry import Rectangle

import numpy as np
from scipy.linalg import norm
from scipy.optimize import minimize
from numpy.testing import assert_almost_equal, assert_, assert_allclose

atol = 1e-15

def mimimum_distance(A1, b1, A2, b2):
    def obj(x):
        return np.sqrt(np.sum((x[:2] - x[2:])**2))
    cons = ({'type': 'ineq',
             'fun': lambda x: b1 - np.dot(A1, x[:2]),
             'jac': lambda x: np.hstack(( -A1, np.zeros((4, 2)) )) },
            {'type': 'ineq',
             'fun': lambda x: b2 - np.dot(A2, x[2:]),
             'jac': lambda x: np.hstack(( np.zeros((4, 2)), -A2 )) }
            )
    x_init = np.zeros(4)
    res = minimize(obj, x_init,
                   method='SLSQP',
                   constraints=cons)
    return obj(res['x'])

class TestRectanlge():
    def test_init_function(self):
        rec1 = Rectangle(0.5, 2, 1, 3, 0)
    
    def test_get_matrix_form(self):
        sq2 = np.sqrt(2)
        pi4 = np.pi / 4
        rects = [Rectangle(1, 2, sq2, 2*sq2, -np.pi / 4),
                 Rectangle(-5.5, -4.5, 2, 3,  np.pi / 2)]
        # expected results
        As = [np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]),
              np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])]
        bs = [np.array([-3, 1, 7, 1]),
              np.array([-5.5, -2.5, 8.5, 4.5])]
        # normalize equations
        for i in range(len(As)):
            n = norm(As[i], axis=1)
            As[i] = As[i] / n[:, None]
            bs[i] = bs[i] / n
        for i in range(len(rects)):
            At, bt = rects[i].get_matrix_form()
            assert_allclose(At, As[i], atol=atol)
            assert_allclose(bt, bs[i], atol=atol)
    
    def test_get_matrix_form_in_optimisation_problem(self):
         rec1 = Rectangle(1, 2, 3, 2, 0)
         rec2 = Rectangle(-1, 5, 2, 4, np.pi/4)
         A1, b1 = rec1.get_matrix_form()
         A2, b2 = rec2.get_matrix_form()
         dist = mimimum_distance(A1, b1, A2, b2)
         assert_almost_equal(dist, 2.121320343529712)
    
    def test_check_self_collision(self):
        rec1 = Rectangle(1, 2, 3, 2, np.pi/3)
        actual = rec1.is_in_collision(rec1)
        desired = True
        assert_(actual == desired)
