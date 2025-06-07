import pandas as pd
from anjana.anonymity import k_anonymity
import pycanon
import time
import json

with open('templates/k_anonymity.json', 'r') as file:
    values = json.load(file)

data = pd.read_csv(values['data'])  # 32561 rows
data.columns = data.columns.str.strip()
cols = [
    'workclass',
    'education',
    'marital-status',
    'occupation',
    'sex',
    'native-country',
]
for col in cols:
    data[col] = data[col].str.strip()
print(data)  # 32561 rows
quasi_ident = values['quasi_ident']
ident = values['ident']
k = 10
supp_level = 50

hierarchies = {
    key: dict(pd.read_csv(value, header=None))
    for key, value in values['hierarchies'].items()
}

start = time.time()
data_anon = k_anonymity(data, ident, quasi_ident, k, supp_level, hierarchies)
end = time.time()
print(f'Elapsed time: {end-start}')
print(f'Value of k calculated: {pycanon.anonymity.k_anonymity(data_anon, quasi_ident)}')

# Elapsed time: 0.9592475891113281
# Value of k calculated: 10

print(f'Number of records suppressed: {len(data) - len(data_anon)}')
print(
    f'Percentage of records suppressed: {100 * (len(data) - len(data_anon)) / len(data)} %'
)

# Number of records suppressed: 14234
# Percentage of records suppressed: 43.71487362181751 %
