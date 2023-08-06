import numpy as np
import pandas as pd
import pickle
import random
import string
from sklearn.preprocessing import scale

class simulate:
    """
    Generates a properly formulated simulated circadian dataset for testing.


    This class takes user specifications on dataset size along with the number and frequency of batch effects and levels of background noise and outputs a simulated dataset along with a key showing which rows represent truly circadian data.


    Parameters
    ----------
    tpoints : int
        
    nrows : int

    nreps : int

    tpoint_space : int
        
    pcirc : float

    phase_prop : float

    phase_noise : float

    amp_noise : float

    n_batch_effects : int

    pbatch : float

    Probability of each batch effects appearance in a given peptide.

    effect_size : float

    Average size of batch effect

    p_miss : float

    probability of missing data




        


    Attributes
    ----------

    simdf : dataframe

    Simulated data without noise.

    simndf : dataframe

    Simulated data with noise.

    """

    def __init__(self,tpoints=24,nrows=1000, nreps=3, tpoint_space=2, pcirc=.5, phase_prop=.5, phase_noise=.25, amp_noise=1, n_batch_effects=5, pbatch=.4, effect_size=2, p_miss=.05):
        """
        Simulates circadian data and saves as a properly formatted example .csv file.

        Takes a file from one of two data types protein ('p') which has two index columns or rna ('r') which has only one.  Opens a pickled file matching pooled controls to corresponding samples if data_type = 'p' and opens a picked file matching samples to blocks if designtype = 'b'.

        """

        np.random.seed(4574)
        self.tpoints = int(tpoints)
        self.nreps = int(nreps)
        self.nrows = int(nrows)
        self.tpoint_space = int(tpoint_space)
        self.pcirc = float(pcirc)
        self.phase_prop = float(phase_prop)
        self.phase_noise = float(phase_noise)
        self.amp_noise = float(amp_noise)
        self.n_batch_effects = int(n_batch_effects)
        self.pbatch = float(pbatch)
        self.effect_size = float(effect_size)
        self.p_miss = float(p_miss)

        #procedurally generate column names
        self.cols = []
        for i in range(self.tpoints):
            for j in range(self.nreps):
                self.cols.append('CT'+str(self.tpoint_space*i)+'_'+str(j+1))

        #randomly determine which rows are circadian
        circ = np.random.binomial(1, self.pcirc, self.nrows)
        #generate a base waveform
        base = np.arange(0,(4*np.pi),(4*np.pi/self.tpoints))
        #simulate data
        self.sim = []
        phases = []
        for i in circ:
            if i == 1:
                temp=[]
                p = np.random.binomial(1, self.phase_prop)
                phases.append(p)
                for j in range(self.nreps):
                    temp.append(np.sin(base+np.random.normal(0,self.phase_noise,1)+np.pi*p)+np.random.normal(0,self.amp_noise,self.tpoints))
                self.sim.append([item for sublist in zip(*temp) for item in sublist])
            else:
                phases.append('nan')
                self.sim.append(np.random.normal(0,self.amp_noise,(self.tpoints*self.nreps)))
        #add in batch effects
        batch_effects = []
        for i in range(self.n_batch_effects):
            batch_effects.append(np.random.normal(0.,self.effect_size,(self.tpoints*self.nreps)))
        self.simnoise = []
        for i in self.sim:
            temp = i
            bts = np.random.binomial(1, self.pbatch, self.n_batch_effects)
            for j in range(self.n_batch_effects):
                temp += bts[j]*batch_effects[j]
            self.simnoise.append(temp)
        m = np.random.binomial(1, self.p_miss, self.tpoints*self.nreps*self.nrows)
        self.sim_miss = np.ma.masked_array(np.asarray(self.simnoise), mask=m).filled(np.nan)


    def generate_pool_map(self, out_name='pool_map'):
        """

        out_name : str

        output file stem

        """
        self.out_name = str(out_name)
        pool_map = {}
        for i in self.cols:
            pool_map[i] = 1
        pickle.dump(pool_map, open(out_name+'.p', "wb") )


    def write_output(self, out_name='simulated_data'):
        """

        out_name : str

        output file stem

        """

        self.out_name = str(out_name)
        
        self.simndf = pd.DataFrame(self.sim_miss,columns=self.cols).fillna('NULL')
        peps = [''.join(random.choices(string.ascii_uppercase, k=12)) for i in range(len(self.simndf))]
        prots = [''.join(random.choices(string.ascii_uppercase, k=12)) for i in range(len(self.simndf))]
        self.simndf.insert(0, 'Protein', prots)
        self.simndf.insert(0, 'Peptide', peps)
        self.simndf.set_index('Peptide',inplace=True)
        self.simndf.insert((len(self.cols)+1), 'pool_01', ['1']*len(self.simndf))
        self.simndf.to_csv(out_name+'_with_noise.txt',sep='\t')

        self.simdf = pd.DataFrame(np.asarray(self.sim),columns=self.cols)
        self.simdf.insert(0, 'Protein', prots)
        self.simdf.insert(0, 'Peptide', peps)
        self.simdf.set_index('Peptide',inplace=True)
        self.simdf.to_csv(out_name+'_baseline.txt',sep='\t')