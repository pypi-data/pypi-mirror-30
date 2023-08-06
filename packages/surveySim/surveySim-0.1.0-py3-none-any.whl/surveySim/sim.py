from __future__ import print_function
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
__all__=['survey','load_example_data']
__dir__=os.path.abspath(os.path.dirname(__file__))


class survey(dict):
    """
    A survey simulator class that allows you to find SN yields.

    :param name: The name of your survey
    :type name: str
    :param snTypes: A list of the supernova Types you want to find yields for
    :type snTypes: list (of str)
    :param magLimits: A list, corresponding to filters, of limiting magnitudes
    :type magLimits: list (of float)
    :param mu: Magnification parameter
    :type mu: float
    :param zmin: Minimum Redshift
    :type zmin: float
    :param zmax: Maximum Redshift
    :type zmax: float
    :param dz: Redshift stepsize
    :type dz: float
    :param area: Survey area (assumed square degrees)
    :type area: float
    :param filters: List of filters corresponding to limiting magnitudes list
    :type filters: list (of str)
    :param cadence: Cadence of survey observations (assumed days)
    :type cadence: float
    :param surveyLength: Length of survey (assumed years)
    :type surveyLength: float
    :param galaxies: For a targeted survey, table containing galaxy data.
    :type galaxies: astropy Table
    :returns: None
    """
    def __init__(self,name='mySurvey',snTypes=['Ia','Ib','Ic','IIP'],zmin=.1,zmax=1.5,dz=.02):
        self.name=name
        self.snTypes=snTypes
        self.magLimits=None
        self.mu=None
        self.zmin=zmin
        self.zmax=zmax
        self.dz=dz
        self.area=None
        self.filters=None
        self.cadence=None
        self.surveyLength=None
        self.yields=dict([])
        self.galaxies=None
        self.tobs=None
        self.ncc=None
        self.errncc=None
        self.nia=None
        self.errnia=None
        self.verbose=False

    def _normalize(self,unTargeted=True):
        if unTargeted:
            try:
                unit=self.area.unit
            except:
                print('You did not add an astropy unit to your area, assuming square degrees.')
                self.area*=u.deg**2
            self.degArea=self.area.to(u.deg**2)
            self.area=self.area.to(u.sr) #change to steradians
            if not self.mu:
                print('No Magnification information found, assuming mu=1')
                self.mu=1
        else:
            for col in self.galaxies.colnames:
                if col != col.lower():
                    self.galaxies.rename_column(col,col.lower())
            if 'redshift' in self.galaxies.colnames:
                self.galaxies.rename_column('redshift','z')
            if 'zs' in self.galaxies.colnames:
                self.galaxies.rename_column('zs', 'z')
            if 'z' not in self.galaxies.colnames:
                print('Could not find redshift in your column names, rename to "z" if it exists')
                import pdb; pdb.set_trace()
                sys.exit(1)
            if not self.mu:
                if 'mu' not in self.galaxies.colnames:
                    print('No Magnification information found, assuming mu=1')
                    self.mu=1
                else:
                    self.mu=np.array(self.galaxies['mu'])
            if 'tobs' in self.galaxies.colnames:
                self.tobs = np.array(self.galaxies['tobs'])
            if 'n_cc' in self.galaxies.colnames:
                if 'ncc_err' not in self.galaxies.colnames:
                    self.galaxies['ncc_err']=.1*self.galaxies['n_cc']
            elif 'sfr' not in self.galaxies.colnames:
                print('SFR not found, change column name to "SFR" if it exists')
                sys.exit(1)
            if 'n_ia' in self.galaxies.colnames:
                if 'nia_err' not in self.galaxies.colnames:
                    self.galaxies['nia_err']=.1*self.galaxies['n_ia']
            elif 'sfr' not in self.galaxies.colnames:
                print('SFR not found, change column name to "SFR" if it exists')
                sys.exit(1)

            self.galaxies.sort('z')

        try:
            unit=self.cadence.unit
        except:
            print('You did not add an astropy unit to your cadence, assuming days.')
            self.cadence*=u.day
        self.cadence=self.cadence.to(u.day).value
        try:
            unit=self.surveyLength.unit
        except:
            print('You did not add an astropy unit to your survey length, assuming years.')
            self.surveyLength*=u.year
        #TODO: when user provides tobs in input data file, don't require surveylength
        if self.tobs is not None:
            self.surveyLength = self.tobs*u.year

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
                wave,trans=np.loadtxt(
                    os.path.join(__dir__, 'data','bands',
                                 str(f[0]).lower()+'Band','paritel'+f+'.dat'),
                    unpack=True)
                wave*=10000
                sncosmo.registry.register(sncosmo.Bandpass(wave,trans,name='paritel::'+f.lower()),force=True)



    #these three functions allow you to access the curveDict via "dot" notation
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getattr__ = dict.__getitem__
    def __str__(self):
        """
        Replaces the printing function for this class

        """
        verbose=self.verbose
        if self.yields:
            if verbose:
                # TODO : handle different survey lengths for different galaxies
                print('Survey Name: '+self.name)
                if np.median(self.surveyLength) == 1:
                    print('     Length: '+str(np.median(self.surveyLength))+' Year')
                else:
                    print('     Length: '+str(np.median(self.surveyLength))+' Years')
                print('     Cadence: '+str(self.cadence)+' Days')
                if not self.galaxies:
                    print('     Area: '+str(self.degArea.value)+' Square Degrees')
                    print('     Redshift Range: '+str(self.zmin)+'-->'+str(self.zmax))
                else:
                    print('     Number of Galaxies: '+str(len(self.galaxies)))
                    print('     Redshift Range: '+str(np.round(np.min(self.galaxies['z']),2))+'-->'+str(np.round(np.max(self.galaxies['z']),2)))
            for band in self.yields.keys():
                if verbose:
                    print('-------------------')
                snYield=self.yields[band]
                if verbose:
                    print('Filter='+band+', Limiting Magnitude='+str(self.magLimits[self.filters==band])+'('+self.zpsys+')')
                    print()
                allSne_lower=[]
                allSne_upper=[]
                allCC_lower=[]
                allCC_upper=[]
                for key in snYield.keys():
                    if verbose: print('     Upper Bound '+key+':'+str(np.round(np.sum(snYield[key]['upper']),2)))
                    if verbose: print('     Lower Bound '+key+':'+str(np.round(np.sum(snYield[key]['lower']),2)))
                    allSne_lower.append(np.sum(snYield[key]['lower']))
                    allSne_upper.append(np.sum(snYield[key]['upper']))
                    if key!='Ia':
                        allCC_upper.append(np.sum(snYield[key]['upper']))
                        allCC_lower.append(np.sum(snYield[key]['lower']))
                if verbose:
                    print()
                    print('     Total Ia Upper Bound:'+str(np.round(np.sum(snYield['Ia']['upper']),2)))
                    print('     Total Ia Lower Bound:'+str(np.round(np.sum(snYield['Ia']['lower']),2)))
                    print('     Total CC Upper Bound:'+str(np.round(np.sum(allCC_upper),2)))
                    print('     Total CC Lower Bound:'+str(np.round(np.sum(allCC_lower),2)))
                    print()
                    print('     Total Lower Bound:'+str(np.round(np.sum(allSne_lower),2)))
                    print('     Total Expectation:'+str(np.round((np.sum(allSne_lower) + np.sum(allSne_upper))/2.,2)))
                    print('     Total Upper Bound:'+str(np.round(np.sum(allSne_upper),2)))
                    print('-------------------')
                else:
                    print(band+'  ' + str(self.magLimits[self.filters==band]) + '    ' +
                          str(np.round(np.sum(snYield['Ia']['lower']),2)) + '   ' +
                          str(np.round(np.sum(snYield['Ia']['upper']),2)) + '     ' +
                          str(np.round(np.sum(allCC_lower),2)) + '   ' +
                          str(np.round(np.sum(allCC_upper),2)) + '     ' +
                          str(np.round(np.sum(allSne_lower), 2)) + '  ' +
                          str(np.round(np.sum(allSne_upper), 2)) )
        else:
            print('No yields calculated.')
        return('')

    def unTargetedSurvey(self,absolutes={'Ia':-19.25,'Ib':-17.45,'Ic':-17.66,'IIP':-16.75},Ia_av=.3,CC_av=.9,zpsys='ab'): #t_obs in years
        """
        Run an untargeted survey from a survey object.

        :param absolutes: Dictionary containing absolute magnitudes for each SN class.
        :type absolutes: dict
        :param Ia_av: A_v for Ia's (Rodney et al.)
        :type Ia_av: float
        :param CC_av: A_v for CC's (Rodney et al.)
        :type CC_av: float
        :returns: None
        """
        self._normalize(unTargeted=True)
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

    def targetedSurvey(self,absolutes={'Ia':-19.25,'Ib':-17.45,'Ic':-17.66,'IIP':-16.75,'IIL':-17,'IIn':-17},Ia_av=.3,CC_av=.9,zpsys='ab'):
        """
        Run a targeted survey from a survey object.

        :param absolutes: Dictionary containing absolute magnitudes for each SN class.
        :type absolutes: dict
        :param Ia_av: A_v for Ia's (Rodney et al.)
        :type Ia_av: float
        :param CC_av: A_v for CC's (Rodney et al.)
        :type CC_av: float
        :returns: None
        """
        self._normalize(unTargeted=False)
        self.zpsys=zpsys
        kcc_lower=5
        kcc_upper=10


        #table=ascii.read(filename)
        thetas=[]
        for row in self.galaxies:
            if row['z']<=1.25:
                thetas.append(float(_getTheta1(row['z'])))
            elif row['z']<=1.7:
                thetas.append(float(_getTheta2(row['z'])))
            else:
                thetas.append(float(.05/(1-.05)))
        self.galaxies['theta']=np.array(thetas)

        if 'n_cc' in self.galaxies.colnames:
            self.galaxies['SNR_CC_upper'] = self.galaxies['n_cc'] + self.galaxies['ncc_err']
            self.galaxies['SNR_CC_lower'] = self.galaxies['n_cc'] - self.galaxies['ncc_err']

        else:
            self.galaxies['SNR_CC_upper'] = kcc_upper * 1E-3 * self.galaxies['sfr']
            self.galaxies['SNR_CC_lower'] = kcc_lower * 1E-3 * self.galaxies['sfr']

        if 'n_ia' in self.galaxies.colnames:
            self.galaxies['SNR_Ia_upper'] = self.galaxies['n_ia'] + self.galaxies['nia_err']
            self.galaxies['SNR_Ia_lower'] = self.galaxies['n_ia'] - self.galaxies['nia_err']
        elif 'mass' in self.galaxies.colnames:
            self.galaxies['SNR_Ia_lower']=1.05E-10*self.galaxies['mass']**.68+kcc_lower*self.galaxies['theta']*1E-3*self.galaxies['sfr']
            self.galaxies['SNR_Ia_upper']=1.05E-10*self.galaxies['mass']**.68+kcc_upper*self.galaxies['theta']*1E-3*self.galaxies['sfr']
        else:
            print('Did not find galaxy mass column, change name to "mass" if it exists, otherwise using scale factor.')
            self.galaxies['SNR_Ia_lower']=1.035*kcc_lower*self.galaxies['theta']*1E-3*self.galaxies['sfr']
            self.galaxies['SNR_Ia_upper']=1.035*kcc_upper*self.galaxies['theta']*1E-3*self.galaxies['sfr']


        for i in range(len(self.filters)):
            _SNfractions=_SNfraction(self.snTypes,self.filters[i],self.magLimits[i],self.galaxies['z'],self.cadence,absolutes,self.mu,Ia_av,CC_av,zpsys)
            snYields=dict([])
            for snClass in _SNfractions.keys():
                if snClass=='Ia':
                    snYields[snClass]={
                        'upper':_SNfractions[snClass] * \
                                self.galaxies['SNR_Ia_upper'] * \
                                self.surveyLength,
                        'lower':_SNfractions[snClass] * \
                                self.galaxies['SNR_Ia_lower'] * \
                                self.surveyLength
                    }
                else:
                    snYields[snClass]={
						'upper':_SNfractions[snClass] * \
								self.galaxies['SNR_CC_upper'] * \
								self.surveyLength,
						'lower':_SNfractions[snClass] * \
								self.galaxies['SNR_CC_lower'] * \
								self.surveyLength
					}
            self.yields[self.filters[i]]=snYields


    def plotHist(self,band,snClass,bound='Lower',
                 facecolor='green',showPlot=True,savePlot=False,
                 **kwargs):
        """
        Plot a histogram of SN yields results.

        :param band: Filter you would like to plot.
        :type band: str
        :param snClass: The SN class you would like to plot.
        :type snClass: str
        :param bound: Plot the lower or upper bound (default lower)
        :type bound: str
        :param showPlot: Show plot?
        :type showPlot: Boolean
        :param savePlot: Save plot?
        :type savePlot: Boolean
        :returns: None
        """
        fig=plt.figure()
        ax=fig.gca()
        if self.galaxies:
            plt.bar(self.galaxies['z'],
                    height=self.yields[band][snClass][bound.lower()]/self.surveyLength,
                    width=0.02, **kwargs)
            if isinstance(self.mu,np.ndarray):
                plt.title('Targeted Survey '+bound+' Limit SN Yield--Band='+band+'--Mag Limit='+str(self.magLimits[self.filters==band])+'--Type '+snClass+'--Average mu='+str(np.round(self.mu.mean(),1)),size=14)
            else:
                plt.title('Targeted Survey '+bound+' Limit SN Yield--Band='+band+'--Mag Limit='+str(self.magLimits[self.filters==band])+'--Type '+snClass+'--mu='+str(self.mu),size=14)
            tType='target'
        else:
            plt.bar(np.arange(self.zmin,self.zmax,self.dz),height=self.yields[band][snClass][bound.lower()]/self.surveyLength, width=self.dz,facecolor=facecolor, **kwargs)
            plt.title('Untargeted Survey '+bound+' Limit SN Yield--Band='+band+'--Mag Limit='+str(self.magLimits[self.filters==band])+'--Type '+snClass+'--mu='+str(self.mu),size=14)
            tType='unTarget'
        plt.xlabel(r'$Redshift$',size=16)
        plt.ylabel('$Number \ of \ SN (yr^{-1})$',size=16)

        plt.grid(True)
        if savePlot:
            plt.savefig(os.path.join(tType+bound.lower()+'_Type'+snClass+'.pdf'),format='png',overwrite=True)
        if showPlot:
            plt.show()
        plt.close()



def load_example_data():	
    return(ascii.read(os.path.join(__dir__,'data','examples','galaxies.dat')))

def _ccm_extinction(wave, ebv, r_v=3.1):
    """
    (Private)
    Helper function for dereddening.

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
    """
    (Private)
    Heler function for getting CSFR.

    """
    return(C/(10**(A*(z-z0))+10**(B*(z-z0))))

def _getTheta1(z):
    """
    (Private)
    Heler function for SNR_Ia/SNR_CC.

    """
    func=interp1d([0,.25,.5,.75,1,1.25],[.25,.17,.16,.155,.15,.15])
    return(func(z)/(1-func(z)))

def _getTheta2(z):
    """
    (Private)
    Heler function for SNR_Ia/SNR_CC.

    """
    func=interp1d([1.25,1.7],[.15,.08])
    return(func(z)/(1-func(z)))

def _getSNR(z,kcc_lower=5,kcc_upper=10):
    """
    (Private)
    Heler function for SNRs.

    """
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
    """
    (Private)
    Heler function for N_exp.

    """
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
    """
    (Private)
    Heler function that returns peak of lightcurve in current band.

    """
    tgrid=np.append(np.arange(model.mintime(),0,tStep),np.arange(0,model.maxtime(),tStep))
    mags=model.bandmag(band,zpsys,tgrid)
    tgrid=tgrid[~np.isnan(mags)]
    mags=mags[~np.isnan(mags)]
    return(tgrid[mags==np.min(mags)][0])


def _SNfraction(classes,band,magLimit,redshifts,cadence,absolutes,mu,Ia_av,CC_av,zpsys):
    """
    (Private)
    Heler function for N_frac

    """
    types,mods=np.loadtxt(os.path.join(__dir__,'data','seds.ref'),dtype='str',unpack=True)

    sne={types[i]:mods[i] for i in range(len(types))}
    resultsDict=dict([])

    for snClass in classes:
        tempmagLimit=magLimit
        if snClass=='Ia':
            tempmagLimit-=_ccm_extinction(sncosmo.get_bandpass(band).wave_eff,Ia_av/3.1)
        else:
            tempmagLimit-=_ccm_extinction(sncosmo.get_bandpass(band).wave_eff,CC_av/3.1)
        absolute=absolutes[snClass]
        if isinstance(mu,np.ndarray):
            magLimits=[tempmagLimit+2.5*np.log10(mu[i]) for i in range(len(redshifts))]
        else:
            magLimits=[tempmagLimit+2.5*np.log10(mu) for i in range(len(redshifts))]
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
            if len(mags[mags<=magLimits[i]])==0:
                fractions.append(0)
            else:
                if len(mags[mags<=magLimits[i]])<cadence:
                    fractions.append(float(len(mags[mags<=magLimits[i]])/cadence))
                else:
                    fractions.append(1)
        resultsDict[snClass]=np.array(fractions)

    return(resultsDict)











