#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.08.2015 16:43:18 CEST
# File:    sphere_division.py

from . import polyhedra

import numpy as np

def divide_sphere(num_subdivisions):
    verts, faces = polyhedra.icosahedron()
    for x in range(num_subdivisions):
        verts, faces = polyhedra.subdivide(verts, faces)

    return verts, faces

def sphere_points(center, radius, divisions):
    r"""
    Return the vertices that lie on a sphere with a given center and radius. The vertices are created by dividing the icosahedron ``divisions`` times. 
    """
    verts_normalized = np.array(divide_sphere(divisions)[0])
    middle = np.array(center)
    return [middle + radius * vert for vert in verts_normalized]
