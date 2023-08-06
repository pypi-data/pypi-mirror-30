Beginners Guide / Help
======================

.. autosummary::
    jscatter.showDoc


Reading ASCII files
-------------------
- dataArray (js.dA) reads **one** dataset from a file (you can choose which one).

- dataList  (js.dL) reads **all** datasets from one or multiple files (even if different in shape).

****

A common problem is how to read ASCII files with data as the format is often not
very intuitive designed. Often there is additional metadata before or after a matrix like block.

Jscatter uses a simple concept to classify lines :
 * 2 numbers at the beginning of a line are data (matrix like data block).
 * a name followed by a number (and more) is an attribute with name and content.
 * everything else is comment (but can later be converted to an attribute).

Often it is just necessary to replace some characters to fit into this idea.
This can be done during reading using some simple options in dataArray/dataList creation:
 * replace={‘old’:’new’,’,’:’.’}     ==>  replace char and strings
 * skiplines=lambda words: any(w in words for w in [‘’,’ ‘,’NAN’,’‘*])  ==> skip complete bad lines
 * takeline='ATOM'   ==> select specific lines
 * ignore ='#'       ==> skip lines starting with this
 * usecols =[1,2,5]  ==> select specific columns
 * lines2parameter=[2,3,4]  ==> use these data lines as comment

See :py:func:`jscatter.dataarray.dataArray` for all options and how to do this.

If there is more information in comments or filename this can be extracted by using the comment lines.
 * data.getfromcomment('nameatfirstcolumn') ==> extract a list of words in this line
 * data.name  ==> filename, see below for example.


**Some examples and how to read them**

data1_273K_10mM.dat (e.g. Instrument JNSE@MLZ, Garching) ::

 this is just a comment or description of the data
 temp     293
 pressure 1013 14
 detectorsetting up
 name     temp1bsa
 0.854979E-01  0.178301E+03  0.383044E+02
 0.882382E-01  0.156139E+03  0.135279E+02
 0.909785E-01  0.150313E+03  0.110681E+02
 0.937188E-01  0.147430E+03  0.954762E+01
 0.964591E-01  0.141615E+03  0.846613E+01
 0.991995E-01  0.141024E+03  0.750891E+01
 0.101940E+00  0.135792E+03  0.685011E+01
 0.104680E+00  0.140996E+03  0.607993E+01

Read by ::

 data=js.dA('data1.dat')
 data.pressure                                    # get [1013, 14] # this was created automatically
 # if you need the additional information
 data.getfromComment('detectorsetting')           # creates attribute detectorsetting with value 'up' found in comments
 data.Temp=float(data.name.split('_')[1][:-1])    # extracts the temperature from filename
 data.conc=float(data.name.split('_')[2][:-2])    # same for concentration


aspirin.pdb: Atomic coordinates for aspirin (protein atomic coordinates
`Matplotlib <https://www.rcsb.org/pdb/home/home.do>`_ )::

 Header
 Remarks blabla
 Remarks in pdb files are sometimes more than 100 lines
 ATOM      1  C1  MON     1       0.864   0.189  -0.055  1.00  0.00
 ATOM      2  C2  MON     1       1.690   1.283  -0.052  1.00  0.00
 ATOM      3  C3  MON     1       3.058   1.144  -0.020  1.00  0.00
 ATOM      4  C4  MON     1       3.612  -0.130   0.017  1.00  0.00
 ATOM      5  C5  MON     1       2.757  -1.212   0.005  1.00  0.00
 ATOM      6  C6  MON     1       1.400  -1.070  -0.032  1.00  0.00
 ATOM      7  C7  MON     1       3.835   2.447  -0.015  1.00  0.00
 ATOM      8  O8  MON     1       3.195   3.503  -0.064  1.00  0.00
 ATOM      9  O9  MON     1       5.226   2.540   0.043  1.00  0.00
 ATOM     10  O10 MON     1       5.039  -0.260   0.070  1.00  0.00
 ATOM     11  C11 MON     1       5.857  -1.416   0.236  1.00  0.00
 ATOM     12  O12 MON     1       5.502  -2.587   0.436  1.00  0.00
 ATOM     13  C13 MON     1       7.303  -1.154   0.202  1.00  0.00
 HETATOM lines may apear at the end

Read by ::

 js.dA('aspirin.pdb',takeline='ATOM',usecols=[6,7,8]) # take 'ATOM' lines, but only column 6-8 as x,y,z coordinates.
 # or
 js.dA('aspirin.pdb',replace={'ATOM':'0'},usecols=[6,7,8])  # replace string by number

data2.txt::

 # this is just a comment or description of the data
 # temp     ;    293
 # pressure ; 1013 14  bar
 # name     ; temp1bsa
 &doit
 0,854979E-01  0,178301E+03  0,383044E+02
 0,882382E-01  0,156139E+03  0,135279E+02
 0,909785E-01  *             0,110681E+02
 0,937188E-01  0,147430E+03  0,954762E+01
 0,964591E-01  0,141615E+03  0,846613E+01
 nan           nan           0

Read by ::

 # ignore is by default '#', so switch it of
 # skip lines with non numbers in data
 # replace some char by others or remove by replacing with empty string ''.
 js.dA('data2.txt',replace={'#':'',';':'',',':'.'},skiplines=[‘*’,'nan'],ignore='' )


pdh format used in some SAXS instruments (first real data point is line 4)::

 SAXS BOX
       2057         0         0         0         0         0         0         0
   0.000000E+00   3.053389E+02   0.000000E+00   1.000000E+00   1.541800E-01
   0.000000E+00   1.332462E+00   0.000000E+00   0.000000E+00   0.000000E+00
 -1.069281E-01   2.277691E+03   1.168599E+00
 -1.037351E-01   2.239132E+03   1.275602E+00
 -1.005422E-01   2.239534E+03   1.068182E+00
 -9.734922E-02   2.219594E+03   1.102175E+00
 ......

Read by::

 # this saves the prepended lines in attribute line_2,...
 empty=js.dA('exampleData/buffer_averaged_corrected_despiked.pdh',usecols=[0,1],lines2parameter=[2,3,4])
 # next just ignores the first lines (and last 50) and uses every second line,
 empty=js.dA('exampleData/buffer_averaged_corrected_despiked.pdh',usecols=[0,1],block=[5,-50,2])

Read csv data by (comma separated list) ::

 js.dA('data2.txt',replace={',':' '})
 # If tabs separate the columns
 js.dA('data2.txt',replace={',':' ','\t':' '})

Creating from numpy arrays
--------------------------
This demonstrates how to create dataArrays form calculated data::

 #
 x=np.r_[0:10:0.5]                 # a list of values
 D,A,q=0.45,0.99,1.2               # parameters
 data=js.dA(np.vstack([x,np.exp(-q**2*D*x)+np.random.rand(len(x))*0.05,x*0+0.05]))
 data.diffusiocoefficient=D
 data.amplitude=A
 data.wavevector=q

 # alternative (diffusion with noise and error )
 data=js.dA(np.c_[x,np.exp(-q**2*D*x)*0.05,x*0+0.05].T)
 f=lambda xx,DD,qq,e:np.exp(-qq**2*DD*xx)+np.random.rand(len(x))*e
 data=js.dA(np.c_[x,f(x,D,q,0.05),np.zeros_like(x)+0.05].T)


Indexing dataArray/dataList and reducing
----------------------------------------
Basic **Slicing** and Indexing/Advanced Indexing/Slicing works as described at
`numpy <https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.indexing.html>`_

This means accessing parts of the dataArray/dataList by indexing with integers, boolean masks or arrays
to extract a subset of the data (returning a copy)

[A,B,C] in the following describes A dataList, B dataArray columns and C values in columns.

::

 i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
 # remove first 2 and last 2 datapoints in all dataArrays
 i6=i5[:,:,:2:-2]
 # remove first column and use 1,2,3 columns in all dataArrays
 i6=i5[:,1:4,:]
 # use each second elelemt in datalist and remove last 2 datapoints in all dataArrays
 i6=i5[::2,:,:-2]
 # You can loop over the dataArrays for individual usage.

**Reducing data** to a lower number of values is done by data.prune (see :py:class:`~.dataList` )

prune reduces e.g by 2000 points by averaging in intervalls to get 100 points.

::

 i7=js.dL(js.examples.datapath+'/a0_336.dat')
 # mean values in interval [0.1,4] with 100 points distributed on logscale
 i7_2=i7.prune(lower=0.1,upper=4,number=100,kind='log') #type='mean' is default

DataList can be **filtered** to use a subset eg to filter for q, temperature,.....

::

 i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
 i6=i5.filter(lambda a:a.q<2)

This demonstrates how to filter data values according to some rule. ::

 x=np.r_[0:10:0.5]
 D,A,q=0.45,0.99,1.2               # parameters
 rand=np.random.randn(len(x))      # the noise on the signal
 data=js.dA(np.vstack([x,np.exp(-q**2*D*x)+rand*0.05,x*0+0.05,rand])) # generate data with noise
 # select like this
 newdata=data[:,data[3]>0]         # take only positive noise in column 3
 newdata=data[:,data.X>2]          # X>2
 newdata=data[:,data.Y<0.9]        # Y<0.9

Fitting experimental data
-------------------------

See :ref:`How to build simple models` for more ways to define models.

Please avoid using lists as parameters as list are used to discriminate
between common parameters and individual fit parameters.

::

 import jscatter as js
 import numpy as np

 # read data
 data=js.dL(js.examples.datapath+'/polymer.dat')
 # merge equal Temperatures each measured with two detector distances
 data.mergeAttribut('Temp',limit=0.01,isort='X')
 # define model
 def gCpower(q,I0,Rg,A,beta,bgr):
     """Model Gaussian chain  + power law and background"""
     gc=js.ff.gaussianChain(q=q,Rg=Rg)
     # add power law and background
     gc.Y=I0*gc.Y+A*q**beta+bgr
     gc.A=A
     gc.I0=I0
     gc.bgr=bgr
     gc.beta=beta
     return gc

 data.makeErrPlot(yscale='l',xscale='l')    # additional errorplot
 data.setlimit(bgr=[0,1])                   # upper and lower soft limit

 # here we use individual parameter for all except a common beta ( no [] )
 # please try removing the [] and play with it :-)
 data.fit(model=gCpower,
          freepar={'I0':[0.1],'Rg':[3],'A':[1],'bgr':[0.01],'beta':-3},
          fixpar={},
          mapNames={'q':'X'},
          condition =lambda a:(a.X>0.05) & (a.X<4))

 # result parameter and error (example)
 data.lastfit.Rg
 data.lastfit.Rg_err

 # save the fit result including parameters, errors and covariance matrix
 data.lastfit.save('polymer_fitDebye.dat')


Plot experimental data and fit result
-------------------------------------
::

 # plot data
 p=js.grace()
 p.plot(data,legend='measured data')
 p.xaxis(min=0.07,max=4,scale='l',label='Q / nm\S-1')
 p.yaxis(scale='l',label='I(Q) / a.u.')
 # plot the result of the fit
 p.plot(data.lastfit,symbol=0,line=[1,1,4],legend='fit Rg=$radiusOfGyration I0=$I0')
 p.legend()

 p1=js.grace()
 # Tempmean because of previous mergeAttribut; otherwise data.Temp
 p1.plot(data.Tempmean,data.lastfit.Rg,data.lastfit.Rg_err)
 p1.xaxis(label='Temperature / C')
 p1.yaxis(label='Rg / nm')

Save data
---------
jscatter saves files in a ASCII format including attributes that can be
reread including the attributes (See first example above and dataArray help).
In this way no information is lost. ::

 data.save('filename.dat')
 # later read them again
 data=js.dA('filename.dat')  # retrieves all attributes

If needed, the raw numpy array can be saved (see numpy.savetxt).
All attribute information is lost. ::

 np.savetxt('test.dat',data.array.T)





