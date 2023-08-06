# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
---
Lattice objects describing a lattice of points.

Included are methods to select sublattices as cubes, sphere or side of planes.

The small angle scattering can is calculated by js.ff.cloudScattering.

The same method can be used to calculate the wide angle scattering with bragg peaks
using larger scattering vectors.


**Examples**

A hollow sphere cut to a wedge.
::

 import jscatter as js
 import numpy as np
 grid= js.lattice.scLattice(1/2.,2*8)
 grid.inSphere(6)
 grid.inSphere(-4)
 grid.limit2Cube(6,6,6)
 grid.planeSide([1,1,1])
 grid.planeSide([1,-1,-1])
 grid.show()

 q=js.loglist(0.01,5,300)
 ffe=js.ff.cloudScattering(q,grid.points,nFib=50,rms=0.1)
 p=js.grace()
 p.plot(ffe)

A comparison of sc, bcc and fcc nanoparticles (takes a while )
::

 import jscatter as js
 import numpy as np
 q=js.loglist(0.01,35,1500)
 q=np.r_[js.loglist(0.01,3,200),3:40:800j]
 cubelength=1.5
 N=8
 grid= js.lattice.scLattice(cubelength,N)
 sc=js.ff.cloudScattering(q,grid.points,nFib=50,rms=0.05)
 grid= js.lattice.bccLattice(cubelength,N)
 bcc=js.ff.cloudScattering(q,grid.points,nFib=50,rms=0.05)
 grid= js.lattice.fccLattice(cubelength,N)
 fcc=js.ff.cloudScattering(q,grid.points,nFib=50,rms=0.05)
 p=js.grace(1.5,1)
 # smooth with Gaussian to include instrument resolution
 p.plot(sc.X,js.formel.smooth(sc,10, window='gaussian'),legend='sc')
 p.plot(bcc.X,js.formel.smooth(bcc,10, window='gaussian'),legend='bcc')
 p.plot(fcc.X,js.formel.smooth(fcc,10, window='gaussian'),legend='fcc')
 p.title('Comparison sc, bcc, fcc lattice for a nano cube')
 p.yaxis(scale='l',label='I(Q)')
 p.xaxis(scale='l',label='Q / A\S-1')
 p.legend(x=0.03,y=0.001,charsize=1.5)
 p.text('cube formfactor',x=0.02,y=0.05,charsize=1.4)
 p.text('Bragg peaks',x=4,y=0.05,charsize=1.4)

END
"""
from __future__ import division
from __future__ import print_function

import numpy as np
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
except:
    pass

class rhombicLattice(object):

    def __init__(self, latticeVectors, size, primitive=None,b=None):
        """
        Create a rhombic lattice.

        Allows to create 1D, 2D or 3D latices by using 1, 2 or 3 latticeVectors.

        Parameters
        ----------
        latticeVectors : list of array 3x1
            Lattice primitive vectors defining the translation of the unit cell along its principal axes.
        size :3x integer or integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.
        primitive : list of 3x1 array, None=[0,0,0]
            Position vectors of atoms in the primitive cell.
        b : list of float
            Corresponding scattering length of atoms in the primitive cell.

        Returns
        -------
        lattice object
            .array  grid points as numpy array
            .primitiveVolume         V = a1*a2 x a3 with latticeVectors a1, a2, a3;  if existing.

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         # cubic lattice with diatomic base
         grid=js.lattice.rhombicLattice([[1,0,0],[0,1,0],[0,0,1]],[3,3,3],[[-0.1,-0.1,-0.1],[0.1,0.1,0.1]],[1,2])
         #
         fig = plt.figure()
         ax = fig.add_subplot(111, projection='3d')
         #
         ax.scatter(grid.X,grid.Y,grid.Z,color="k",s=20)
         ax.set_xlim([-5,5])
         ax.set_ylim([-5,5])
         ax.set_zlim([-5,5])
         ax.set_aspect("equal")
         plt.tight_layout()
         plt.show(block=False)

        """
        if len(latticeVectors) != len(size):
            raise TypeError('size and latticeVectors not compatible. Check dimension!')
        if primitive is None:
            primitive = [np.r_[0, 0, 0]]
        if b is None:
            b=[1]*len(primitive)
        self.primitive_b=b
        self.dimension = len(latticeVectors)
        try:
            V=np.dot(latticeVectors[0],np.cross(latticeVectors[1],latticeVectors[2]))
            self.primitiveVolume=V
            #self.reciprocalVectors = []
            #self.append(2 * np.pi/V *np.cross(latticeVectors[2],latticeVectors[3]))
            #self.append(2 * np.pi / V * np.cross(latticeVectors[3], latticeVectors[1]))
            #self.append(2 * np.pi / V * np.cross(latticeVectors[1], latticeVectors[2]))
        except:pass
        self.latticeVectors=latticeVectors
        self.size=size
        self._makeLattice( self.latticeVectors, size, primitive, self.primitive_b)

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, item, value):
        self.points[item] = value

    @property
    def X(self):
        """X coordinates"""
        return self.points[:,0]

    @property
    def Y(self):
        """Y coordinates"""
        return self.points[:, 1]

    @property
    def Z(self):
        """Z coordinates"""
        return self.points[:, 2]

    @property
    def b(self):
        """Scattering length"""
        return self.points[:, 3]

    @property
    def shape(self):
        return self.array.shape

    @property
    def array(self):
        """Coordinates and scattering length as array"""
        return np.array(self.points)

    def filter(self,funktion):
        """
        Filter lattice points according to a function.

        The existing points in the lattice size are tested.

        Parameters
        ----------
        funktion : function returning bool
            Function to select lattice points.
            The function is applied with the point coordinates (array) as input.
            This corresponds to .points[:,:3]

        Returns
        -------
            array

        Examples
        --------
        To select points inside of a sphere with radius 50 around [0,0,0]:
        ::

         grid.filter(lambda xyz: np.sum(xyz**2)<50**2)


        """
        return self.points[[funktion(point) for point in self.points[:,:3]]]

    def centerOfMass(self):
        """
        CenterOf mass
        """
        return self.points[:,:3].mean(axis=0)

    def limit2Cube(self,a,b,c):
        """
        Cut at cube with edges at

        Parameters
        ----------
        a,b,c : float
            Cut at +-[a,0,0],+-[0,b,0],+-[0,0,c]

        Returns
        -------

        """
        choose=(abs(self.X)<a) & (abs(self.Y)<b) & (abs(self.Z)<c)
        self.points=self.points[choose]

    def planeSide(self,vector,invert=False):
        """
        Select points on one side of a plane.

        Parameters
        ----------
        vector : list 3x float
            Vector from origin to plane, perpendicular to plane.
        invert : bool
            False choose points at origin side. True other side.

        """
        v=np.array(vector)
        vv=(v ** 2).sum() ** 0.5
        v=v/vv
        if invert:
            choose = np.dot(self.points[:,:3] , v) >= vv
        else:
            choose = np.dot(self.points[:,:3] , v) <= vv
        self.points = self.points[choose]

    def move(self,vector):
        """
        Move all points by vector.
        Parameters
        ----------
        vector : list of float
            Vector to shift the points.

        """
        self.points[:,:3]=self.points[:,:3]+np.array(vector)

    def inSphere(self,R):
        """
        Choose lattice points in sphere

        Parameters
        ----------
        R: float
            Radius of sphere around origin.
            If negative the points outside are choosen

        """
        if R>0:
            choose=np.sum((self.points[:,:3]**2),axis=1)<R**2
        else:
            choose = np.sum((self.points[:,:3]**2), axis=1) > R**2
        self.points=self.points[choose]

    def show(self):
        """
        Show the lattice in matplotlib.

        """
        ff=1.2
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.X,self.Y,self.Z,color="k",s=20)
        ax.set_xlim([self.X.min()*ff,self.X.max()*ff])
        ax.set_ylim([self.Y.min()*ff,self.Y.max()*ff])
        ax.set_zlim([self.Z.min()*ff,self.Z.max()*ff])
        ax.set_aspect("equal")
        plt.tight_layout()
        plt.show(block=False)
        return fig

    def _makeLattice(self, latticeVectors, size, primitive=None,pb=None):
        abc=latticeVectors[0]*np.r_[-size[0]:size[0]+1][:,None]
        if len(size)>1:
            abc = abc+(latticeVectors[1]*np.r_[-size[1]:size[1]+1][:,None])[:,None]
        if len(size) > 2:
            abc = abc + (latticeVectors[2]*np.r_[-size[2]:size[2]+1][:,None,None])[:,None,None]
        abc=abc.reshape(-1,3)
        abc=np.c_[(abc,np.zeros(abc.shape[0]))]
        self.points=np.vstack([abc + np.r_[ev,b] for ev,b in zip(primitive,pb)])
        self.primitive=primitive


class bravaisLattice(rhombicLattice):

    def __init__(self, latticeVectors, size):
        """
        Create a bravais lattice. Lattice with one atom in the primitive cell.

        See rhombicLattice for methods and attributes.

        Parameters
        ----------
        latticeVectors : list of array 1x3
            Lattice primitive vectors defining the translation of the unit cell along its principal axes.
        size :3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points asnumpy array

        """
        rhombicLattice.__init__(self, latticeVectors, size, primitive=None)


class scLattice(bravaisLattice):

    def __init__(self, abc, size):
        """
        Simple Cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.lattice.bccLattice(1.2,1).array
         #
         fig = plt.figure()
         ax = fig.add_subplot(111, projection='3d')
         #
         ax.scatter(grid[:,0],grid[:,1],grid[:,2],color="k",s=20)
         ax.set_xlim([-5,5])
         ax.set_ylim([-5,5])
         ax.set_zlim([-5,5])
         ax.set_aspect("equal")
         plt.tight_layout()
         plt.show(block=False)

        """
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size,int):
            size = [size]*3
        bravaisLattice.__init__(self, latticeVectors, size)


class bccLattice(rhombicLattice):

    def __init__(self, abc, size,b=None):
        """
        Body centered cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.lattice.bccLattice(1.2,1).array
         #
         fig = plt.figure()
         ax = fig.add_subplot(111, projection='3d')
         #
         ax.scatter(grid[:,0],grid[:,1],grid[:,2],color="k",s=20)
         ax.set_xlim([-5,5])
         ax.set_ylim([-5,5])
         ax.set_zlim([-5,5])
         ax.set_aspect("equal")
         plt.tight_layout()
         plt.show(block=False)

        """
        primitive = [np.r_[0, 0, 0], abc * np.r_[0.5, 0.5, 0.5]]
        latticeVectors = [abc * np.r_[1., 0., 0.],
                          abc * np.r_[0., 1., 0.],
                          abc * np.r_[0., 0., 1.]]
        if isinstance(size,int):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, primitive,b)


class fccLattice(rhombicLattice):

    def __init__(self, abc, size):
        """
        Face centered cubic lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        abc : float
            Point distance.
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.lattice.fccLattice(1.2,1).array
         #
         fig = plt.figure()
         ax = fig.add_subplot(111, projection='3d')
         #
         ax.scatter(grid[:,0],grid[:,1],grid[:,2],color="k",s=20)
         ax.set_xlim([-5,5])
         ax.set_ylim([-5,5])
         ax.set_zlim([-5,5])
         ax.set_aspect("equal")
         plt.tight_layout()
         plt.show(block=False)

        """
        primitive = [      np.r_[0, 0, 0],
                     abc * np.r_[0, 0.5, 0.5],
                     abc * np.r_[0.5, 0, 0.5],
                     abc * np.r_[0.5, 0.5, 0]]
        latticeVectors = [abc *np.r_[1., 0., 0.],
                          abc *np.r_[0., 1., 0.],
                          abc *np.r_[0., 0., 1.]]
        if isinstance(size,int):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, primitive)

class hexLattice(rhombicLattice):

    def __init__(self, ab,c, size):
        """
        Hexagonal lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab,c : float
            Point distance.
            ab is distance in hexagonal plane, c perpendicular.
            For c/a = (8/3)**0.5 the hcp structure
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.lattice.hexLattice(1.,2,[2,2,2]).array
         #
         fig = plt.figure()
         ax = fig.add_subplot(111, projection='3d')
         ax.scatter(grid[:,0],grid[:,1],grid[:,2],color="k",s=20)
         ax.set_xlim([-5,5])
         ax.set_ylim([-5,5])
         ax.set_zlim([-5,5])
         ax.set_aspect("equal")
         plt.tight_layout()
         plt.show(block=False)

        """

        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5*ab, 3**0.5/2*ab, 0.],
                          np.r_[0., 0., c]]
        primitive = [      np.r_[0, 0, 0] ]
        if isinstance(size,int):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, primitive)

class hcpLattice(rhombicLattice):

    def __init__(self, ab, size):
        """
        Hexagonal closed packed lattice.

        See rhombicLattice for methods.

        Parameters
        ----------
        ab : float
            Point distance.
            ab is distance in hexagonal plane, c = ab* (8/3)**0.5
        size : 3x integer, integer
            A list of integers describing the size in direction of the respective latticeVectors.
            Size is symmetric around zero in interval [-i,..,i] with length 2i+1.
            If one integer is given it is used for all 3 dimensions.

        Returns
        -------
        lattice object
            .array  grid points as numpy array

        Examples
        --------
        ::

         import jscatter as js
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         grid=js.lattice.hcpLattice(1.2,[3,3,1]).array
         #
         fig = plt.figure()
         ax = fig.add_subplot(111, projection='3d')
         #
         ax.scatter(grid[:,0],grid[:,1],grid[:,2],color="k",s=20)
         ax.set_xlim([-5,5])
         ax.set_ylim([-5,5])
         ax.set_zlim([-5,5])
         ax.set_aspect("equal")
         plt.tight_layout()
         plt.show(block=False)

        """
        c = ab* (8/3.)**0.5
        latticeVectors = [np.r_[ab, 0., 0.],
                          np.r_[0.5*ab, 3**0.5/2*ab, 0.],
                          np.r_[0., 0., c]]
        primitive = [      np.r_[0, 0, 0],
                     1/3.*latticeVectors[0] + 1/3.*latticeVectors[1] + 0.5*latticeVectors[2] ]

        if isinstance(size,int):
            size = [size]*3
        rhombicLattice.__init__(self, latticeVectors, size, primitive)

