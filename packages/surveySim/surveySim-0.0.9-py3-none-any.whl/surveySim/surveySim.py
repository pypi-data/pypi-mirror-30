import math,os,sncosmo,sys
import astropy.constants as constants
import numpy as np
from astropy.io import ascii
from scipy .interpolate import interp1d
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.cosmology import WMAP9 as cosmo

__H0__=73.24

for f in ['J','H','Ks']:
	wave,trans=np.loadtxt(os.path.join('/Users','jpierel','rodney','snsedextend','snsedextend','data','bands',str(f[0]).lower()+'Band','paritel'+f+'.dat'),unpack=True)
	wave*=10000
	sncosmo.registry.register(sncosmo.Bandpass(wave,trans,name='paritel::'+f.lower()),force=True)

def _getSFR(z,z0=1.243,A=-.997,B=.241,C=.18):
	return(C/(10**(A*(z-z0))+10**(B*(z-z0))))

def getSNR(z,kcc_lower=5E-3,kcc_upper=10E-3):
	CSFR=_getSFR(z)

	cc_lower=kcc_lower*CSFR #Mpc^-3
	cc_upper=kcc_upper*CSFR
	if z<1:
		theta=.35
	else:
		theta=.07
	ia_lower=1.035*kcc_lower*theta*CSFR
	ia_upper=1.035*kcc_upper*theta*CSFR
	return(ia_lower,ia_upper,cc_lower,cc_upper)


def getSNexploding(t_obs,area,dz,zmin,zmax):
	redshifts=np.arange(zmin,zmax,dz)
	N_CC_upper=[]
	N_CC_lower=[]
	N_Ia_upper=[]
	N_Ia_lower=[]
	for z in np.arange(zmin,zmax,dz):
		dr=cosmo.comoving_distance(z+dz).value-cosmo.comoving_distance(z).value#megaparsecs
		dr=1
		d=cosmo.comoving_distance(z).value#megaparsecs
		dV=4*math.pi*d**2*dr
		surveyV=(area/(4*math.pi*u.sr))*dV
		ia_lower,ia_upper,cc_lower,cc_upper=getSNR(z)
		N_CC_upper.append(cc_upper*surveyV*(t_obs/(1+z)))
		N_CC_lower.append(cc_lower*surveyV*(t_obs/(1+z)))
		N_Ia_upper.append(ia_upper*surveyV*(t_obs/(1+z)))
		N_Ia_lower.append(ia_lower*surveyV*(t_obs/(1+z)))
	return(redshifts,np.array(N_CC_upper),np.array(N_CC_lower),np.array(N_Ia_upper),np.array(N_Ia_lower))


def SNfraction(band,magLimit,redshifts,cadence,absolute_Ia,absolute_CC,mu,Ia_av,CC_av,zpsys):

	classes=['Ia','IIP','Ib','Ic']
	mod,types=np.loadtxt('../snsedextend/bianco/models.ref',dtype='str',unpack=True)
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
			absolute=absolute_Ia
			magLimit-=Ia_av
		else:
			absolute=absolute_CC
			magLimit-=CC_av
		magLimit+=2.5*np.log10(mu)

		fractions=[]
		for redshift in redshifts:
			
			model=sncosmo.Model(sne[snClass])#,effects=effects,effect_names=effect_names,effect_frames=effect_frames)
			model.set(z=redshift)
			model.set_source_peakabsmag(absolute,'bessellb','ab')
			t0=0
			if model.bandmag(band,zpsys,t0)>magLimit:
				fractions.append(0)
			else:
				while t0>=model.mintime() and t0<=cadence and model.bandmag(band,zpsys,t0)<=magLimit:
					t0-=1
				lowerT=t0+1
				t0=0
				while t0>=model.mintime() and t0 <= cadence and model.bandmag(band,zpsys,t0)<=magLimit:
					t0+=1
				upperT=t0-1
				totalT=math.fabs(lowerT)+upperT
				if totalT>=cadence:
					fractions.append(1)
				else:
					fractions.append(float(totalT/cadence))
		resultsDict[snClass]=np.array(fractions)
	return(resultsDict)




def surveySim(area,deltaT,filterList,magLimitList,t_obs=1,galFile=None,dz=.1,zmin=.2,zmax=1.21,absolute_Ia=-19.3,absolute_CC=-17,mu=1,Ia_av=.3,CC_av=.9,zpsys='ab'): #t_obs in years
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
		redshifts,N_CC_upper,N_CC_lower,N_Ia_upper,N_Ia_lower=getSNexploding(t_obs,area,dz,zmin,zmax)
		for i in range(len(filterList)):
			SNfractions=SNfraction(filterList[i],magLimitList[i],redshifts,deltaT,absolute_Ia,absolute_CC,mu,Ia_av,CC_av,zpsys)
		snYields=dict([])
		for snClass in SNfractions.keys():

			if snClass=='Ia':
				snYields[snClass]={'upper':SNfractions[snClass]*N_Ia_upper,'lower':SNfractions[snClass]*N_Ia_lower}
			else:
				snYields[snClass]={'upper':SNfractions[snClass]*N_CC_upper,'lower':SNfractions[snClass]*N_CC_lower}
	return(snYields)
			

def main():
	magLimit=22.5
	mu=5
	snYield=surveySim(10*u.deg**2,30,['bessellv'],[magLimit],mu=mu)
	fig=plt.figure()
	ax=fig.gca()
	for snClass in snYield.keys():
		plt.bar(np.arange(.2,1.21,.1),height=snYield[snClass]['lower'], width=.1,facecolor='green')
		plt.xlabel(r'$Redshift$',size=16)
		plt.ylabel('$Number \ of \ SN (yr^{-1})$',size=16)
		plt.title('Lower Limit SN Yield--V Band--Mag Limit='+str(magLimit)+'--Type '+snClass+'--mu='+str(mu),size=12)
		plt.grid(True)
		plt.savefig(os.path.join('figs','lower_Type'+snClass+'.pdf'),format='pdf',overwrite=True)
		plt.close()
		plt.bar(np.arange(.2,1.21,.1),height=snYield[snClass]['upper'], width=.1,facecolor='green')
		plt.xlabel(r'$Redshift$',size=16)
		plt.ylabel('$Number \ of \ SN (yr^{-1})$',size=16)
		plt.title('Upper Limit SN Yield--V Band--Mag Limit='+str(magLimit)+'--Type '+snClass+'--mu='+str(mu),size=12)
		plt.grid(True)
		plt.savefig(os.path.join('figs','upper_Type'+snClass+'.pdf'),format='pdf',overwrite=True)
		plt.close()

if __name__=='__main__':
	main()











