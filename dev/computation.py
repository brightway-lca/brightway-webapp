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

df_csv = pd.read_csv('/Users/michaelweinold/Downloads/data.csv')