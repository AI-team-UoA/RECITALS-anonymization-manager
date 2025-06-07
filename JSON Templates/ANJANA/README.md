# ANJANA usage through json templates

## Setup

1. Create a Python3.10 virtual environment in `.venv` and activate it.

``` shell
$ python3.10 -m venv .venv
$ source .venv/bin/activate # for bash
```

1. Install the dependencies.

``` shell
pip install -r requirements.txt
```

## JSON templates structure

Each template has the necessary attributes for ANJANA to function. Namely, it *must* include:

1. `data`: The path to the dataset (csv files only for now).
2. `ident`: The identifier's column name.
3. `quasi_ident`: A list of column names of the dataset's QAs.
4. `supp_level`: The suppression level for ANJANA (float between 0 and 100).
5. `hierarchies`: A dictionary with QAs as keys and the path to the corresponding hierarchy csv file as value.
6. `k`: The value of $k$ for $k$-anonymity.

For $l$-diversity, the json template must also include:

1. `sens_att`: The sensitive attribute column name (not needed for $k$-anonymity).
2. `l`: The value of $l$ for $l$-diversity.

And for $t$-closeness:

1. `t`: The value of $t$ for $t$-closeness.

## Example usage

The provided templates use the `adult.csv` dataset [1] and use the values used in ANJANA's official examples [2]. To use a specific template, pass it as a CLI argument to the `wrapper.py` script, like so:

``` shell
$ python ./wrapper.py sample_templates/t-closeness.json
```

## References

[1] R. K. Barry Becker, “Adult.” UCI Machine Learning Repository, 1996. doi: 10.24432/C5XW20. Available: https://archive.ics.uci.edu/dataset/2

[2] J. Sáinz-Pardo Díaz and Á. López García, “Anjana.” May 2024. Available: https://github.com/IFCA-Advanced-Computing/anjana
