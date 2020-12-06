import pandas as pd
import numpy as np
import plotly.graph_objects as go


def intersection(a, b):
    return list(set(a).intersection(set(b)))


def filter_zeros(df):
    df = df.copy()
    return df.loc[df.sum(axis=1) > 0, df.sum(axis=0) > 0]

def get_inn_index(inn, inn_dict):
    return [inn_dict[inn] for inn in inn]


def get_transaction_sample(seller_list, buyer_list, transaction_matrix, inn_dict):
    
    seller_ind = get_inn_index(seller_list, inn_dict)
    buyer_ind = get_inn_index(buyer_list, inn_dict)
        
    return transaction_matrix[seller_ind][:,buyer_ind]


def transaction_dataframe(seller_list, buyer_list, transaction_matrix, inn_dict):
    
    transaction_matrix = get_transaction_sample(seller_list, buyer_list, transaction_matrix, inn_dict)
    return pd.DataFrame(transaction_matrix.toarray(), index=seller_list, columns=buyer_list).astype(int)


def group_transaction(df, seller_group, buyer_group):
    return df.groupby(seller_group, axis=0).sum().groupby(buyer_group, axis=1).sum()


def sankey_1(tmp, width=1500, height=2000):
    label = list(tmp)
    arr = tmp.values
    source, target = np.where(arr > 0)
    value = arr[source, target]

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = label,
          color = "blue"
        ),
        link = dict(
          source = source,
          target = target,
          value = value
      ))])

    fig.update_layout(title_text="Transaction Sankey Diagram", font_size=10)
    fig.update_layout(
        autosize=True,
        width=width,
        height=height,)
    return fig


def sankey_2(tmp, width=1500, height=2000):
    seller_list = [inn for inn in tmp.index.tolist()]
    buyer_list = [inn for inn in tmp.columns.tolist()]
    label = seller_list + buyer_list

    arr = tmp.values
    source, target = np.where(arr > 0)
    value = arr[source, target]
    target += len(arr)

    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.2),
          label = label,
          color = "red"
        ),
        link = dict(
          source = source,
          target = target,
          value = value
      ))])

    fig.update_layout(title_text="Transaction Sankey Diagram", font_size=10)
    fig.update_layout(
        autosize=True,
        width=width,
        height=height,)
    return fig