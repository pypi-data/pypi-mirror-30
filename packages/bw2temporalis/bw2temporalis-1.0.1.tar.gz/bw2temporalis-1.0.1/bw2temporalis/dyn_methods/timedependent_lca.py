# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *
import os
import numpy as np
from ..dynamic_lca import DynamicLCA
import pickle

# ~CONSTANTS_PATH = pickle.load( open(os.path.join(os.path.dirname(__file__), 'constants.pkl'), "rb" ) )

CONSTANTS_PATH = os.path.join(os.path.dirname(__file__), 'constants.pkl')


def time_dependent_LCA(demand,dynIAM='GWP',t0=None,TH=100,DynamicLCA_kwargs={},characterize_dynamic_kwargs={}):
    """calculate dynamic GWP or GTP for the functional unit and the time horizon indicated following the approach of Levausseur (2010, doi: 10.1021/es9030003).
    It also consider climate effect of forest regrowth of biogenic CO2 (Cherubini 2011  doi: 10.1111/j.1757-1707.2011.01102.x)
    assuming a rotation lenght of 100 yrs.
    
    Note that TH is calculated on the basis of t0 i.e. also if first emissions occurs before t0 everyting is characterzied till t0+TH. This imply
    that, for instance, co2 emissions occuring before t0 but due to `demand` has an impact that his higher than   

    
Args:
    * *demand* (dict):  The functional unit. Same format as in LCA.
    * *t0* (datetime,default = now): year 0 of the time horizon considered.
    * *TH* (int,default =100): lenght of the time horizon in years. This TH is calculate on the basis of t0 i.e. also if first emissions occurs before t0 everyting is characterzied till t0=Th
    * *dynIAM* (string, default='GWP'): Dynamic IA Method, can be 'GWP' or 'GTP'.
    * *DynamicLCA_kwargs* (dict, default=None): optional argument to be passed for DynamicLCA.
    * *characterize_dynamic_kwargs* (dict, default=None): optional arguments to be passed for characterize_dynamic.

    """
    CONSTANTS=pickle.load( open( CONSTANTS_PATH , "rb" ) )
    
    dyn_m={"GWP":"RadiativeForcing",
           "GTP":"AGTP", #default is ar5
           "GTP base":"AGTP OP base",
           "GTP low":"AGTP OP low",
           "GTP high":"AGTP OP high",
           }
    assert dynIAM in dyn_m, "DynamicIAMethod not present, make sure name is correct and `create_climate_methods` was run"

    #set default start and calculate year of TH end
    th_zero=np.datetime64('now') if t0 is None else np.datetime64(t0)
    th_end=th_zero.astype('datetime64[Y]').astype(str).astype(int) + TH #convert to string first otherwhise gives years relative to POSIX time

    #calculate lca
    dlca = DynamicLCA(demand, (dyn_m[dynIAM] , "worst case"),
                      th_zero,
                      **DynamicLCA_kwargs
                     )
    dyn_lca= dlca.calculate().characterize_dynamic(dyn_m[dynIAM],cumulative=False, **characterize_dynamic_kwargs)
    #dyn_lca=([int(x) for x in dyn_lca[0]],dyn_lca[1]) #convert years to int, but better not to be consistent with resolution less than years

    #pick denominator based on metric chosen
    if dynIAM=='GWP':
        co2_imp=CONSTANTS['co2_rf_td']
    elif dynIAM=='GTP':
        co2_imp=CONSTANTS['co2_agtp_ar5_td']
    elif dynIAM=='GTP base':
        co2_imp=CONSTANTS['co2_agtp_base_td']
    elif dynIAM=='GTP low':
        co2_imp=CONSTANTS['co2_agtp_low_td']
    elif dynIAM=='GTP high':
        co2_imp=CONSTANTS['co2_agtp_high_td']
        
    #calculate lenght of th from first emission occuring
    length=len([int(yr) for yr in dyn_lca[0] if int(yr) <= th_end])

    #calculate agwp for demand and co2 and then gwp
    res=np.trapz(x=dyn_lca[0][:length] , y=dyn_lca[1][:length]) / np.trapz(
                 x=(co2_imp.times.astype('timedelta64[Y]').astype('int') + dyn_lca[0][0])[:length],
                 y=co2_imp.values[:length])
    
    return res
