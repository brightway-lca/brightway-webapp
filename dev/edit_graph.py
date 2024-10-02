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
    'uid': [0, 1, 2, 3],
    'description': ['cardboard', 'paper', 'wood', 'electricity'],
    'production': [1, 0.25, 0.2, 0.1],
    'production_override': [False, True, False, False],
    'emissions_intensity': [1.5, 2.2, 0.1, 0.2],
    'emissions_intensity_override': [False, False, True, False],
    'branch': [[], [0,1], [0,1,2], [0,1,2,3]]
}

df_after_user_input = pd.DataFrame(data_after_user_input)


# %%
