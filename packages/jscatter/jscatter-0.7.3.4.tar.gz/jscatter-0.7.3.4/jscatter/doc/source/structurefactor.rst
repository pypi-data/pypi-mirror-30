structurefactor (sf)
====================

.. automodule:: jscatter.structurefactor
    :noindex:
   
Structure Factors
-----------------
.. autosummary::
   RMSA
   PercusYevick
   PercusYevick1D
   PercusYevick2D
   stickyHardSphere
   adhesiveHardSphere
   criticalSystem
   latticeStructureFactor
   
Hydrodynamics
-------------
.. autosummary::
   hydrodynamicFunct
   
Pair Correlation
----------------
.. autosummary::
   sq2gr

Lattice
-------
Lattices with specific structure :

.. autosummary::
    bravaisLattice
    scLattice
    bccLattice
    fccLattice
    hexLattice
    hcpLattice
    rhombicLattice
    pseudoRandomLattice

lattice methods :

.. autosummary::
    lattice.X
    lattice.Y
    lattice.Z
    lattice.b
    lattice.filter
    lattice.centerOfMass
    lattice.numberOfAtoms
    lattice.planeSide
    lattice.move
    lattice.inSphere
    lattice.show
    lattice.limit2Cube

.. include:: ../../lattice.py
    :start-after: ---
    :end-before:  END

--------

.. automodule:: jscatter.structurefactor
    :members:
    :undoc-members:
    :show-inheritance:
   
.. autoclass:: lattice
    :members:

.. autoclass:: rhombicLattice
.. autoclass:: bravaisLattice
.. autoclass:: scLattice
.. autoclass:: bccLattice
.. autoclass:: fccLattice
.. autoclass:: hexLattice
.. autoclass:: hcpLattice
.. autoclass:: pseudoRandomLattice


