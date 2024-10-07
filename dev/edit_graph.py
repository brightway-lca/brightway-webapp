# %%
import pandas as pd

data_original = {
    'uid': [0, 1, 2, 3],
    'description': ['cardboard', 'paper', 'wood', 'electricity'],
    'production': [1, 0.5, 0.2, 0.1],
    'emissions_intensity': [1.5, 2.2, 0.7, 0.2],
    'branch': [[], [0,1], [0,1,2], [0,1,2,3]]
}

df_original = pd.DataFrame(data_original)

def compute_direct_emissions(df):
    df['direct_emissions'] = df['production'] * df['emissions_intensity']
    return df

data_after_user_input = {
    'uid': [0, 1, 2, 3, 4],
    'description': ['cardboard', 'paper', 'wood', 'electricity', 'oil'],
    'production': [1, 0.5, 0.2, 0.1, 0.05],
    'production_user': [np.NaN, 0.25, np.NaN, 0.18, np.NaN],
    'emissions_intensity': [1.5, 2.2, 0.1, 0.2, 1],
    'branch': [[], [0,1], [0,1,2], [0,1,2,3], [0,1,2,3,4]]
}

df_after_user_input = pd.DataFrame(data_after_user_input)


def create_user_input_column(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
        column_name: str
    ) -> pd.DataFrame:
    """
    Creates a new column in the 'original' DataFrame with the user input data.

    For instance, given an "original" DataFrame of the kind:

    | UID | SupplyAmount |
    |-----|--------------|
    | 0   | 1            |
    | 1   | 0.5          |
    | 2   | 0.2          |

    and a "user input" DataFrame of the kind:

    | UID | SupplyAmount |
    |-----|--------------|
    | 0   | NaN          |
    | 1   | 0.25         |
    | 2   | NaN          |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount | USERSupplyAmount |
    |-----|--------------|------------------|
    | 0   | 1            | NaN              |
    | 1   | 0.5          | 0.25             |
    | 2   | 0.2          | NaN              |

    Parameters
    ----------
    df_original : pd.DataFrame
        Original DataFrame.

    df_user_input : pd.DataFrame
        User input DataFrame.
    """
    
    df_original = df_original.set_index('uid')
    df_user_input = df_user_input.set_index('uid')

    df_original[f'USER{column_name}'] = df_user_input[column_name]

    return df_original.reset_index()


def update_production_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount | USERSupplyAmount | Branch        |
    |-----|--------------|------------------|---------------|
    | 0   | 1            | NaN              | []            |
    | 1   | 0.5          | 0.25             | [0,1]         |
    | 2   | 0.2          | NaN              | [0,1,2]       |
    | 3   | 0.1          | NaN              | [0,3]         |
    | 4   | 0.1          | 0.18             | [0,1,2,4]     |
    | 5   | 0.05         | NaN              | [0,1,2,4,5]   |
    | 6   | 0.01         | NaN              | [0,1,2,4,5,6] |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount      | Branch        |
    |-----|-------------------|---------------|
    | 0   | 1                 | []            |
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

    df_user_input_only = df[df['USERSupplyAmount'].notna()]
    dict_user_input = dict(zip(df_user_input_only['UID'], df_user_input_only['USERSupplyAmount']))

    """
    For the example DataFrame from the docstrings above,
    the dict_user_input would be:

    dict_user_data = {
        1: 0.25,
        4: 0.18
    }
    """

    def multiplier(row):
        for branch_uid in reversed(row['Branch']):
            if branch_uid in dict_user_input:
                return row['SupplyAmount'] * dict_user_input[branch_uid]
        return row['SupplyAmount']

    df['SupplyAmount'] = df.apply(multiplier, axis=1)

    return df


def recompute_direct_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recomputes the direct emissions of each node in the DataFrame.
    """
    
    df['direct_emissions'] = df['production'] * df['emissions_intensity']
    
    return df

def 


def highlight_edited_tabulator_rows(pd.DataFrame) -> pd.DataFrame:
    """
    def highlight(s):
    if s.duration > 5:
        return ['background-color: yellow'] * len(s)

    https://panel.holoviz.org/reference/widgets/Tabulator.html#styling
    https://stackoverflow.com/a/48306463
    """