"""load backup into Dataframe and view"""

import pandas as pd

df = pd.read_json("customers.json")
df.to_csv(f'customers.csv', index=False)