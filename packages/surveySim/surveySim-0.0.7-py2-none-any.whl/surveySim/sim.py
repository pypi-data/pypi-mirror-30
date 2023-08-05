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
__all__=['survey']
__dir__=os.path.abspath(os.path.dirname(__file__))

class survey(dict):
	def __init__(self,name='mySurvey',snTypes=['Ia','Ib','Ic','IIP'],mu=1,zmin=.1,zmax=1.5,dz=.02):
		self.name=name
		self.snTypes=snTypes
		self.magLimits=None
		self.mu=mu
		self.zmin=zmin
		self.zmax=zmax
		self.dz=dz
		self.area=None
		self.filters=None
		self.cadence=None
		self.surveyLength=None
		self.yields=dict([])

	def normalize(self):
		try:
			unit=self.area.unit
		except:
			print('You did not add an astropy unit to your area, assuming square degrees.')
			self.area*=u.deg**2
		self.degArea=self.area.to(u.deg**2)
		self.area=self.area.to(u.sr) #change to steradians

		try:
			unit=self.cadence.unit
		except:
			print('You did not add an astropy unit to your cadence, assuming days.')
			cadence*=u.day
		self.cadence=self.cadence.to(u.day).value
		try:
			unit=self.surveyLength.unit
		except:
			print('You did not add an astropy unit to your survey length, assuming years.')
			self.surveyLength*=u.year
		self.surveyLength=self.surveyLength.to(u.year).value
		if not isinstance(self.filters,(list,tuple)):
			self.filters=[self.filters]
		if not isinstance(self.magLimits,(list,tuple)):
			self.magLimits=[self.magLimits]
		if len(self.filters) != len(self.magLimits):
			print('Your list of bands and list of limiting magnitudes need to be the same length.')
			sys.exit()
		if np.any([x.lower().find('paritel') for x in self.filters]):
			for f in ['J','H','Ks']:
			    wave,trans=np.loadtxt(os.path.join('surveySim','data','bands',str(f[0]).lower()+'Band','paritel'+f+'.dat'),unpack=True)
			    wave*=10000
			    sncosmo.registry.register(sncosmo.Bandpass(wave,trans,name='paritel::'+f.lower()),force=True)

	#these three functions allow you to access the curveDict via "dot" notation
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__
	__getattr__ = dict.__getitem__
	def __str__(self):
		if self.yields:
			print('Survey Name:'+self.name)
			print('		Length: '+str(self.surveyLength)+' Years')
			print('		Cadence: '+str(self.cadence)+' Days')
			print('		Area: '+str(self.degArea.value)+' Square Degrees')
			print('		Redshift Range: '+str(self.zmin)+'-->'+str(self.zmax))
			for band in self.yields.keys():
				print('-------------------')
				snYield=self.yields[band]
				print('Filter='+band+', Limiting Magnitude='+str(self.magLimits[self.filters==band]))
				allSne_lower=[]
				allSne_upper=[]
				allCC_lower=[]
				allCC_upper=[]
				for key in snYield.keys():
					print('		Upper Bound '+key+':'+str(np.round(np.sum(snYield[key]['upper']),2)))
					print('		Lower Bound '+key+':'+str(np.round(np.sum(snYield[key]['lower']),2)))
					allSne_lower.append(np.sum(snYield[key]['lower']))
					allSne_upper.append(np.sum(snYield[key]['upper']))
					if key!='Ia':
						allCC_upper.append(np.sum(snYield[key]['upper']))
						allCC_lower.append(np.sum(snYield[key]['lower']))
				print
				print('		Total Ia Upper Bound:'+str(np.round(np.sum(snYield['Ia']['upper']),2)))
				print('		Total Ia Lower Bound:'+str(np.round(np.sum(snYield['Ia']['lower']),2)))
				print('		Total CC Upper Bound:'+str(np.round(np.sum(allCC_upper),2)))
				print('		Total CC Lower Bound:'+str(np.round(np.sum(allCC_lower),2)))
				print
				print('		Total Lower Bound:'+str(np.round(np.sum(allSne_lower),2)))
				print('		Total Upper Bound:'+str(np.round(np.sum(allSne_upper),2)))
		else:
			print('No yields calculated.')
		return('-------------------')

	def unTargetedSurvey(self,absolutes={'Ia':-19.25,'Ib':-17.45,'Ic':-17.66,'IIP':-16.75},Ia_av=.3,CC_av=.9,zpsys='ab'): #t_obs in years
		self.normalize()
		redshifts,N_CC_upper,N_CC_lower,N_Ia_upper,N_Ia_lower=_getSNexploding(self.surveyLength,self.area,self.dz,self.zmin,self.zmax)
		#filterDict=dict([])
		for i in range(len(self.filters)):
			_SNfractions=_SNfraction(self.snTypes,self.filters[i],self.magLimits[i],redshifts,self.cadence,absolutes,self.mu,Ia_av,CC_av,zpsys)
			snYields=dict([])
			for snClass in _SNfractions.keys():
				if snClass=='Ia':
					snYields[snClass]={'upper':_SNfractions[snClass]*N_Ia_upper,'lower':_SNfractions[snClass]*N_Ia_lower}
				else:
					snYields[snClass]={'upper':_SNfractions[snClass]*N_CC_upper,'lower':_SNfractions[snClass]*N_CC_lower}
			self.yields[self.filters[i]]=snYields

	def plotHist(self,band,snClass,bound='lower',facecolor='green',showPlot=True,savePlot=False):
		fig=plt.figure()
		ax=fig.gca()
		plt.bar(np.arange(self.zmin,self.zmax,self.dz),height=self.yields[band][snClass][bound]/self.surveyLength, width=self.dz,facecolor=facecolor)
		plt.xlabel(r'$Redshift$',size=16)
		plt.ylabel('$Number \ of \ SN (yr^{-1})$',size=16)
		plt.title('Lower Limit SN Yield--Band='+band+'--Mag Limit='+str(self.magLimits[self.filters==band])+'--Type '+snClass+'--mu='+str(self.mu),size=12)
		plt.grid(True)
		if savePlot:
			plt.savefig(os.path.join(bound+'_Type'+snClass+'.pdf'),format='pdf',overwrite=True)
		if showPlot:
			plt.show()
		plt.close()
		return
		

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


def _SNfraction(classes,band,magLimit,redshifts,cadence,absolutes,mu,Ia_av,CC_av,zpsys):
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
		for i in range(len(redshifts)):
			model=sncosmo.Model(sne[snClass])
			model.set(z=redshifts[i])
			model.set_source_peakabsmag(absolute,'bessellb',zpsys)
			#model.set(t0=-_snMax(model,band,zpsys))
			#if snClass=='Ia':
			#	sncosmo.plot_lc(model=model,bands=['sdss::i'])
			#	plt.show()
			#	sys.exit()
			t0=_snMax(model,band,zpsys)
			mags=model.bandmag(band,zpsys,np.append(np.arange(t0-(cadence+1),t0,1),np.arange(t0,t0+cadence+1,1)))
			if len(mags[mags<=magLimit])==0:
				fractions=np.append(fractions,[0 for j in range(len(redshifts)-i)])
				break
			else:
				if len(mags[mags<=magLimit])<cadence:
					fractions.append(float(len(mags[mags<=magLimit])/cadence))
				else:
					fractions.append(1)
		resultsDict[snClass]=np.array(fractions)
	return(resultsDict)






	

def targetedSurvey(filename):
	table=ascii.read(filename)
	outputTable=Table()
	#for row in table:



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










