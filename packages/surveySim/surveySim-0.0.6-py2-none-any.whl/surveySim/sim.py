import math,os,sncosmo,sys,warnings
import astropy.constants as constants
import numpy as np
from astropy.io import ascii
from astropy.table import Table
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.cosmology import WMAP9 as cosmo

warnings.simplefilter('ignore')
__all__=['unTargetedSurvey','targetedSurvey','plotHist']
__dir__=os.path.abspath(os.path.dirname(__file__))

def _ccm_extinction(wave, ebv, r_v=3.1):
    """
    (Private)
    Heler function for dereddening.

    """
    scalar = not np.iterable(wave)
    if scalar:
        wave = np.array([wave], float)
    else:
        wave = np.array(wave, float)

    x = 10000.0/wave
    npts = wave.size
    a = np.zeros(npts, float)
    b = np.zeros(npts, float)

    #Infrared
    good = np.where( (x > 0.3) & (x < 1.1) )
    a[good] = 0.574 * x[good]**(1.61)
    b[good] = -0.527 * x[good]**(1.61)

    # Optical & Near IR
    good = np.where( (x  >= 1.1) & (x < 3.3) )
    y = x[good] - 1.82

    c1 = np.array([ 1.0 , 0.104,   -0.609,    0.701,  1.137,
                    -1.718,   -0.827,    1.647, -0.505 ])
    c2 = np.array([ 0.0,  1.952,    2.908,   -3.989, -7.985,
                    11.102,    5.491,  -10.805,  3.347 ] )

    a[good] = np.polyval(c1[::-1], y)
    b[good] = np.polyval(c2[::-1], y)

    # Mid-UV
    good = np.where( (x >= 3.3) & (x < 8) )
    y = x[good]
    F_a = np.zeros(np.size(good),float)
    F_b = np.zeros(np.size(good),float)
    good1 = np.where( y > 5.9 )

    if np.size(good1) > 0:
        y1 = y[good1] - 5.9
        F_a[ good1] = -0.04473 * y1**2 - 0.009779 * y1**3
        F_b[ good1] =   0.2130 * y1**2  +  0.1207 * y1**3

    a[good] =  1.752 - 0.316*y - (0.104 / ( (y-4.67)**2 + 0.341 )) + F_a
    b[good] = -3.090 + 1.825*y + (1.206 / ( (y-4.62)**2 + 0.263 )) + F_b

    # Far-UV
    good = np.where( (x >= 8) & (x <= 11) )
    y = x[good] - 8.0
    c1 = [ -1.073, -0.628,  0.137, -0.070 ]
    c2 = [ 13.670,  4.257, -0.420,  0.374 ]
    a[good] = np.polyval(c1[::-1], y)
    b[good] = np.polyval(c2[::-1], y)

    # Defining the Extinction at each wavelength
    a_v = r_v * ebv
    a_lambda = a_v * (a + b/r_v)
    if scalar:
        a_lambda = a_lambda[0]
    return a_lambda

def _getSFR(z,z0=1.243,A=-.997,B=.241,C=.18):
	return(C/(10**(A*(z-z0))+10**(B*(z-z0))))

def _getTheta1(z):
	func=interp1d([0,.25,.5,.75,1,1.25],[.25,.17,.16,.155,.15,.15])
	return(func(z)/(1-func(z)))

def _getTheta2(z):
	func=interp1d([1.25,1.7],[.15,.08])
	return(func(z)/(1-func(z)))

def _getSNR(z,kcc_lower=5,kcc_upper=10):
	CSFR=_getSFR(z)
	cc_lower=kcc_lower*1E-3*CSFR #Mpc^-3
	cc_upper=kcc_upper*1E-3*CSFR
	if z<=1.25:
		theta=float(_getTheta1(z))
	elif z<=1.7:
		theta=float(_getTheta2(z))
	else:
		theta=float(.05/(1-.05))
	
	ia_lower=1.035*kcc_lower*theta*1E-3*CSFR
	ia_upper=1.035*kcc_upper*theta*1E-3*CSFR
	return(ia_lower,ia_upper,cc_lower,cc_upper)


def _getSNexploding(t_obs,area,dz,zmin,zmax):
	redshifts=np.arange(zmin,zmax,dz)
	N_CC_upper=[]
	N_CC_lower=[]
	N_Ia_upper=[]
	N_Ia_lower=[]
	for z in np.arange(zmin,zmax,dz):
		dV=cosmo.comoving_volume(z+dz).value-cosmo.comoving_volume(z).value#megaparsecs
		surveyV=(area/(4*math.pi*u.sr))*dV
		ia_lower,ia_upper,cc_lower,cc_upper=_getSNR(z)
		N_CC_upper.append(cc_upper*surveyV*(t_obs/(1+z)))
		N_CC_lower.append(cc_lower*surveyV*(t_obs/(1+z)))
		N_Ia_upper.append(ia_upper*surveyV*(t_obs/(1+z)))
		N_Ia_lower.append(ia_lower*surveyV*(t_obs/(1+z)))
	return(redshifts,np.array(N_CC_upper),np.array(N_CC_lower),np.array(N_Ia_upper),np.array(N_Ia_lower))


def _snMax(model,band,zpsys,tStep=1):
	tgrid=np.append(np.arange(model.mintime(),0,tStep),np.arange(0,model.maxtime(),tStep))
	mags=model.bandmag(band,zpsys,tgrid)
	tgrid=tgrid[~np.isnan(mags)]
	mags=mags[~np.isnan(mags)]
	return(tgrid[mags==np.min(mags)][0])


def _SNfraction(band,magLimit,redshifts,cadence,absolutes,mu,Ia_av,CC_av,zpsys):

	classes=['Ia','IIP','Ib','Ic']
	mod,types=np.loadtxt(os.path.join(__dir__,'data','models.ref'),dtype='str',unpack=True)
	modDict={mod[i]:types[i] for i in range(len(mod))}
	sne=dict([])
	for sn in ['Ib','Ic','IIP']:
		mods = [x for x in sncosmo.models._SOURCES._loaders.keys() if x[0] in modDict.keys() and modDict[x[0]] ==sn] #need sn to be list of models of that type, woops
		mods = {x[0] if isinstance(x,(tuple,list)) else x for x in mods}
		sne[sn]=list(mods)[1]

	sne['Ia']='salt2'
	resultsDict=dict([])
	for snClass in classes:
		if snClass=='Ia':
			magLimit-=_ccm_extinction(sncosmo.get_bandpass(band).wave_eff,Ia_av/3.1)
		else:
			magLimit-=_ccm_extinction(sncosmo.get_bandpass(band).wave_eff,CC_av/3.1)
		absolute=absolutes[snClass]
		magLimit+=2.5*np.log10(mu)

		fractions=[]
		for redshift in redshifts:
			model=sncosmo.Model(sne[snClass])
			model.set(z=redshift)
			model.set_source_peakabsmag(absolute,'bessellb',zpsys)
			#model.set(t0=-_snMax(model,band,zpsys))
			#if snClass=='Ia':
			#	sncosmo.plot_lc(model=model,bands=['sdss::i'])
			#	plt.show()
			#	sys.exit()
			t0=_snMax(model,band,zpsys)
			mags=model.bandmag(band,zpsys,np.append(np.arange(model.mintime(),t0,1),np.arange(t0,model.maxtime(),1)))
			if len(mags[mags<=magLimit])==0:
				fractions.append(0)
			else:
				if len(mags[mags<=magLimit])<cadence:
					fractions.append(float(len(mags[mags<=magLimit])/cadence))
				else:
					fractions.append(1)
		resultsDict[snClass]=np.array(fractions)
	return(resultsDict)




def unTargetedSurvey(area,deltaT,filterList,magLimitList,t_obs=1,galFile=None,dz=.1,zmin=.2,zmax=1.21,
	absolutes={'Ia':-19.25,'Ib':-17.45,'Ic':-17.66,'IIP':-16.75},mu=1,Ia_av=.3,CC_av=.9,zpsys='ab'): #t_obs in years
	try:
		unit=area.unit
	except:
		print('You did not add an astropy unit to your area, assuming square degrees.')
		area*=u.deg**2
	area=area.to(u.sr) #change to steradians
	if not isinstance(filterList,(list,tuple)):
		filterList=[filterList]
	if not isinstance(magLimitList,(list,tuple)):
		magLimitList=[magLimitList]
	if not galFile:
		if len(filterList) != len(magLimitList):
			print('Your list of bands and list of limiting magnitudes need to be the same length.')
			sys.exit()
		redshifts,N_CC_upper,N_CC_lower,N_Ia_upper,N_Ia_lower=_getSNexploding(t_obs,area,dz,zmin,zmax)

		for i in range(len(filterList)):
			_SNfractions=_SNfraction(filterList[i],magLimitList[i],redshifts,deltaT,absolutes,mu,Ia_av,CC_av,zpsys)
		snYields=dict([])
		for snClass in _SNfractions.keys():

			if snClass=='Ia':
				snYields[snClass]={'upper':_SNfractions[snClass]*N_Ia_upper,'lower':_SNfractions[snClass]*N_Ia_lower}
			else:
				snYields[snClass]={'upper':_SNfractions[snClass]*N_CC_upper,'lower':_SNfractions[snClass]*N_CC_lower}
	return(snYields)

def targetedSurvey(filename):
	table=ascii.read(filename)
	outputTable=Table()
	#for row in table:

def plotHist(snYield,snClass,magLimit,mu,zmin,zmax,dz,bound='lower'):
	fig=plt.figure()
	ax=fig.gca()
	plt.bar(np.arange(zmin,zmax,dz),height=snYield[snClass][bound], width=dz,facecolor='green')
	plt.xlabel(r'$Redshift$',size=16)
	plt.ylabel('$Number \ of \ SN (yr^{-1})$',size=16)
	plt.title('Lower Limit SN Yield--V Band--Mag Limit='+str(magLimit)+'--Type '+snClass+'--mu='+str(mu),size=12)
	plt.grid(True)
	plt.savefig(os.path.join('figs',bound+'_Type'+snClass+'.pdf'),format='pdf',overwrite=True)
	plt.close()

'''
def main():
	magLimit=22.5
	mu=5
	snYield=surveySim(10*u.deg**2,30,['bessellv'],[magLimit],mu=mu)
	for snClass in snYield.keys():
		plotHist(snClass,magLimit,mu,.2,1.21,.1,bound='lower')
		plotHist(snClass,magLimit,mu,.2,1.21,.1,bound='upper')
		
if __name__=='__main__':
	main()
'''










