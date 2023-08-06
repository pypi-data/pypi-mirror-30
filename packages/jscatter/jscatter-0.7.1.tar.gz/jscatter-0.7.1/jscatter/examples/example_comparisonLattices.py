# A comparison of sc, bcc and fcc nanoparticles

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

# p.save('jscatter/examples/LatticeComparison.png')


