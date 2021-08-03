# scratchpad

import pandas as pd
#import plotly.express as px

#df = px.data.gapminder()

retain_dict = {
    'Cohort': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    #'Customers': [500, 450, 475, 460],
    1: [.9, .6, .3, .1],
    2: [.8, .5, .2, 0],
    3: [.7, .4 , .1, 0],
    4: [.6, .3 , 0, 0],
}

df= pd.DataFrame(retain_dict)

print(df)
