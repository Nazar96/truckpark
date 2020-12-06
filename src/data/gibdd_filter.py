import pandas as pd
import numpy as np


def normalize_name(s):
    try:
        if s.endswith('.0'):
            return s[:-2]
        if s.isnumeric():
            return s
        
    except AttributeError:
        return np.nan
    return np.nan


class GibddFilter:
    def __init__(self, df):
        self.df = df
        self.filter_methods = [
            'filter_inn',
            'filter_vin',
            'filter_class',
            'filter_mass',
            'filter_brand',
            'filter_vehicle',
            'filter_model',
            'filter_year',
        ]
    
    def filter_data(self, filter_methods=None):
        if filter_methods is None:
            filter_methods = self.filter_methods
            
        for func in self.filter_methods:
            print(func)
            self.df = getattr(self, func)()
            
        return self
    
    def filter_inn(self, inn_name_len=10):
        """
        Filter invalid INN names
        """
        df = self.df.copy()
        
        df['inn'] = df['inn'].astype(str).apply(normalize_name)
        df.loc[df['inn'].str.len()==9, 'inn'] = df.loc[df['inn'].str.len()==9, 'inn'].apply(lambda x: '0'+x)
        valid_inn = (df['inn'].str.len() == inn_name_len) | (df['activity_field'] == 'ФИЗ ЛИЦО')
        df = df[valid_inn]
        
        return df

    def filter_vin(self, vin_name_len=17):
        """
        Filter invalid VIN names
        """
        df = self.df.copy()

        mask_vin = (df['vin'].str.len() == vin_name_len)
        df = df.loc[mask_vin]
        
        return df

    def filter_class(self):
        """
        Leave Heavy Duty Trucks and Medium Duty Trucks only
        """
        df = self.df.copy()

        class_mask = (df['class'].str.startswith('HDT')) | (df['class'].str.startswith('MDT'))
        df = df[class_mask]
        
        return df

    def filter_mass(self, max_mass=50_000, min_mass=4_000):
        """
        Filter unrealistic mass
        """
        df = self.df.copy()

        df['mass_max'] = df['mass_max'].astype(float)
        df['mass_idle'] = df['mass_idle'].astype(float)
        df.loc[df['mass_idle'] > max_mass, 'mass_idle'] = np.nan
        df.loc[df['mass_idle'] < min_mass, 'mass_idle'] = np.nan

        df['mass_max'] = df['mass_max'].apply(normalize_name).astype(float)

        df.loc[df['mass_max'] > max_mass, 'mass_max'] = np.nan
        df.loc[df['mass_max'] < min_mass, 'mass_max'] = np.nan

        return df

    def filter_brand(self):
        """
        Filter brand
        """
        df = self.df.copy()

        df.loc[df['brand'] == 'КАМАЗ НМР', 'brand'] = 'КАМАЗ'
        df.loc[(df['brand'] == 'IVECO-AMT'), 'brand'] = 'IVECO'
        df.loc[(df['brand'] == 'IVECO-АМТ'), 'brand'] = 'IVECO'

        df = df[df['brand'] != 'LADA']
        df = df[df['brand'] != 'KIA']

        brand_per_vin = df.groupby('vin')['brand'].nunique()
        valid_vin = brand_per_vin[brand_per_vin==1].index
        df = df[df['vin'].isin(valid_vin)]

        return df

    def filter_vehicle(self):
        """
        Filter car class
        Leave A B classes
        """
        df = self.df.copy()

        mask = df['vehicle_type'].isin(['А', 'В'])
        df = df.loc[~mask]

        tmp = df.groupby('vin')['vehicle_type'].nunique()
        valid_vin = tmp[tmp==1].index
        df = df[df['vin'].isin(valid_vin)]

        return df

    def filter_model(self, max_wheels=10):
        """
        Filter chassis configuration
        """
        df = self.df.copy()

        df['chassis_config'] = df['chassis_config'].str.lower()
        df['chassis_config'] = df['chassis_config'].str.replace('х', 'x')

        valid_chassis = df['chassis_config'].value_counts().head(15).index
        df = df[df['chassis_config'].isin(valid_chassis)]
        df = df[df['chassis_config'].str.split('x').str[0].astype(float) < max_wheels]

        return df

    def filter_year(self, min_year=1980):
        """
        Filter year
        """
        df = self.df.copy()

        df['year'] = df['year'].astype(float)
        df = df[df['year'] > min_year]
        tmp = df.groupby('vin')['year'].nunique()
        valid_vin = tmp[tmp==1].index
        df = df[df['vin'].isin(valid_vin)]

        return df
