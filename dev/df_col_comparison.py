# %%

import pandas as pd

df1 = pd.DataFrame({
    'SupplyAmount': [1, 2, 3],
})

df2 = pd.DataFrame({
    'SupplyAmount': [1, 2, 0],
})

if (df1['SupplyAmount'] != df2['SupplyAmount']).any():
    print('Different!')
else:
    print('Same!')