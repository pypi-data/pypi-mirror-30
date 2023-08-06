# -*- coding: utf-8 -*-
#  this file is intended to used in the debugger
# write a script that calls your function to debug it

import jscatter as js
import numpy as np
import sys
# some arrays
w=np.r_[-100:100]
q=np.r_[0:10:0.1]
x=np.r_[1:10]

# use pseudo random
# https://en.wikipedia.org/wiki/Low-discrepancy_sequence

q = np.r_[js.loglist(0.1, 3, 100), 3:40:800j]
unitcelllength = 1.5
N = 8
rms=0.05
domainsize=unitcelllength*(2*N+1)

fccgrid = js.lattice.fccLattice(unitcelllength, N)
fcc = js.ff.cloudScattering(q, fccgrid.points, relError=0.02, rms=rms)
p = js.grace(1.5, 1)
p.plot(fcc.X, js.formel.smooth(fcc, 5, window='gaussian')*fccgrid.numberOfAtoms(), legend='fcc explicit')

q = np.r_[js.loglist(0.1, 3, 200), 3:40:1600j]
sc = js.sf.latticeStructureFactor(q, a=unitcelllength, rmsd=rms , domainsize=domainsize,type='fcc')
p.plot(sc, li=[1, 3, 4], sy=0, le='fcc analytic')
p.yaxis(scale='l', label='I(Q)')
p.xaxis(scale='l', label='Q / A\S-1')
p.legend(x=1, y=100, charsize=1.5)
p.title('Comparison explicit and implicit model for a crystal cube')
p.text('cube formfactor', x=0.11, y=1, charsize=1.4)
p.text('fcc Bragg peaks', x=4, y=100, charsize=1.4)
p.text('diffusive scattering', x=10, y=0.1, charsize=1.4)
# p.save('jscatter/examples/LatticeComparison3.png')


