# -*- coding: utf-8 -*-
'''
HITRAN database parser 
'''

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import pandas as pd
import numpy as np
from collections import OrderedDict
import os
from os.path import exists, splitext
from six.moves import range
from six.moves import zip

# %% Hitran groups and classes
# As defined in Rothman et al, "The HITRAN 2004 molecular spectroscopic database"
# Tables 3 and 4

# Groups (define local quanta)

HITRAN_GROUP1 = ['H2O', 'O3', 'SO2', 'NO2', 'HNO3', 'H2CO', 'HOCl', 'H2O2', 'COF2',
               'H2S', 'HO2', 'HCOOH', 'ClONO2', 'HOBr', 'C2H4'] # asymmetric rotors

HITRAN_GROUP2 = ['CO2', 'N2O', 'CO', 'HF', 'HCl', 'HBr', 'HI', 'OCS', 'N2', 'HCN',
                 'C2H2', 'NO+']   # diatomic and linear molecules

HITRAN_GROUP3 = ['SF6', 'CH4']   # Spherical rotors

HITRAN_GROUP4 = ['CH3D', 'CH3Cl', 'C2H6', 'NH3', 'PH3', 'CH3OH']  # symmetric rotors

HITRAN_GROUP5 = ['O2']  # Triplet-Sigma ground electronic states

HITRAN_GROUP6 = ['NO', 'OH', 'ClO']  # Doublet-Pi ground electronic states 

# Classes (define global quanta)

HITRAN_CLASS1 = ['CO', 'HF', 'HCl', 'HBr', 'HI', 'N2', 'NO+']

HITRAN_CLASS2 = ['O2']  # Diatomic molecules with different electronic levels

HITRAN_CLASS3 = ['NO', 'OH', 'ClO']  # Diatomic molecules with doublet-Pi electronic state
    
HITRAN_CLASS4 = ['N2O', 'OCS', 'HCN']  # Linear triatomic

HITRAN_CLASS5 = ['CO2']  # Linear triatomic with large Fermi resonance

HITRAN_CLASS6 = ['H2O', 'O3', 'SO2', 'NO2', 'HOCl', 'H2S', 'HO2', 'HOBr'] # Non-linear triatomic

HITRAN_CLASS7 = ['C2H2']  # Linear tetratomic

HITRAN_CLASS8 = ['NH3', 'PH3']  # Pyramidal tetratomic

HITRAN_CLASS9 = ['H2CO', 'H2O2', 'COF2']  # Non-linear tetratomic

HITRAN_CLASS10 = ['CH4', 'CH3D', 'CH3Cl', 'C2H6', 'HNO3', 'SF6', 'HCOOH', 
                  'ClONO2', 'C2H4', 'CH3OH']  # Pentatomic or greater polyatomic

# %% Parsing functions

# General case
columns_2004 = OrderedDict([ (
               # name    # format # type  # description                                 # unit 
               'id',     ('a2',   int,   'Molecular number'                               ,''                      )),(
               'iso',    ('a1',   int,   'isotope number'                                 ,''                      )),(
               'wav',    ('a12',  float, 'vacuum wavenumber'                              ,'cm-1'                  )),(
               'int',    ('a10',  float, 'intensity at 296K'                              ,'cm-1/(molecule/cm-2)', )),(
               'A',      ('a10',  float, 'Einstein A coefficient'                         ,'s-1'                   )),(
               'airbrd', ('a5',   float, 'air-broadened half-width at 296K'               ,'cm-1.atm-1'            )),(
               'selbrd', ('a5',   float, 'self-broadened half-width at 296K'              ,'cm-1.atm-1'            )),(
               'El',     ('a10',  float, 'lower-state energy'                             ,'cm-1'                  )),(
               'Tdpair', ('a4',   float, 'temperature-dependance exponent for Gamma air'  ,''                      )),(
               'Pshft',  ('a8',   float, 'air pressure-induced line shift at 296K'        ,'cm-1.atm-1'            )),( 
               'globu',  ('a15',  str,   'electronic and vibrational global upper quanta' ,''                      )),(
               'globl',  ('a15',  str,   'electronic and vibrational global lower quanta' ,''                      )),(
               'locu',   ('a15',  str,   'electronic and vibrational local upper quanta'  ,''                      )),(
               'locl',   ('a15',  str,   'electronic and vibrational local lower quanta'  ,''                      )),(
               'ierr',   ('a6',   str,   'ordered list of indices corresponding to uncertainty estimates of transition parameters'    ,''   )),(
               'iref',   ('a12',  str,   'ordered list of reference identifiers for transition parameters'                    ,''           )),(
               'lmix',   ('a1',   str,   'flag indicating the presence of additional data and code relating to line-mixing'   ,''           )),(
               'gp',     ('a7',   float, 'upper state degeneracy'                         ,''                      )),(
               'gpp',    ('a7',   float, 'lower state degeneracy'                         ,''                      ))
               ])


# Particular cases for different groups of local quanta ('locu', 'locl' are split)
# cf "The HITRAN 2004 molecular spectroscopic database", Rothman et al. 2004
# -----------

# Group 2: diatomic and linear molecules
columns_grp2 = OrderedDict([ (
               # name    # format # type  # description                                 # unit 
               'id',     ('a2',   int,   'Molecular number'                               ,''                      )),(
               'iso',    ('a1',   int,   'isotope number'                                 ,''                      )),(
               'wav',    ('a12',  float, 'vacuum wavenumber'                              ,'cm-1'                  )),(
               'int',    ('a10',  float, 'intensity at 296K'                              ,'cm-1/(molecule/cm-2)', )),(
               'A',      ('a10',  float, 'Einstein A coefficient'                         ,'s-1'                   )),(
               'airbrd', ('a5',   float, 'air-broadened half-width at 296K'               ,'cm-1.atm-1'            )),(
               'selbrd', ('a5',   float, 'self-broadened half-width at 296K'              ,'cm-1.atm-1'            )),(
               'El',     ('a10',  float, 'lower-state energy'                             ,'cm-1'                  )),(
               'Tdpair', ('a4',   float, 'temperature-dependance exponent for Gamma air'  ,''                      )),(
               'Pshft',  ('a8',   float, 'air pressure-induced line shift at 296K'        ,'cm-1.atm-1'            )),( 
               'globu',  ('a15',  str,   'electronic and vibrational global upper quanta' ,''                      )),(
               'globl',  ('a15',  str,   'electronic and vibrational global lower quanta' ,''                      )),(
               #'locu',   ('a15',  str,   'electronic and vibrational local upper quanta'  ,''                      )),(
                # 10X included in Fu
               'Fu',     ('a15',  str,  'upper state total angular momentum including nuclear spin'  ,''         )),(
               #'locl',   ('a15',  str,   'electronic and vibrational local lower quanta'  ,''                      )),(
               'branch', ('a6',   str,     'O, P, Q, R, S branch symbol'                  ,''                      )),(
               'jl',     ('a3',   int,    'lower state rotational quantum number'         ,''                      )),(
               'sym',    ('a1',   str,     'symmetry'                                     ,''                      )),(
               'Fl',     ('a5',   str,   'lower state total angular momentum including nuclear spin', ''         )),(
               #
               'ierr',   ('a6',   str,   'ordered list of indices corresponding to uncertainty estimates of transition parameters'   ,''    )),(
               'iref',   ('a12',  str,   'ordered list of reference identifiers for transition parameters'                    ,''           )),(
               'lmix',   ('a1',   str,   'flag indicating the presence of additional data and code relating to line-mixing'   ,''           )),(
               'gp',     ('a7',   float, 'upper state degeneracy'                         ,''                      )),(
               'gpp',    ('a7',   float, 'lower state degeneracy'                         ,''                      ))
               ])

# quick fix # TODO: proper implementation of HITRAN classes, and groups
# Update: classes are now implemented properly, groups remain to be done 

# %% Hitran global quanta classes

def parse_HITRAN_class1(df):
    ''' Diatomic molecules: CO, HF, HCl, HBr, HI, N2, NO+
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>      v1
    >>>  13x I2
    
    '''
    dgu = df['globu'].str.extract(
            '[ ]{13}(?P<v1u>[\d ]{2})',
            expand=True)
    dgl = df['globl'].str.extract(
            '[ ]{13}(?P<v1l>[\d ]{2})',
            expand=True)
    dgu = dgu.apply(pd.to_numeric)
    dgl = dgl.apply(pd.to_numeric)
    return pd.concat([df, dgu, dgl], axis=1)

def parse_HITRAN_class2(df):
    ''' Diatomic molecules with different electronic levels: O2
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>      X  v1
    >>>  12x A1 I2
    
    '''
    raise NotImplementedError

def parse_HITRAN_class3(df):
    ''' Diatomic molecules with doublet-Pi electronic state: NO, OH, ClO
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -------
    
    HITRAN syntax:
    
    >>>      X i     v1
    >>>  7x A1 A3 2x I2
    '''
    raise NotImplementedError

def parse_HITRAN_class4(df):
    ''' Linear triatomic: N2O, OCS, HCN
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>     v1 v2 l2 v3
    >>>  7x I2 I2 I2 I2
    
    Note: I2 in regexp: [\d ]{2} 
    '''
    dgu = df['globu'].str.extract(
            '[ ]{7}(?P<v1u>[\d ]{2})(?P<v2u>[\d ]{2})(?P<l2u>[\d ]{2})(?P<v3u>[\d ]{2})',
            expand=True)
    dgl = df['globl'].str.extract(
            '[ ]{7}(?P<v1l>[\d ]{2})(?P<v2l>[\d ]{2})(?P<l2l>[\d ]{2})(?P<v3l>[\d ]{2})',
            expand=True)
    dgu = dgu.apply(pd.to_numeric)
    dgl = dgl.apply(pd.to_numeric)
    return pd.concat([df, dgu, dgl], axis=1)

def parse_HITRAN_class5(df):
    ''' Linear triatomic with large Fermi resonance: CO2
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>     v1 v2 l2 v3 r
    >>>  6x I2 I2 I2 I2 I1
    
    Note: I2 in regexp: [\d ]{2} 
    '''
    dgu = df['globu'].str.extract(
            '[ ]{6}(?P<v1u>[\d ]{2})(?P<v2u>[\d ]{2})(?P<l2u>[\d ]{2})(?P<v3u>[\d ]{2})(?P<ru>\d)',
            expand=True)
    dgl = df['globl'].str.extract(
            '[ ]{6}(?P<v1l>[\d ]{2})(?P<v2l>[\d ]{2})(?P<l2l>[\d ]{2})(?P<v3l>[\d ]{2})(?P<rl>\d)',
            expand=True)
    dgu = dgu.apply(pd.to_numeric)
    dgl = dgl.apply(pd.to_numeric)
    return pd.concat([df, dgu, dgl], axis=1)

def parse_HITRAN_class6(df):
    ''' Non-linear triatomic: H2O, O3, SO2, NO2, HOCl, H2S, HO2, HOBr
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>     v1 v2 v3
    >>>  9x I2 I2 I2
    
    Note: I2 in regexp: [\d ]{2} 
    '''
    dgu = df['globu'].str.extract(
            '[ ]{9}(?P<v1u>[\d ]{2})(?P<v2u>[\d ]{2})(?P<v3u>[\d ]{2})',
            expand=True)
    dgl = df['globl'].str.extract(
            '[ ]{9}(?P<v1l>[\d ]{2})(?P<v2l>[\d ]{2})(?P<v3l>[\d ]{2})',
            expand=True)
    dgu = dgu.apply(pd.to_numeric)
    dgl = dgl.apply(pd.to_numeric)
    return pd.concat([df, dgu, dgl], axis=1)

def parse_HITRAN_class7(df):
    ''' Linear tetratomic: C2H2
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>
    '''
    raise NotImplementedError

def parse_HITRAN_class8(df):
    ''' Pyramidal tetratomic: NH3, PH3
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>
    '''
    raise NotImplementedError

def parse_HITRAN_class9(df):
    ''' Non-linear tetratomic: H2CO, H2O2, COF2
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>
    '''
    raise NotImplementedError

def parse_HITRAN_class10(df):
    ''' Pentatomic or greater polyatomic
    
    
    Parameters
    ----------
    
    df: pandas Dataframe
        lines read from a HITRAN-like database
        
    
    Notes
    -----
    
    HITRAN syntax:
    
    >>>
    '''
    raise NotImplementedError

# %% Reading function


def _format_dtype(dtype):
    ''' Format dtype from specific columns. Crash with hopefully helping error message '''
    
    try:
        dt = np.dtype([(str(k), c) for k, c in dtype])
        # Note: dtype names cannot be `unicode` in Python2. Hence the str()
    except TypeError:
        # Cant read database. Try to be more explicit for user
        print('Data type')
        print('-'*30)
        for (k, c) in dtype:
            print(str(k), '\t', c)
        print('-'*30)
        raise
    return dt

def _cast_to_dtype(data, dtype):
    ''' Cast array to certain type, crash with hopefull helping error message.
    Return casted data
    
    
    Parameters    
    ----------
    
    data: array to cast
    
    dtype: (ordered) list of (param, type)
    
    '''
    
    dt = _format_dtype(dtype)
    
    try:
        data = np.array(data, dtype=dt)
    except ValueError:
        try:
            # Cant read database. Try to be more explicit for user
            print('Cant cast data to specific dtype. Trying column by column:')
            print('-'*30)
            for i in range(len(data[0])):
                print(dtype[i], '\t', np.array(data[0][i], dtype=dt[i]))
            print('-'*30)
        except ValueError:
            print('>>> Next param:', dtype[i], '. Value:', data[0][i], '\n')
            raise ValueError('Cant cast data to specific dtype. Tried column by column. See results above')

    return data
        
def hit2df(fname, count=-1, cache=False, verbose=True):
    ''' Convert a HITRAN/HITEMP file to a Pandas dataframe 
    
    
    Parameters    
    ----------
    
    fname: str
        HITRAN-HITEMP file name 
        
    count: int
        number of items to read (-1 means all file)
        
    cache: boolean
        if True, a pandas-readable HDF5 file is generated on first access, 
        and later used. This saves on the datatype cast and conversion and
        improves performances a lot (but changes in the database are not 
        taken into account). If False, no database is used. If 'regen', temp
        file are reconstructed. Default False. 
    
    
    References
    ----------
    
    HITRAN-HITEMP doc 
    
    
    Notes
    -----
    
    Performances: see CDSD-HITEMP parser
    
    '''
    
    columns = columns_2004

    if cache: # lookup if cached file exist. 
#        fcache = fname+'.cached'
        fcache = splitext(fname)[0]+'.h5'
        if exists(fcache):
            if cache == 'regen':
                os.remove(fcache)
                if verbose: print('Deleted h5 cache file : {0}'.format(fcache))
            else:
                if verbose: print('Using h5 file: {0}'.format(fcache))
    #            return pd.read_csv(fcache)
                return pd.read_hdf(fcache, 'df')
        
    # Detect the molecule by reading the start of the file
    with open(fname) as f:
        mol = get_molecule(int(f.read(2)))
        
    # parse group specific local quanta information
    if mol in HITRAN_GROUP1:
        if verbose: print('Local quanta specific format not implemented yet for group 1') #TODO someday
    elif mol in HITRAN_GROUP2:
        columns = columns_grp2  
    elif mol in HITRAN_GROUP3:
        if verbose: print('Local quanta specific format not implemented yet for group 3') #TODO someday
    elif mol in HITRAN_GROUP4:
        if verbose: print('Local quanta specific format not implemented yet for group 4') #TODO someday
    elif mol in HITRAN_GROUP5:
        if verbose: print('Local quanta specific format not implemented yet for group 5') #TODO someday
    elif mol in HITRAN_GROUP6:
        if verbose: print('Local quanta specific format not implemented yet for group 6') #TODO someday
    else:
        if verbose: print('Unknown molecule group for:', mol)


    # %% Start reading the full file
    
    # get format of line return
    if sys.platform in ['linux', 'darwin']:
        linereturnformat = 'a1'
    elif sys.platform in ['win32','linux2']:
        linereturnformat = 'a2'
    else:
        raise ValueError('Line return format not defined for this OS: please update neq')

    # ... Create a dtype with the binary data format and the desired column names
    dtype = [(k, c[0]) for (k, c) in columns.items()]+[('_linereturn',linereturnformat)]   
    # ... _linereturn is to capture the line return symbol. We delete it afterwards
    dt = _format_dtype(dtype)
    data = np.fromfile(fname, dtype=dt, count=count)
    
    # ... Cast to new type
    # This requires to recast all the data already read, but is still the fastest
    # method I found to read a file directly (for performance benchmark see 
    # CDSD-HITEMP parser)
    newtype = [c[0] if (c[1]==str) else c[1] for c in columns.values()]
    dtype = list(zip(list(columns.keys()), newtype))+[('_linereturn',linereturnformat)]
    data = _cast_to_dtype(data, dtype)

    # %% Create dataframe    
    df = pd.DataFrame(data.tolist(), columns=list(columns.keys())+['_linereturn'])

    # assert one molecule per database only. Else the groupbase data reading 
    # above doesnt make sense
    nmol = len(set(df['id']))
    if nmol == 0:
        raise ValueError('Databank looks empty')        
    elif nmol!=1:
        raise ValueError('Multiple molecules in database ({0}). Current '.format(nmol)+\
                         'spectral code only computes 1 species at the time. Use MergeSlabs')
    
    for k, c in columns.items():
        if c[1] == str:
            df[k] = df[k].str.decode("utf-8")
            
    # Add global quanta attributes
    if mol in HITRAN_CLASS1:
        df = parse_HITRAN_class1(df)
    elif mol in HITRAN_CLASS2:
        df = parse_HITRAN_class2(df)
    elif mol in HITRAN_CLASS3:
        df = parse_HITRAN_class3(df)
    elif mol in HITRAN_CLASS4:
        df = parse_HITRAN_class4(df)
    elif mol in HITRAN_CLASS5:
        df = parse_HITRAN_class5(df)
    elif mol in HITRAN_CLASS6:
        df = parse_HITRAN_class6(df)
    elif mol in HITRAN_CLASS7:
        df = parse_HITRAN_class7(df)
    elif mol in HITRAN_CLASS8:
        df = parse_HITRAN_class8(df)
    elif mol in HITRAN_CLASS9:
        df = parse_HITRAN_class9(df)
    elif mol in HITRAN_CLASS10:
        df = parse_HITRAN_class10(df)
    else:
        raise ValueError('Unknown class for molecule {0}. Cant parse global quanta'.format(
                mol))
            
    # Strip whitespaces around PQR columns (due to 2 columns jumped)
    if 'branch' in df:
        df['branch'] = df.branch.str.strip()
    
    # Delete dummy column than handled the line return character
    del df['_linereturn']
    
    if cache: # cached file mode but cached file doesn't exist yet (else we had returned)
        if verbose: print('Generating cached file: {0}'.format(fcache))
        try:
#            df.to_csv(fcache)
            df.to_hdf(fcache, 'df', format='fixed')
        except:
            if verbose:
                print(sys.exc_info())
                print('An error occured in cache file generation. Lookup access rights')
            pass
        
    return df 

def get_molecule_identifier(molecule_name):
    '''
    For a given input molecular formula, return the corresponding HITRAN molecule identifier number.
    
    
    Parameters
    ----------
    molecular_formula : str
        The string describing the molecule.
        
        
    Returns
    -------
    M : int
        The HITRAN molecular identified number.
        
        
    References
    ----------
    
    Function from https://github.com/nzhagen/hitran/blob/master/hitran.py
    '''

    trans = { '1':'H2O',    '2':'CO2',   '3':'O3',      '4':'N2O',   
              '5':'CO',    '6':'CH4',   '7':'O2',     '8':'NO',
              '9':'SO2',   '10':'NO2',  '11':'NH3',    '12':'HNO3', 
              '13':'OH',   '14':'HF',   '15':'HCl',   '16':'HBr',
             '17':'HI',    '18':'ClO',  '19':'OCS',    '20':'H2CO', 
             '21':'HOCl', '22':'N2',   '23':'HCN',   '24':'CH3Cl',
             '25':'H2O2',  '26':'C2H2', '27':'C2H6',   '28':'PH3',  
             '29':'COF2', '30':'SF6',  '31':'H2S',   '32':'HCOOH',
             '33':'HO2',   '34':'O',    '35':'ClONO2', '36':'NO+',  
             '37':'HOBr', '38':'C2H4', '39':'CH3OH', '40':'CH3Br',
             '41':'CH3CN', '42':'CF4',  '43':'C4H2',   '44':'HC3N', 
             '45':'H2',   '46':'CS',   '47':'SO3'}
    ## Invert the dictionary.
    trans = {v:k for k,v in trans.items()}

    return(int(trans[molecule_name]))

def get_molecule(molecule_id):
    '''
    For a given input molecular identifier, return the corresponding HITRAN 
    molecule name.
    
    
    Parameters    
    ----------
    
    molecular_id : str
        Hitran identifier of the molecule.
    '''
    
    # assert str
    id = '{0}'.format(molecule_id)

    trans = { '1':'H2O',    '2':'CO2',   '3':'O3',      '4':'N2O',   
              '5':'CO',    '6':'CH4',   '7':'O2',     '8':'NO',
              '9':'SO2',   '10':'NO2',  '11':'NH3',    '12':'HNO3', 
              '13':'OH',   '14':'HF',   '15':'HCl',   '16':'HBr',
             '17':'HI',    '18':'ClO',  '19':'OCS',    '20':'H2CO', 
             '21':'HOCl', '22':'N2',   '23':'HCN',   '24':'CH3Cl',
             '25':'H2O2',  '26':'C2H2', '27':'C2H6',   '28':'PH3',  
             '29':'COF2', '30':'SF6',  '31':'H2S',   '32':'HCOOH',
             '33':'HO2',   '34':'O',    '35':'ClONO2', '36':'NO+',  
             '37':'HOBr', '38':'C2H4', '39':'CH3OH', '40':'CH3Br',
             '41':'CH3CN', '42':'CF4',  '43':'C4H2',   '44':'HC3N', 
             '45':'H2',   '46':'CS',   '47':'SO3'}

    return(trans[id])

## ======================================================
# %% Test

def _test(verbose=True, warnings=True, **kwargs):
    ''' Analyse some default files to make sure everything still works'''
    from neq.test.utils import getTestFile
    from time import time
    
    b = True
    
    t0 = time()
    df = hit2df(getTestFile('hitran_CO_fragment.par'))
    print('File loaded in {0:.0f}s'.format(time()-t0))
    if verbose: print(df.head())
    b *= (list(df.ix[0, ['v1u', 'v1l']]) == [4, 4])

    t0 = time()
    df = hit2df(getTestFile('hitran_CO2_fragment.par'))
    print('File loaded in {0:.0f}s'.format(time()-t0))
    if verbose: print(df.head())
    b *= (list(df.ix[0, ['v1u', 'v2u', 'l2u', 'v3u', 'v1l', 'v2l', 'l2l', 'v3l']]) ==
              [4, 0, 0, 0, 0, 0, 0, 1])
    
    return (bool(b))


if __name__ == '__main__':
    print('Testing HITRAN parsing: ', _test())
        