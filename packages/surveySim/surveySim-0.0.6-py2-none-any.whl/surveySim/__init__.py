import numpy as np
import sncosmo,os
for f in ['J','H','Ks']:
    wave,trans=np.loadtxt(os.path.join('surveySim','data','bands',str(f[0]).lower()+'Band','paritel'+f+'.dat'),unpack=True)
    wave*=10000
    sncosmo.registry.register(sncosmo.Bandpass(wave,trans,name='paritel::'+f.lower()),force=True)
from .sim import *
