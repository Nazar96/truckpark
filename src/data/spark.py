import os
import pandas as pd
import click

@click.command()
@click.argument('spark_path', default='/home/jovyan/remote_shared_data/dsdiag222/gibdd_dataset_raw/spark_inn/', type=click.Path(exists=True))
@click.argument('holdings_path', default='/home/jovyan/remote_shared_data/dsdiag222/gibdd_dataset_raw/holdings.csv', type=click.Path())
@click.argument('save_path', default='/home/jovyan/shared_data/truck_park/data/processed/inn_info.parquet', type=click.Path())
def main(spark_path, holdings_path, save_path):
    
    SPARK_RENAME = {
            'Код налогоплательщика': 'inn',
            'Размер компании': 'size',
            'Краткое наименование': 'name',
            'Вид деятельности/отрасль': 'activity',
            'Статус': 'status',
            'Код основного вида деятельности': 'activity_code',
            'Сводный индикатор': 'risk',
        }
    SPARK_COLUMNS = ['inn', 'size', 'name', 'activity', 'status', 'activity_code', 'risk']


    # LOAD SPARK DATA
    spark_list = os.listdir(spark_path)
    res = []
    for spark_file in spark_list:
        if spark_file.endswith('.xlsx'):
            res.append(pd.read_excel(spark_path+spark_file,
                                     skiprows=3,
                                     header=[0],
                                     index_col=[0],
                                     dtype={'Регистрационный номер': str, 'Код налогоплательщика':str}
                                    )
                      )
    inn_info = pd.concat(res).dropna(axis=0, how='all').reset_index(drop=True)
    inn_info = inn_info.rename(SPARK_RENAME, axis=1)[SPARK_COLUMNS].dropna(subset=['inn'])
    inn_info = inn_info.drop_duplicates(['inn'], keep='first')
    inn_info = inn_info.set_index('inn')
    del res


    # LOAD HOLDINGS INFO
    if holdings_path is not None:
        holdings = pd.read_csv(
            holdings_path,
            delimiter=';',
            error_bad_lines=False,
            dtype={'Код налогоплательщика':str}
        ).rename({
            'Код налогоплательщика': 'inn',
            'Группа': 'group',
        }, axis=1)[['inn', 'group']]
        mask = holdings['inn'].str.len()==9
        holdings.loc[mask, 'inn'] = holdings.loc[mask, 'inn'].apply(lambda x: '0'+x)
        holdings.set_index('inn', inplace=True)


    # JOIN HOLDINGS AND SPARK
    inn_info = pd.merge(inn_info, holdings, left_index=True, right_index=True, how='outer')

    # DUMP
    inn_info.to_parquet(save_path)
    
    
if __name__ == '__main__':
    main()