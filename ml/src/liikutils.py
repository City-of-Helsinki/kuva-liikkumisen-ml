# -*- coding: utf-8 -*-
"""
Utility functions to load and extract data

Created on Mon Feb  5 09:01:54 2024


@author: SeppoNyrkkö
"""

import pandas as pd


def load_data(vuosi=-1, ryhma=''):
    '''
    Lataa pohjadatat liikutils-luokalle.
    Lataa arvot näihin jäseniin:
        - perus_df
        - toiminta_df
        - ktk_df
        - m20m_df
        - nykytila_df 

    Parameters
    ----------
    vuosi : TYPE, optional
        Mitkä vuodet luetaan. Oletuksena luetaan kaikki (-1)
    ryhma : TYPE, optional
        Luokka-aste tai sukupuoli. Esim '5p' tai '5'

    Returns
    -------
    None.

    '''
    global perus_df
    global toiminta_df
#    global ktk_df
#    global m20m_df
    global nykytila_df 

    perus_df = pd.read_excel(
        "../input/Koulujen_perustiedot_suojattu_200922.xlsx", engine='openpyxl')
    
    toiminta_df = pd.read_excel(
        "../input/Koulujen_toimintasuunnitelmat_suojattu_2022-2023.xlsx", engine="openpyxl")
    
    nykytila_df = pd.read_excel("../input/Helsinki_nykytilan_arviointi_suojattu_2018-2023.xlsx",engine="openpyxl")
    
#    ktk_df = dict()
#    ktk_df['2023']= pd.read_csv(
#        "../data/ktk_2023_g.tsv",sep="\t")
    
#    ktk_df['2023_5t']= pd.read_csv(
#        "../data/ktk_2023_5t_g.tsv",sep="\t")
    
#    ktk_df['2023_5p']= pd.read_csv(
#        "../data/ktk_2023_5p_g.tsv",sep="\t")
    
#    m20m_df = pd.read_csv("../data/move-osuudet_2022.tsv", sep="\t")
    
#def load_liitu(vuosi=-1,ryhma=''):
#    global liitu_df
#    liitu_df = pd.read_csv("../liitu_60min.csv", sep="\t")
    
