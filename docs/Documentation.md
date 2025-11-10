# Anonymization Manager API Documentation

## Overview

The Anonymization Manager is a Python API that provides privacy-preserving anonymization techniques for datasets. It is part of the open-source RECITALS platform and offers a unified interface to apply k-anonymity, l-diversity, and t-closeness privacy models to sensitive datasets. The API supports multiple backend libraries (ARX and ANJANA) and provides comprehensive analysis capabilities for anonymized results.

## Architecture

The API follows an adapter pattern architecture, allowing seamless switching between different anonymization backends while maintaining a consistent interface. The core components are:

### Core Components

1. **AnonymizationConfig**: Configuration class that defines all parameters for the anonymization process
2. **AnonymizationManager**: Main API class that orchestrates the anonymization workflow
3. **AnonymizedData**: Wrapper class that provides a unified interface to anonymization results
4. **Backend Adapters**: 
   - `ARXAnonymizer`: Adapter for the ARX Java library
   - `AnjanaAnonymizer`: Adapter for the ANJANA Python library

### Data Flow

```
Configuration → AnonymizationManager → Backend Adapter → Anonymization Result
```

## Supported Privacy Models

### 1. K-Anonymity

K-anonymity ensures that each record in the anonymized dataset is indistinguishable from at least k-1 other records with respect to quasi-identifiers. This prevents re-identification attacks by ensuring sufficient diversity in the quasi-identifier combinations.

**Configuration**: Set the `k` parameter (integer, typically ≥ 2)

### 2. L-Diversity

L-diversity extends k-anonymity by ensuring that each equivalence class (group of records with identical quasi-identifiers) contains at least l distinct values for sensitive attributes. This protects against homogeneity and background knowledge attacks.

**Configuration**: Set the `l` parameter (integer, typically ≥ 2)

**Note**: Currently, ANJANA backend supports only one sensitive attribute.

### 3. T-Closeness

T-closeness further enhances privacy by ensuring that the distribution of sensitive attributes within each equivalence class is close to the overall distribution in the dataset. The parameter `t` (0 ≤ t ≤ 1) defines the maximum allowed distance between distributions.

**Configuration**: Set the `t` parameter (float between 0 and 1)

**Note**: Currently, ANJANA backend supports only one sensitive attribute.

## Backend Libraries

### ARX (Anonymization and Risk Assessment)

- **Language**: Java-based library
- **Integration**: Uses JPype to bridge Python and Java
- **Library Version**: 3.9.2 (libarx-3.9.2.jar)
- **Features**:
  - Full support for all privacy models
  - Comprehensive quality metrics
  - Multiple sensitive attributes support
  - Advanced optimization algorithms

### ANJANA (Python Anonymization Library)

- **Language**: Pure Python library
- **Integration**: Direct Python import
- **Features**:
  - Lightweight and fast
  - Python-native implementation
  - Currently supports single sensitive attribute
  - Simpler implementation suitable for smaller datasets

**Default Backend**: ARX (when `backend` is not specified or set to `None`)

## Configuration

### AnonymizationConfig Class

The `AnonymizationConfig` class accepts the following parameters:

#### Required Parameters

- **data** (str): Path to the input dataset (CSV, Excel, JSON, or SQLite3 formats)
- **identifiers** (list[str]): List of attribute names that directly identify individuals (e.g., "Name", "SSN")
- **quasi_identifiers** (list[str]): List of attribute names that can be combined to identify individuals (e.g., "Age", "ZIP Code")
- **sensitive_attributes** (list[str]): List of attribute names containing sensitive information (e.g., "Disease", "Salary")
- **insensitive_attributes** (list[str]): List of attribute names that are neither identifying nor sensitive
- **hierarchies** (dict[str, str]): Dictionary mapping attribute names to paths of CSV hierarchy files

#### Optional Parameters

- **k** (int | None): K-anonymity parameter (default: None, meaning no k-anonymity)
- **l** (int | None): L-diversity parameter (default: None)
- **t** (float | None): T-closeness parameter (default: None)
- **suppression_limit** (float | None): Maximum percentage of records that can be suppressed (default: None for ARX, 50% for ANJANA)
- **backend** (str | None): Backend library to use ("arx" or "anjana", default: "arx")

### Configuration from JSON

You can load configuration from a JSON file using the `from_json` class method:

```python
config = AnonymizationConfig.from_json("path/to/config.json")
```

Example JSON configuration:

```json
{
    "data": "path/to/data.csv",
    "identifiers": ["Name", "LastName"],
    "quasi_identifiers": ["Age"],
    "sensitive_attributes": ["Disease"],
    "insensitive_attributes": ["Gender"],
    "hierarchies": {
        "Age": "path/to/age_hierarchy.csv"
    },
    "k": 2,
    "l": 2,
    "t": 0.5,
    "suppression_limit": 50,
    "backend": "arx"
}
```

### Hierarchy Files

Hierarchy files define generalization levels for quasi-identifiers. They are CSV files with the following structure:

- First column: Original attribute value
- Subsequent columns: Generalization levels (from most specific to most general)
- Last level typically contains "*" (representing complete suppression)

Example hierarchy file for Age (`age.csv`):

```csv
Age,Level1,Level2,Level3
18,10-19,0-49,*
19,10-19,0-49,*
23,20-29,0-49,*
...
```

## Usage

### Basic Usage

```python
from anonymization_manager import AnonymizationManager, AnonymizationConfig

# Create configuration
config = AnonymizationConfig(
    data="path/to/dataset.csv",
    identifiers=["Name", "LastName"],
    quasi_identifiers=["Age"],
    sensitive_attributes=["Disease"],
    insensitive_attributes=["Gender"],
    hierarchies={"Age": "path/to/age.csv"},
    k=2,
    l=2,
    t=0.5,
    suppression_limit=50,
    backend="arx"
)

# Perform anonymization
result = AnonymizationManager.anonymize(config)

# Access anonymized data
anonymized_df = result.get_anonymized_data_as_dataframe()
print(anonymized_df)
```

### Accessing Results

The `AnonymizedData` wrapper provides access to anonymized results through the following methods:

#### Data Access Methods

- **get_anonymized_data_as_dataframe()** → pd.DataFrame: Returns the anonymized dataset as a pandas DataFrame
- **get_raw_data_as_dataframe()** → pd.DataFrame: Returns the original dataset as a pandas DataFrame
- **store_as_csv(output_path: str)** → None: Saves the anonymized dataset to a CSV file
- **get_transformations()** → dict[str, int]: Returns the generalization levels applied to each quasi-identifier

#### Timing Information

- **get_anonymization_time()** → int: Returns anonymization time in milliseconds

#### Equivalence Class Statistics

- **get_average_equivalence_class_size()** → float: Average size of equivalence classes
- **get_max_equivalence_class_size()** → int: Maximum equivalence class size
- **get_min_equivalence_class_size()** → int: Minimum equivalence class size
- **get_number_of_equivalence_classes()** → int: Total number of equivalence classes
- **get_number_of_suppressed_records()** → int: Number of records removed during anonymization

#### Quality Metrics

- **get_discernibility_metric()** → float: Measures how distinguishable records are
- **get_average_class_size_metric()** → float: Average class size metric
- **get_granularity_metric(attribute: str)** → float: Granularity of generalization for a specific attribute
- **get_ssesst_metric()** → float: Sum of squared errors for sensitive attributes
- **get_record_level_squared_error_metric()** → float: Record-level squared error
- **get_attribute_level_squared_error_metric(attribute: str)** → float: Attribute-level squared error
- **get_non_uniform_entropy_metric(attribute: str)** → float: Non-uniform entropy for an attribute
- **get_generalization_intensity_metric(attribute: str)** → float: Generalization intensity for an attribute
- **get_ambiguity_metric()** → float: Ambiguity metric for the dataset

**Note**: Some quality metrics are not yet implemented in the ANJANA backend (marked with TODO comments in the code).

## Implementation Details

### ARX Adapter

The ARX adapter:

1. Loads the ARX Java library using JPype
2. Creates a data object from the input CSV file
3. Defines attribute types (identifying, quasi-identifying, sensitive, insensitive)
4. Loads generalization hierarchies from CSV files
5. Configures privacy models (k-anonymity, l-diversity, t-closeness)
6. Executes anonymization using ARX's optimization algorithms
7. Wraps the Java result object in a Python-friendly interface

### ANJANA Adapter

The ANJANA adapter:

1. Reads the input CSV file using pandas
2. Applies k-anonymity first (if k > 1)
3. Applies l-diversity (if specified)
4. Applies t-closeness (if specified)
5. Measures execution time
6. Returns results with metadata

The ANJANA adapter applies privacy models sequentially, building upon the previous model.

## Current Limitations

### ANJANA Backend Limitations

1. **Single Sensitive Attribute**: Only one sensitive attribute is currently supported
2. **File Format Support**: Currently assumes CSV format (no automatic file type detection)
3. **Incomplete Metrics**: Several quality metrics are not yet implemented:
   - `get_max_equivalence_class_size()`
   - `get_min_equivalence_class_size()`
   - `get_number_of_equivalence_classes()`
   - `get_average_class_size_metric()`
   - `get_granularity_metric()`
   - `get_ssesst_metric()` (partially implemented)
   - `get_record_level_squared_error_metric()`
   - `get_attribute_level_squared_error_metric()`
   - `get_non_uniform_entropy_metric()`
   - `get_generalization_intensity_metric()`
   - `get_ambiguity_metric()`

### General Limitations

1. **File Type Handling**: The code mentions support for CSV, Excel, JSON, and SQLite3, but automatic format detection is not implemented. Currently, CSV is the primary supported format.
2. **Hierarchy Validation**: No validation of hierarchy files before processing
3. **Error Handling**: Limited error handling for malformed configurations or data

## Future Enhancement Opportunities

### Feature Enhancements

1. **Multi-format Support**
   - Implement automatic file type detection
   - Add support for Excel, JSON, and SQLite3 formats
   - Create a common file loading function for both adapters

2. **ANJANA Backend Improvements**
   - Implement missing quality metrics
   - Add support for multiple sensitive attributes
   - Improve error handling and validation

3. **Configuration Enhancements**
   - Add configuration validation
   - Provide default hierarchies for common attributes
   - Support for programmatic hierarchy generation

4. **Performance Optimization**
   - Add caching mechanisms
   - Implement parallel processing for large datasets
   - Optimize memory usage for large datasets

5. **Additional Privacy Models**
   - Differential privacy
   - (α, k)-anonymity
   - m-invariance
   - δ-presence

6. **Enhanced Analysis**
   - Risk assessment metrics
   - Privacy-utility tradeoff visualization
   - Comparison tools between different anonymization strategies
   - Statistical analysis of anonymized data

7. **API Improvements**
   - REST API wrapper
   - Batch processing capabilities
   - Progress tracking and callbacks
   - Result comparison utilities

8. **Documentation and Examples**
   - Comprehensive usage examples
   - Best practices guide
   - Performance benchmarks
   - Case studies

9. **Testing and Validation**
   - Unit tests for all components
   - Integration tests
   - Validation against known anonymization benchmarks
   - Privacy guarantee verification

10. **User Experience**
    - CLI interface
    - Configuration wizard
    - Interactive result visualization
    - Template library for common use cases

## Technical Dependencies

### Core Dependencies

- **pandas**: Data manipulation and DataFrame operations
- **anjana** (>=1.1.0): Python anonymization library
- **jpype1** (>=1.6.0): Python-Java bridge for ARX integration
- **py4j** (==0.10.9.9): Alternative Python-Java bridge (if needed)

### Development Dependencies

- **basedpyright**: Type checking
- **ruff**: Code linting and formatting
- **pdoc**: Documentation generation

### Backend Libraries

- **ARX**: Java library (libarx-3.9.2.jar included)
- **ANJANA**: Python library (installed via pip)

## Project Structure

```
anonymization_manager/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration class
├── core.py                     # Main API classes
├── test.py                     # Example/test script
└── adapters/
    ├── arx/
    │   ├── arx.py             # ARX adapter implementation
    │   └── libarx-3.9.2.jar   # ARX Java library
    └── anjana/
        └── anjana.py          # ANJANA adapter implementation
```

## Examples

### Example 1: Basic K-Anonymity

```python
from anonymization_manager import AnonymizationManager, AnonymizationConfig

config = AnonymizationConfig(
    data="examples/chatgpt_sample.csv",
    identifiers=["Name", "LastName"],
    quasi_identifiers=["Age"],
    sensitive_attributes=["Disease"],
    insensitive_attributes=["Gender"],
    hierarchies={"Age": "examples/age.csv"},
    k=2,
    backend="arx"
)

result = AnonymizationManager.anonymize(config)
print(result.get_anonymized_data_as_dataframe())
print(f"Suppressed records: {result.get_number_of_suppressed_records()}")
print(f"Anonymization time: {result.get_anonymization_time()} ms")
```

### Example 2: Combined Privacy Models

```python
config = AnonymizationConfig(
    data="examples/chatgpt_sample.csv",
    identifiers=["Name", "LastName"],
    quasi_identifiers=["Age"],
    sensitive_attributes=["Disease"],
    insensitive_attributes=["Gender"],
    hierarchies={"Age": "examples/age.csv"},
    k=2,
    l=2,
    t=0.5,
    suppression_limit=50,
    backend="anjana"
)

result = AnonymizationManager.anonymize(config)
print(f"Average equivalence class size: {result.get_average_equivalence_class_size()}")
print(f"Transformations: {result.get_transformations()}")
```

### Example 3: Using JSON Configuration

```python
config = AnonymizationConfig.from_json("templates/sample.json")
result = AnonymizationManager.anonymize(config)
result.store_as_csv("output/anonymized_data.csv")
```

## Best Practices

1. **Start with k-anonymity**: Begin with k-anonymity and add l-diversity and t-closeness only if needed for stronger privacy guarantees.

2. **Choose appropriate k values**: Higher k values provide better privacy but reduce data utility. Typical values range from 2 to 10.

3. **Design hierarchies carefully**: Well-designed hierarchies balance privacy and utility. Test different hierarchy designs to find the optimal tradeoff.

4. **Set suppression limits**: Use suppression limits to prevent excessive data loss. Monitor the number of suppressed records.

5. **Compare backends**: Test both ARX and ANJANA backends to find which works best for your dataset and requirements.

6. **Validate results**: Always check quality metrics to ensure the anonymized data maintains sufficient utility for your use case.

7. **Test with sample data**: Start with small datasets to understand the behavior before processing large datasets.

## Contributing

When contributing to this project:

1. Follow Google-style docstrings
2. Ensure all docstrings end with periods
3. Use type hints throughout
4. Run linting with ruff (line length: 79)
5. Follow the adapter pattern for new backends
6. Maintain backward compatibility with the API

## License and Authors

This project is part of the RECITALS platform:

- **Authors**: Georgios Stamoulis, Konstantinos Chousos, Dimitris Pavlou
- **Institution**: University of Athens (Department of Informatics)

## References

- **ARX**: Comprehensive anonymization framework for privacy-preserving data publishing
- **ANJANA**: Python library for k-anonymity and related privacy models
- **RECITALS Platform**: Open-source platform for privacy-preserving data processing

