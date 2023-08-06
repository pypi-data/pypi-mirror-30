# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *
import pickle
from .metrics import AGTP,RadiativeForcing
import numpy as np
from ..dynamic_ia_methods import DynamicIAMethod
from bw2data import config, Database, databases
import itertools
import os


CONSTANTS_FILEPATH=os.path.join(os.path.dirname(__file__), 'constants.pkl').replace("\\", "\\\\")

def _create_constants():
    """create the climate constants and save to pickle"""
    constants={}

    #create AGTP timeline (add other gasses)
    constants["co2_agtp_ar5_td"]= AGTP("co2", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["co2bio_agtp_ar5_td"]= AGTP("co2_biogenic", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["ch4_agtp_ar5_td"]= AGTP("ch4", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["ch4_fossil_agtp_ar5_td"]= AGTP("ch4_fossil", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["n2o_agtp_ar5_td"]= AGTP("n2o", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["sf6_agtp_ar5_td"]= AGTP("sf6", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["co2_agtp_base_td"]= AGTP("co2", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_base")
    constants["co2bio_agtp_base_td"]= AGTP("co2_biogenic", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_base")
    constants["ch4_agtp_base_td"]= AGTP("ch4", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_base")
    constants["ch4_fossil_agtp_base_td"]= AGTP("ch4_fossil", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_base")
    constants["n2o_agtp_base_td"]= AGTP("n2o", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_base")
    constants["sf6_agtp_base_td"]= AGTP("sf6", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_base")
    constants["co2_agtp_low_td"]= AGTP("co2", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_low")
    constants["co2bio_agtp_low_td"]= AGTP("co2_biogenic", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_low")
    constants["ch4_agtp_low_td"]= AGTP("ch4", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_low")
    constants["ch4_fossil_agtp_low_td"]= AGTP("ch4_fossil", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_low")
    constants["n2o_agtp_low_td"]= AGTP("n2o", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_low")
    constants["sf6_agtp_low_td"]= AGTP("sf6", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_low")
    constants["co2_agtp_high_td"]= AGTP("co2", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_high")
    constants["co2bio_agtp_high_td"]= AGTP("co2_biogenic", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_high")
    constants["ch4_agtp_high_td"]= AGTP("ch4", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_high")
    constants["ch4_fossil_agtp_high_td"]= AGTP("ch4_fossil", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_high")
    constants["n2o_agtp_high_td"]= AGTP("n2o", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_high")
    constants["sf6_agtp_high_td"]= AGTP("sf6", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000, "op_high")
    #create RF timeline (add other gasses)
    constants["co2_rf_td"]= RadiativeForcing("co2", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["co2bio_rf_td"]= RadiativeForcing("co2_biogenic", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["ch4_rf_td"]= RadiativeForcing("ch4", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["ch4_fossil_rf_td"]= RadiativeForcing("ch4_fossil", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["n2o_rf_td"]= RadiativeForcing("n2o", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    constants["sf6_rf_td"]= RadiativeForcing("sf6", np.array((1.,)), np.array((0,),dtype=('timedelta64[Y]')), 'Y', 1000)
    
    #save to pickle
    pickle.dump(constants, open(CONSTANTS_FILEPATH, "wb" ) )
    
    
def _register_static_forest_biosphere():
    db = Database("static_forest") 
    db.write(
    {('static_forest', 'C_biogenic'): {
     # ~#{'categories': ('water','ground-'), 
      'code': 'C_biogenic', 
      'database': 'Biogenic Carbon dioxide from forest regrowth', 
      'name': 'C biogenic from forest regrowth', 
      'type': 'emission',
      'unit': 'kilogram'}})

def create_climate_methods(overwrite_constants=False):
    
    """Create the dynamic LCIA methods for AGTP and Radiative Forcing that are calculated every year over 500 years for each GHG emissions.
    Gasses from custom biosphere database can be added simpy adding their names to `gas_name_in_biosphere`
    
    All the work is based on the library ghgforcing built by Greg Schively. It can be downloaded from https://github.com/gschivley/ghgforcing.
    
    Args:
        * *overwrite_constants* (Boolean, default=False): Recreate clilmate constants even if the `constants.pkl` file already exists.
    
    """
    
    #first we create the constants
    if not os.path.isfile(CONSTANTS_FILEPATH) or overwrite_constants:
        const=_create_constants()
    #we register our biosphere flow for forest
    if 'static_forest' not in databases.list:
        _register_static_forest_biosphere()
    
    bio = Database(config.biosphere)
    
    #from report 'ecoinvent 3.3_LCIA_implementation'
    gas_name_in_biosphere = {
    'co2': [
        "Carbon dioxide, fossil", #fossil fuel emission thus normal CF
        "Carbon dioxide, from soil or biomass stock", # emission from LUC thus normal CF
        "Carbon dioxide, land transformation", #same of above in ei2. bw2 maps to biosphere flow of ei3, left just in case
            #"Carbon dioxide, non-fossil, from calcination" #non characterized in ei 3.3"
            ],
    'ch4_fossil': [
        "Methane", # old fossil ch4 of ei2. bw2 maps to biosphere flow of ei3, left just in case
        "Methane, fossil",
        "Methane, from soil or biomass stock"
            ],
    'ch4': [
        "Methane, non-fossil",
        "Methane, biogenic" # old non_fossil ch4 of ei2. bw2 maps to biosphere flow of ei3, left just in case
            ],
    'n2o': ["Dinitrogen monoxide"],
    'sf6': ["Sulfur hexafluoride"],
    'co2bio':
            ('static_forest',"C_biogenic"), #see DynamicLCA.add_biosphere_flows() to understand why this, should be biogenic (ei22) or non-fossil (ei3) technically but used this trick and check if downstream goes to forest
            
    }   
    
    dyn_met={"agtp_ar5":"AGTP",
             "agtp_base":"GTP OP base",
             "agtp_low":"GTP OP low",
             "agtp_high":"GTP OP high",
             "rf":"RadiativeForcing",
             }
                    
    function="""def {0}_{1}_function(datetime):
                    import pickle
                    import numpy as np
                    from datetime import timedelta
                    import collections
                    constants = pickle.load( open(\"{2}\", "rb" ) )
                    return_tuple = collections.namedtuple('return_tuple', ['dt', 'amount'])
                    return [return_tuple(d,v) for d,v in zip((datetime+constants[\"{0}_{1}_td\"].times.astype(timedelta)),constants[\"{0}_{1}_td\"].values)]"""

    print('Dynamic IA Methods written:')
    for met_func,met_name in dyn_met.items():

        method = DynamicIAMethod(met_name)

        cf_data = {}

        for gas,gas_bio in gas_name_in_biosphere.items():
            if gas=='co2bio':
                #need again to convert datetime back to numpy
                cf_data[gas_bio] =function.format(gas,met_func,CONSTANTS_FILEPATH)
            else:
                for gas_n in gas_bio:
                    for bio_key in [ds.key for ds in bio if ds['name']==gas_n]: 
                        cf_data[bio_key] = function.format(gas,met_func,CONSTANTS_FILEPATH)                            
        method.register(
            from_function="create_climate_methods",
            library="dyn_methods"
        )   
        method.write(cf_data)     

        method.to_worst_case_method((met_name,"worst case"), dynamic=False)
        print(method)

    #GIU:is the return of method necessary?
    # return method

