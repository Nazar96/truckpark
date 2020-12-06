# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from glob import glob
from pprint import pprint
import pandas as pd
import numpy as np
from . import DATE_COLUMNS, dtypes, RUS2ENG_COL


usecols = list(RUS2ENG_COL.keys())


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ 
    Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')
    
    files_gibdd = glob(input_filepath+'*.csv')
    pprint(files_gibdd)
    
    
    df_list = [pd.read_csv(file, delimiter=';', usecols=usecols, dtype=dtypes) for file in files_gibdd[1:]]
    df_gibdd = pd.concat(df_list)
    del df_list

    df_gibdd = df_gibdd.rename(columns=RUS2ENG_COL)
    
    for col in DATE_COLUMNS:
        df_gibdd[col] = pd.to_datetime(df_gibdd[col], errors='coerce', format='%Y-%m-%d') 

    df_gibdd.to_parquet(output_filepath)

    
if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables

    main()
