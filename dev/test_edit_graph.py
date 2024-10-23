# %%
import pandas as pd
import numpy as np


data_original = {
    'UID': [0, 1, 2, 3, 4, 5, 6],
    'SupplyAmount': [1000, 500, 70, 100, 90, 10, 5],
    'BurdenIntensity': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
    'Branch': [np.NaN, [0, 1], [0, 1, 2], [0, 3], [0, 1, 2, 4], [0, 1, 2, 4, 5], [0, 1, 2, 4, 5, 6]]
}

df_original = pd.DataFrame(data_original)

data_user_input = {
    'UID': [0, 1, 2, 3, 4, 5, 6],
    'SupplyAmount': [1000, 0, 70, 100, 40, 10, 5],
    'BurdenIntensity': [0.1, 0.5, 0.3, 0.4, 0.5, 2, 0.7],
    'Branch': [np.NaN, [0, 1], [0, 1, 2], [0, 3], [0, 1, 2, 4], [0, 1, 2, 4, 5], [0, 1, 2, 4, 5, 6]]
}

df_user_input = pd.DataFrame(data_user_input)


def create_user_input_column(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
        column_name: str
    ) -> pd.DataFrame:
    """
    Creates a new column in the 'original' DataFrame where only the
    user-supplied values are kept. The other values are replaced by NaN.

    For instance, given an "original" DataFrame of the kind:

    | UID | SupplyAmount |
    |-----|--------------|
    | 0   | 1            |
    | 1   | 0.5          |
    | 2   | 0.2          |

    and a "user input" DataFrame of the kind:

    | UID | SupplyAmount |
    |-----|--------------|
    | 0   | 1            |
    | 1   | 0            |
    | 2   | 0.2          |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER |
    |-----|--------------|-------------------|
    | 0   | 1            | NaN               |
    | 1   | 0.5          | 0                 |
    | 2   | 0.2          | NaN               |

    Parameters
    ----------
    df_original : pd.DataFrame
        Original DataFrame.

    df_user_input : pd.DataFrame
        User input DataFrame.
    """
    
    df_merged = pd.merge(
        df_original,
        df_user_input[['UID', column_name]],
        on='UID',
        how='left',
        suffixes=('', '_USER')
    )

    df_merged[f'{column_name}_USER'] = np.where(
        df_merged[f'{column_name}_USER'] != df_merged[f'{column_name}'],
        df_merged[f'{column_name}_USER'],
        np.nan
    )

    return df_merged


def update_production_based_on_user_data(
        df: pd.DataFrame,
        column_name: str
    ) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | Branch        |
    |-----|--------------|-------------------|---------------|
    | 0   | 1            | NaN               | NaN           |
    | 1   | 0.5          | 0.25              | [0,1]         |
    | 2   | 0.2          | NaN               | [0,1,2]       |
    | 3   | 0.1          | NaN               | [0,3]         |
    | 4   | 0.1          | 0.18              | [0,1,2,4]     |
    | 5   | 0.05         | NaN               | [0,1,2,4,5]   |
    | 6   | 0.01         | NaN               | [0,1,2,4,5,6] |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount      | Branch        |
    |-----|-------------------|---------------|
    | 0   | 1                 | NaN           |
    | 1   | 0.25              | [0,1]         |
    | 2   | 0.2 * (0.25/0.5)  | [0,1,2]       |
    | 3   | 0.1               | [0,3]         |
    | 4   | 0.18              | [0,1,2,4]     |
    | 5   | 0.05 * (0.1/0.18) | [0,1,2,4,5]   |
    | 6   | 0.01 * (0.1/0.18) | [0,1,2,4,5,6] |

    Notes
    -----

    As we can see, the function updates production only
    for those nodes upstream of a node with 'production_user':

    - Node 2 is upstream of node 1, which has a 'production_user' value.
    - Node 3 is NOT upstream of node 1. It is upstream of node 0, but node 0 does not have a 'production_user' value.

    As we can see, the function always takes the "most recent"
    'production_user' value upstream of a node:

    - Node 5 is upstream of node 4, which has a 'production_user' value.
    - Node 4 is upstream of node 1, which also has a 'production_user' value.

    In this case, the function takes the 'production_user' value of node 4, not of node 1.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame. Must have the columns 'production', 'production_user' and 'branch'.

    Returns
    -------
    pd.DataFrame
        Output DataFrame.
    """

    df_filtered = df[~df[f'{column_name}_USER'].isna()]
    dict_user_input = df_filtered.set_index('UID').to_dict()[f'{column_name}_USER']
    
    """
    For the example DataFrame from the docstrings above,
    the dict_user_input would be:

    dict_user_input = {
        1: 0.25,
        4: 0.18
    }
    """

    df = df.copy(deep=True)
    def multiplier(row):
        if not isinstance(row['Branch'], list):
            return row[column_name]
        for branch_UID in reversed(row['Branch']):
            if branch_UID in dict_user_input:
                return row[column_name] * dict_user_input[branch_UID]
        return row[column_name]

    df[column_name] = df.apply(multiplier, axis=1)
    df.drop(columns=[f'{column_name}_USER'], inplace=True)

    return df, dict_user_input


df_user_col = create_user_input_column(
    df_original=df_original,
    df_user_input=df_user_input,
    column_name='SupplyAmount'
)
