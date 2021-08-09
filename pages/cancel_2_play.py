import pandas as pd

mock = {
    'Reason 1' : [95, 75, 85, 65, 60],
    'Reason 2' : [80, 90, 45, 55, 75],
}

indx = [
    'January 2021',
    'February 2021',
    'March 2021',
    'April 2021',
    'May 2021'
]

df_mock = pd.DataFrame(mock, index = indx)

print(df_mock)
