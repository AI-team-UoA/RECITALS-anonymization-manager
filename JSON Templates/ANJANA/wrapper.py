import pandas as pd
from anjana.anonymity import k_anonymity, l_diversity, t_closeness
import pycanon
import time
import json
import argparse

# Set up the argument parser
parser = argparse.ArgumentParser(description='Load hierarchies from a JSON file.')
parser.add_argument('json_file', type=str, help='Path to the JSON file')

# Parse the command line arguments
args = parser.parse_args()
json_file_path = args.json_file

# Template file reading
with open(json_file_path, 'r') as file:
    values = json.load(file)

data = pd.read_csv(values['data'])
quasi_ident = values['quasi_ident']
ident = values['ident']
k = values['k']
l = values['l']
t = values['t']
supp_level = values['supp_level']
sens_att = values.get('sens_att')

hierarchies = {
    key: dict(pd.read_csv(value, header=None))
    for key, value in values['hierarchies'].items()
}

# TODO: remove this somehow
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

start = time.time()

data_anon = k_anonymity(data, ident, quasi_ident, k, supp_level, hierarchies)
if not l == False:
    data_anon = l_diversity(
        data_anon, ident, quasi_ident, sens_att, k, l, supp_level, hierarchies
    )
    if not t == False:
        data_anon = t_closeness(
            data_anon, ident, quasi_ident, sens_att, k, t, supp_level, hierarchies
        )

end = time.time()

print(f"Elapsed time: {end-start}")
print(
    f"Value of k calculated: "
    f"\t{pycanon.anonymity.k_anonymity(data_anon, quasi_ident)}"
)
if not l == False:
    print(
        f"Value of l-diversity: "
        f"\t{pycanon.anonymity.l_diversity(data_anon, quasi_ident, [sens_att])}"
    )
    if not t == False:
        print(
            f"Value of t-closeness: "
            f"\t{pycanon.anonymity.t_closeness(data_anon, quasi_ident, [sens_att])}"
        )
        
