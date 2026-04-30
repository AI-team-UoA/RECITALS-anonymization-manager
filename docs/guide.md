# Guide
## Attribute Classification
When using the RECITALS Anonymization Manager, you must classify every column in your dataset into one of four categories. This classification dictates how the privacy models *(k,l,t)* treat the data.

### Attribute Types
| Attribute Type | Description | Action |
| :--- | :--- | :--- |
| **Identifying** | Directly identifies an individual (e.g. Name, SSN, Phone Number) | **Removed** |
| **Quasi-Identifying** | Indirectly identifies via combination (e.g. Age, ZIP Code) | **Altered** |
| **Sensitive** | Harmful information (e.g. Diagnosis, Salary) | **Retained** through *(l,t)* models. |
| **Insensitive** | General info with no privacy risk  | **Ignored** |

### Example

This example shows how you can define the attribute types for each column of the dataset.
```python
config = AnonymizationConfig(
    data="dummy_set.csv",

    # Defines Identifiers
    identifiers=["id1", "id2",...,"idn"],

    # Defines Quasi-Identifiers
    quasi_identifiers=["qid1", "qid2",...,"qidn"],

    # Defines Sensitive Attributes
    sensitive_attributes=["sa1", "sa2",...,"san"],

    # Defines Insensitive Attributes
    insensitive_attributes=["ia1", "ia2",...,"ian"],

    ...

)
```

## Hierarchies
In the RECITALS Anonymization Manager, hierarchies are the most important part of the generalization process. They dictate how to transform specific data into broader categories (e.g. turning "25" into "20-30" or "Greece" into "Europe").

These are provided as `.csv` files where each column represents a level of abstraction.

### Structure
A hierarchy file must be a `.csv` where:

- **Column 0 (Level 0)**: The original, raw data values.
- **Column 1 (Level 1)**: The first level of generalization.
- **Column 2 (Level 2)**: The second level of generalization.
- ...
- **Column k (Level k)**: Usually contains a `*` to represent total suppression.

### Example 1. Numerical Hierarchy (Age)
| Level (0) | Level 1 | Level 2 | Level 3 |
| :--- | :--- | :--- | :--- |
| 23 | 20-25 | 20-30 | * |
| 21 | 20-25 | 20-30 | * |
| 28 | 25-30 | 20-30 | * |
| 31 | 30-35 | 30-40 | * |

### Example 2. Categorical Hierarchy (Location)
| Level (0) | Level 1 | Level 2 | Level 3 |
| :--- | :--- | :--- | :--- |
| Athens | Greece | Europe | * |
| Thesaloniki | Greece | Europe | * |
| Rome | Italy | Europe | * |
| Delhi | India | Asia | * |

### Hierarchy Usage
To use hierarchies, simply map each column name to the appropriate hierarchy file path within the `AnonymizationConfig`.
```python
    config = AnonymizationConfig(
        data="dataset.csv",
        quasi_identifiers=["age", "location"]

        # Defines the hierarchies.
        hierarchies={
            "age":"hierarchies/age.csv",
            "location":"hierarchies/location.csv"
        }
    )
```
## Privacy Models

### Using k-anonymity
To use *k*-anonymity, specify the *k* threshold and provide hierarchies for all quasi-identifiers. This ensures that each record is indistinguishable from at least *k*-1 records.

!!! warning "Hierarchies" 
    You must provide hierarchies for every quasi-identifier!
```python
from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/arx_example/data/adult.csv",
        identifiers=["education-num"],
        quasi_identifiers=[
            "age",
            "native-country",
            "race",
            "sex",
            "marital-status",
            "occupation",
            "workclass",
            "education",
        ],
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/arx_example/hierarchies/age.csv",
            "native-country": "examples/arx_example/hierarchies/country.csv",
            "race": "examples/arx_example/hierarchies/race.csv",
            "sex": "examples/arx_example/hierarchies/sex.csv",
            "marital-status": "examples/arx_example/hierarchies/marital.csv",
            "occupation": "examples/arx_example/hierarchies/occupation.csv",
            "workclass": "examples/arx_example/hierarchies/workclass.csv",
            "education": "examples/arx_example/hierarchies/education.csv",
        },
        k=3,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```
### Using l-diversity
*l*-diversity extends *k*-anonymity by guaranteeing that each equivalence class has at least *l* well-preserved values for the sensitive attributes. To use *l*-diversity, simply pass the *l* parameter to the `AnonymizationConfig`.

!!! warning "Sensitive Attributes" 
    In constrast to *k*-anonymity, *l*-diversity requires that the user has defined the sensitive attributes!
```python
from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/arx_example/data/adult.csv",
        identifiers=["education-num"],
        quasi_identifiers=[
            "age",
            "native-country",
            "race",
            "sex",
            "marital-status",
            "occupation",
            "workclass",
            "education",
        ],
        sensitive_attributes=["salary-class"],
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/arx_example/hierarchies/age.csv",
            "native-country": "examples/arx_example/hierarchies/country.csv",
            "race": "examples/arx_example/hierarchies/race.csv",
            "sex": "examples/arx_example/hierarchies/sex.csv",
            "marital-status": "examples/arx_example/hierarchies/marital.csv",
            "occupation": "examples/arx_example/hierarchies/occupation.csv",
            "workclass": "examples/arx_example/hierarchies/workclass.csv",
            "education": "examples/arx_example/hierarchies/education.csv",
        },
        l=2,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```
### Using t-closeness
*t*-closeness requires that the distribution of a sensitive attribute in any equivalence class is close to the distribution of the attribute in the entire table (within a threshold parameter *t*). To use *t*-closeness, simply pass the parameter *t* to the `AnonymizationConfig`.
!!! warning "Sensitive Attributes" 
    In constrast to *k*-anonymity, *t*-closeness requires that the user has defined the sensitive attributes!
```python
from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/arx_example/data/adult.csv",
        identifiers=["education-num"],
        quasi_identifiers=[
            "age",
            "native-country",
            "race",
            "sex",
            "marital-status",
            "occupation",
            "workclass",
            "education",
        ],
        sensitive_attributes=["salary-class"],
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/arx_example/hierarchies/age.csv",
            "native-country": "examples/arx_example/hierarchies/country.csv",
            "race": "examples/arx_example/hierarchies/race.csv",
            "sex": "examples/arx_example/hierarchies/sex.csv",
            "marital-status": "examples/arx_example/hierarchies/marital.csv",
            "occupation": "examples/arx_example/hierarchies/occupation.csv",
            "workclass": "examples/arx_example/hierarchies/workclass.csv",
            "education": "examples/arx_example/hierarchies/education.csv",
        },
        t=0.5,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```
### Using All Models
It is highly recommended to use a combination of privacy models. While *k*-anonymity protects against **identity disclosure** (i.e. linking a person to a table entry), *l*-diversity and *t*-closeness protect against **attribute disclosure** (i.e. learning sensitive information about a person).

!!! success "Best Practice"
    Using all three models *(k,l,t)* provides a more resilient approach, satisfying stricter privacy guarantees!

```python
from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/arx_example/data/adult.csv",
        identifiers=["education-num"],
        quasi_identifiers=[
            "age",
            "native-country",
            "race",
            "sex",
            "marital-status",
            "occupation",
            "workclass",
            "education",
        ],
        sensitive_attributes=["salary-class"],
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/arx_example/hierarchies/age.csv",
            "native-country": "examples/arx_example/hierarchies/country.csv",
            "race": "examples/arx_example/hierarchies/race.csv",
            "sex": "examples/arx_example/hierarchies/sex.csv",
            "marital-status": "examples/arx_example/hierarchies/marital.csv",
            "occupation": "examples/arx_example/hierarchies/occupation.csv",
            "workclass": "examples/arx_example/hierarchies/workclass.csv",
            "education": "examples/arx_example/hierarchies/education.csv",
        },
        k=3,
        l=2,
        t=0.5,
    )

    result = AnonymizationManager.anonymize(config)
    print(result.get_anonymized_data_as_dataframe())
```
## Suppression
Sometimes, a dataset might contain outliers that make anonymization difficult without aggressively generalizing attributes. 
By using suppression, you effectively allow the exclusion of a small percentage of records to maintain data usability.
!!! tip "Suppression Limit"
    A `suppression_limit=0.05` means that the algorithm is allowed to delete up to **5%** of the records if it helps to satisfy the *k,l,t* requirements.
```python
from anonymization_manager import *

if __name__ == "__main__":
    config = AnonymizationConfig(
        data="examples/arx_example/data/adult.csv",
        identifiers=["education-num"],
        quasi_identifiers=[
            "age",
            "native-country",
            "race",
            "sex",
            "marital-status",
            "occupation",
            "workclass",
            "education",
        ],
        sensitive_attributes=["salary-class", "capital-gain", "capital-loss"],
        insensitive_attributes=["hours-per-week"],
        hierarchies={
            "age": "examples/arx_example/hierarchies/age.csv",
            "native-country": "examples/arx_example/hierarchies/country.csv",
            "race": "examples/arx_example/hierarchies/race.csv",
            "sex": "examples/arx_example/hierarchies/sex.csv",
            "marital-status": "examples/arx_example/hierarchies/marital.csv",
            "occupation": "examples/arx_example/hierarchies/occupation.csv",
            "workclass": "examples/arx_example/hierarchies/workclass.csv",
            "education": "examples/arx_example/hierarchies/education.csv",
        },
        k=4,
        l=2,
        suppression_limit=0.05
    )

    result = AnonymizationManager.anonymize(config)
    dataframe = print(result.get_anonymized_data_as_dataframe())
```