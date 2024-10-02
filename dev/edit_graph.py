import pandas as pd

# %%

data = {
    'uid': [0, 1, 2, 3],
    'description': ['cardboard', 'paper', 'wood', 'electricity'],
    'production': [True, False, True, False],
    'emissions_intensity': [1.5, 2.2, 0.7, 0.2],
}

df = pd.DataFrame(data)