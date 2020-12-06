from ipywidgets import interact, widgets
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly import express as px


def dataframe_select(df, queries):
    df = df.copy()
    for query in queries:
        for key, values in query.items():
            df = df.loc[df[key].isin(values)]
    return df.reset_index(drop=True)


def min_transaction_filter(df, column, min_transaction):
    if min_transaction is None:
        return df
    tr_count = df[column].value_counts()
    valid_list = tr_count[tr_count >= min_transaction].index
    df.loc[~df[column].isin(valid_list), column] = 'MINOR'
    return df


def sankey(transaction_df, seller='inn_seller', buyer='inn_buyer', w=1_000, h=1_500, min_carpark_size_seller=None, min_carpark_size_buyer=None, min_transaction_seller=None, min_transaction_buyer=None,  bipartite=True, display_nan=True, display_minor=True, drop_cycle=False):
    
    transaction_df = transaction_df.copy()
    transaction_df['values'] = 1
    
    ########################################################################################
    
    transaction_df = min_transaction_filter(transaction_df, seller, min_transaction_seller)
    transaction_df = min_transaction_filter(transaction_df, buyer, min_transaction_buyer)
    
    ########################################################################################
        
    if drop_cycle:
        transaction_df = transaction_df.loc[transaction_df[seller] != transaction_df[buyer]]
    
    ########################################################################################
    
    if display_nan:
        transaction_df.loc[transaction_df[seller].isna(), seller] = 'UNKNOWN'
        transaction_df.loc[transaction_df[buyer].isna(), buyer] = 'UNKNOWN'
        
    ########################################################################################
    
    if not display_minor:
        transaction_df = transaction_df.loc[transaction_df[seller] != 'MINOR']
        transaction_df = transaction_df.loc[transaction_df[buyer] != 'MINOR']
        
    ########################################################################################
    
    tmp = transaction_df.groupby([seller, buyer])['values'].count().reset_index()
    
    seller_list = tmp[seller].unique()
    buyer_list = tmp[buyer].unique()
    
    label = np.concatenate((seller_list, buyer_list))
    
    seller_dict = {name: i for i, name in enumerate(seller_list)}
    buyer_dict = {name: i+len(seller_dict) for i, name in enumerate(buyer_list)}
    
    color = ['red' for name in seller_list] + ['blue' for name in buyer_list]
    
    ########################################################################################
    
    if bipartite is False:
        
        label = np.unique(label)
        seller_dict = buyer_dict = {name: i for i, name in enumerate(label)}
        color = 'green'
    
    source = tmp[seller].apply(lambda x: seller_dict[x]).tolist()
    target = tmp[buyer].apply(lambda x: buyer_dict[x]).tolist()
    value = tmp['values'].values
    
    ########################################################################################

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.2),
          label = label,
          color = color,
        ),
        link = dict(
          source = source,
          target = target,
          value = value,
      ))])

    fig.update_layout(title_text="Transaction Sankey Diagram", font_size=10)
    fig.update_layout(
        autosize=True,
        width=w,
        height=h,)
    
    return fig


def select_mult_w(df, column):
    values = df[column].unique()
    w = widgets.SelectMultiple(
        options=values,
        rows=min(10, len(values)),
        description=column,
        disabled=False
    )
    return w


class SelectMultipleInteract(widgets.HBox):

    def __init__(self, df, columns):
        
        self.selectors = []
        for col in columns:
            self.selectors.append(select_mult_w(df, col))           
        
        super().__init__(children=self.selectors)
        self._set_observes()

    def _set_observes(self):
        for widg in self.selectors:
            widg.observe(self._observed_function, names='value')

    def _observed_function(self, widg):
        for widg in self.selectors:
            print(widg.description)
            print(widg.get_interact_value())
            

def enrich_inn(df, inn_info):

    tmp = pd.merge(
        df, 
        inn_info.rename({col:col+'_seller' for col in list(inn_info)}, axis=1),
        left_on='inn_seller',
        right_index=True,
        how='left',
    )

    tmp = pd.merge(
        tmp, 
        inn_info.rename({col:col+'_buyer' for col in list(inn_info)}, axis=1),
        left_on='inn_buyer',
        right_index=True,
        how='left',
    )
    
    return tmp


def get_histogram(df, feature='age', sec_feature=None):
    # AGE OF 1ST APPEARANCE ON THE 2NDARY MARKET
    initial_secondary_market = df.query('operation_reason != "первичная регистрация"').sort_values('operation_date').groupby('vin').first()
    px.histogram(initial_secondary_market, x=feature, histnorm='probability density', color=sec_feature, opacity=0.75, title='1ST APPEARANCE ON THE 2NDARY MARKET ' + df['brand'].value_counts().index[0]).show()
    
    # AGE OF RESALED CARS
    resaled_carpark = df.query('operation_reason != "первичная регистрация"')
    px.histogram(resaled_carpark, x=feature, histnorm='probability density', color=sec_feature, opacity=0.75, title='RESALED CARS').show()
    
    
def get_transacation_count(df, feature_1='age', feature_2='operation_year'):
    return df.pivot_table(index=feature_1, columns=feature_2, values='vin', aggfunc='count').fillna(0).astype(int)


def prepare_date(df, inn_info, INN_FEATURES, VEHICLE_FEATURES, TRANSACTION_FEATURES):
    
    INN_SELLER_FEATURES = [col+'_seller' for col in INN_FEATURES]
    INN_BUYER_FEATURES = [col+'_buyer' for col in INN_FEATURES]


    df.sort_index(inplace=True)
    df['inn_buyer'] = df['inn']
    df[INN_BUYER_FEATURES] = df[INN_FEATURES]
    df[['inn_seller'] + INN_SELLER_FEATURES] = df.groupby('vin')[['inn_buyer'] + INN_BUYER_FEATURES].shift()
    df.loc[df['operation_reason'] == 'первичная регистрация', 'inn_seller'] = 'INITIAL'

    df = df.loc[df['inn_buyer'] != df['inn_seller']].reset_index()
    df['operation_year'] = df['operation_date'].dt.year
    
    df['age'] = df['operation_year'] - df['year']
    df['age'] = df['age'].astype(int)

    transaction_data = df[['inn_seller', 'inn_buyer']+INN_SELLER_FEATURES+INN_BUYER_FEATURES+VEHICLE_FEATURES+TRANSACTION_FEATURES]

    transaction_data = enrich_inn(transaction_data, inn_info)

    #########################################################################################

    transaction_data.loc[transaction_data['name_buyer'].isna(), 'name_buyer'] = transaction_data.loc[transaction_data['name_buyer'].isna(), 'inn_buyer']
    transaction_data.loc[transaction_data['name_seller'].isna(), 'name_seller'] = transaction_data.loc[transaction_data['name_seller'].isna(), 'inn_seller']

    transaction_data.loc[transaction_data['group_buyer'].isna(), 'group_buyer'] = transaction_data.loc[transaction_data['group_buyer'].isna(), 'name_buyer']
    transaction_data.loc[transaction_data['group_seller'].isna(), 'group_seller'] = transaction_data.loc[transaction_data['group_seller'].isna(), 'name_seller']

    #########################################################################################
    
    return transaction_data
