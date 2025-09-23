'''
    Dependencies.
'''
import pandas as pd
import numpy as np
from faker import Faker


output = "data"

'''
    Creates the data.
'''
def create_data(n:int):
    faker = Faker()
    data = {
        "name" : [faker.first_name() for _ in range(n)],
        "last_name" : [faker.last_name() for _ in range(n)],
        "city" : [faker.city() for _ in range(n)],
        "country" : [faker.country() for _ in range(n)],
        "age" : np.random.randint(18, 90, n),
        "credit_score" : np.random.randint(1, 801, n),
        "balance" : np.round(np.random.normal(loc=2740, scale=1234, size=n)).astype("int"),
        "defaulted" : np.random.choice(["yes", "no"], size=n, p=[0.2, 0.8])
    }

    df = pd.DataFrame(data)
    df.to_csv(f"{output}/data.csv", index=False)

    return df

'''
    Creates a hierachy for age.
'''
def create_hierarchy_age(df):
    age_levels = []
    for age in sorted(df["age"].unique()):
        if age < 20:
            level1 = "<20"
            level2 = "[18-19]"
        elif age < 30:
            level1 = "[20-29]"
            level2 = "[20-39]"
        elif age < 40:
            level1 = "[30-39]"
            level2 = "[20-39]"
        elif age < 50:
            level1 = "[40-49]"
            level2 = "[40-59]"
        elif age < 60:
            level1 = "[50-59]"
            level2 = "[40-59]"
        elif age < 70:
            level1 = "[60-69]"
            level2 = "[60-89]"
        elif age < 80:
            level1 = "[70-79]"
            level2 = "[60-89]"
        elif age < 90:
            level1 = "[80-89]"
            level2 = "[80-99]"
        age_levels.append([str(age), level1, level2, "[0-99]"])

    pd.DataFrame(age_levels).drop_duplicates().to_csv(
        f"{output}/age_hierarchy.csv", index=False, header=False
    )

'''
    Creates a hierachy for balances.
'''
def create_hierarchy_balance(df):
    balance_levels = []

    for bal in df["balance"]:
        if bal < 1000:
            level1 = "[0-999]"
        elif bal < 5000:
            level1 = "[1000-4999]"
        elif bal < 10000:
            level1 = "[5000-9999]"
        elif bal < 100000:
            level1 = "[10000-99999]"
        
        balance_levels.append([str(bal), level1, "[0-inf]"])
    pd.DataFrame(balance_levels).drop_duplicates().to_csv(
        f"{output}/balance_hierarchy.csv", index=False, header=False
    )

'''
    Creates a hierarchy for scores.
'''
def create_hierarchy_credit_score(df):
    credit_levels = []

    for score in df["credit_score"]:
        if score < 200:
            level1 = "[0-199]"
            level2 = "[0-399]"
        elif score < 400:
            level1 = "[200-399]"
            level2 = "[0-399]"
        elif score < 600:
            level1 = "[400-599]"
            level2 = "[400-799]"
        elif score < 800:
            level1 = "[600-799]"
            level2 = "[400-799]"
        
        credit_levels.append([str(score), level1, level2, "[0-799]"])
    pd.DataFrame(credit_levels).drop_duplicates().to_csv(
        f"{output}/credit_score_hierarchy.csv", index=False, header=False
    )

if __name__ == "__main__":
    df = create_data(100)
    create_hierarchy_age(df)
    create_hierarchy_balance(df)
    create_hierarchy_credit_score(df)

