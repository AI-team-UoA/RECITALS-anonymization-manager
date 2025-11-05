# Feature Enhancement Implementation Guide

This document provides detailed instructions for implementing each feature enhancement listed in the Documentation.md file. Each section includes a plan, source files to modify, and recommended third-party libraries.

## Implementation Priority Recommendations

### High Priority (Foundation)
1. **Multi-format Support** - Enables broader use cases
2. **ANJANA Backend Improvements** - Completes existing functionality
3. **Testing and Validation** - Ensures quality and reliability

### Medium Priority (Enhancement)
4. **Configuration Enhancements** - Improves usability
5. **Performance Optimization** - Enables larger datasets
6. **User Experience** - Makes tool more accessible

### Lower Priority (Advanced Features)
7. **Enhanced Analysis** - Advanced analytics
8. **API Improvements** - Web/API integration
9. **Additional Privacy Models** - Research and development
10. **Documentation and Examples** - Ongoing effort

---

## 1. Multi-format Support

### Objective
Implement automatic file type detection and support for Excel, JSON, and SQLite3 formats in addition to CSV.

### Implementation Plan

#### Step 1: Create a Common File Loader Module
- **New File**: `src/anonymization_manager/utils/file_loader.py`
- **Purpose**: Centralize file loading logic for all supported formats

**Implementation Details:**
```python
# Structure:
- detect_file_type(file_path: str) -> str
- load_data(file_path: str, file_type: str | None = None) -> pd.DataFrame
- validate_file_exists(file_path: str) -> bool
```

**Third-Party Libraries:**
- `pandas` (already in use): Supports CSV, Excel, JSON via `pd.read_csv()`, `pd.read_excel()`, `pd.read_json()`
- `openpyxl` (for Excel): `pip install openpyxl` - Required for `.xlsx` files
- `sqlalchemy` (for SQLite3): `pip install sqlalchemy` - For database connections
- `python-magic` or `filetype`: `pip install python-magic-bin` (or `filetype`) - For MIME type detection

**File Detection Strategy:**
1. Primary: Use file extension (`.csv`, `.xlsx`, `.json`, `.db`, `.sqlite`)
2. Fallback: Use `python-magic` or `filetype` library for MIME type detection
3. Validation: Attempt to read the file and catch exceptions

#### Step 2: Update ARX Adapter
- **File**: `src/anonymization_manager/adapters/arx/arx.py`
- **Changes**:
  - Modify `anonymize()` method to accept `pd.DataFrame` instead of file path
  - Create temporary CSV file from DataFrame before passing to ARX (since ARX expects file path)
  - Use `tempfile` module to create temporary files
  - Add cleanup logic after anonymization

**Key Changes:**
```python
# In ARXAnonymizer.anonymize():
1. Import file_loader utility
2. Load data using file_loader.load_data(config.data)
3. Create temporary CSV file using tempfile.NamedTemporaryFile()
4. Pass temp file path to ARX Data.create()
5. Clean up temp file after processing
```

**Third-Party Libraries:**
- `tempfile` (built-in Python module) - No installation needed

#### Step 3: Update ANJANA Adapter
- **File**: `src/anonymization_manager/adapters/anjana/anjana.py`
- **Changes**:
  - Replace `pd.read_csv(config.data)` with `file_loader.load_data(config.data)`
  - Remove the TODO comment about file type handling

**Key Changes:**
```python
# In AnjanaAnonymizer.anonymize():
1. Replace: data = pd.read_csv(config.data)
2. With: data = file_loader.load_data(config.data)
```

#### Step 4: Update Configuration Class
- **File**: `src/anonymization_manager/config.py`
- **Changes**:
  - Add optional `file_type` parameter to `AnonymizationConfig.__init__()`
  - Update docstring to reflect automatic detection capability
  - Add validation method for file existence

#### Step 5: Add Error Handling
- **Files**: Both adapter files
- **Changes**:
  - Add `FileNotFoundError` handling
  - Add format-specific exceptions (e.g., `xlrd.XLRDError` for Excel)
  - Provide clear error messages indicating supported formats

### Testing
- Create test files in each format (CSV, Excel, JSON, SQLite3)
- Test automatic detection
- Test manual file type specification
- Test error handling for unsupported formats

### Files to Create/Modify
1. **New**: `src/anonymization_manager/utils/__init__.py`
2. **New**: `src/anonymization_manager/utils/file_loader.py`
3. **Modify**: `src/anonymization_manager/adapters/arx/arx.py`
4. **Modify**: `src/anonymization_manager/adapters/anjana/anjana.py`
5. **Modify**: `src/anonymization_manager/config.py`

---

## 2. ANJANA Backend Improvements

### Objective
Implement missing quality metrics and add support for multiple sensitive attributes.

### Implementation Plan

#### Part A: Implement Missing Quality Metrics

**Metrics to Implement:**
1. `get_max_equivalence_class_size()`
2. `get_min_equivalence_class_size()`
3. `get_number_of_equivalence_classes()`
4. `get_average_class_size_metric()`
5. `get_granularity_metric(attribute: str)`
6. `get_ssesst_metric()` (partially implemented)
7. `get_record_level_squared_error_metric()`
8. `get_attribute_level_squared_error_metric(attribute: str)`
9. `get_non_uniform_entropy_metric(attribute: str)`
10. `get_generalization_intensity_metric(attribute: str)`
11. `get_ambiguity_metric()`

#### Step 1: Create Metrics Calculation Utility
- **New File**: `src/anonymization_manager/adapters/anjana/metrics.py`
- **Purpose**: Centralize all metric calculations

**Implementation Details:**

**Basic Equivalence Class Metrics:**
```python
def get_equivalence_classes(df, quasi_identifiers):
    """Group records by quasi-identifiers to form equivalence classes."""
    return df.groupby(quasi_identifiers)

def get_max_equivalence_class_size(df, quasi_identifiers):
    """Maximum size of any equivalence class."""
    eq_classes = get_equivalence_classes(df, quasi_identifiers)
    return int(eq_classes.size().max())

def get_min_equivalence_class_size(df, quasi_identifiers):
    """Minimum size of any equivalence class."""
    eq_classes = get_equivalence_classes(df, quasi_identifiers)
    return int(eq_classes.size().min())

def get_number_of_equivalence_classes(df, quasi_identifiers):
    """Total number of distinct equivalence classes."""
    eq_classes = get_equivalence_classes(df, quasi_identifiers)
    return len(eq_classes)
```

**Advanced Metrics:**
- **Granularity Metric**: Measure the level of generalization applied
- **SSESST Metric**: Sum of Squared Errors for Sensitive attributeS
- **Squared Error Metrics**: Calculate errors between original and anonymized values
- **Entropy Metrics**: Information-theoretic measures
- **Generalization Intensity**: Measure how much generalization was applied
- **Ambiguity Metric**: Measure ambiguity introduced by anonymization

**Third-Party Libraries:**
- `numpy`: `pip install numpy` - For numerical calculations
- `scipy`: `pip install scipy` - For statistical functions (entropy, distance metrics)
- `pandas` (already in use) - For data manipulation

**Reference Implementation:**
Use ARX's implementation in `arx.py` as a reference for metric formulas. Research academic papers on these metrics:
- Granularity: Measures generalization levels
- SSESST: Sum of squared errors for sensitive attributes
- Record/Attribute Level Squared Error: Distance metrics
- Non-uniform Entropy: Information theory based
- Generalization Intensity: Ratio of generalization levels
- Ambiguity: Measure of uncertainty introduced

#### Step 2: Update AnjanaResult Class
- **File**: `src/anonymization_manager/adapters/anjana/anjana.py`
- **Changes**:
  - Import metrics utility
  - Replace all `...` (ellipsis) with actual implementations
  - Store computed metrics in `__init__` for efficiency (optional optimization)

**Implementation Pattern:**
```python
def get_max_equivalence_class_size(self) -> int:
    """Returns the maximum size of an equivalence class."""
    return metrics.get_max_equivalence_class_size(
        self.result, self.quasi_identifiers
    )
```

#### Step 3: Fix Discernibility Metric
- **File**: `src/anonymization_manager/adapters/anjana/anjana.py`
- **Issue**: Line 110 uses `np.sum()` but `numpy` is not imported
- **Fix**: Add `import numpy as np` and complete the implementation

#### Part B: Multiple Sensitive Attributes Support

#### Step 1: Update AnjanaAnonymizer.anonymize()
- **File**: `src/anonymization_manager/adapters/anjana/anjana.py`
- **Changes**:
  - Remove the limitation: `sens_att = config.sensitive_attributes[0]`
  - Loop through all sensitive attributes when applying l-diversity and t-closeness
  - Ensure ANJANA library supports multiple sensitive attributes (verify library capabilities)

**Implementation:**
```python
# Instead of:
sens_att = config.sensitive_attributes[0]

# Use:
for sens_att in config.sensitive_attributes:
    # Apply l-diversity for each sensitive attribute
    if l is not None:
        data = l_diversity(..., sens_att, ...)
    # Apply t-closeness for each sensitive attribute
    if t is not None:
        data = t_closeness(..., sens_att, ...)
```

**Note**: Verify ANJANA library's capabilities. If it doesn't support multiple sensitive attributes, consider:
1. Applying models sequentially for each sensitive attribute
2. Contacting ANJANA maintainers for multi-attribute support
3. Implementing a workaround that combines multiple sensitive attributes

#### Step 2: Update Error Messages
- **File**: `src/anonymization_manager/adapters/anjana/anjana.py`
- **Changes**: Remove or update comments/TODOs about single sensitive attribute limitation

### Testing
- Create test datasets with multiple sensitive attributes
- Verify all metrics match ARX results (when applicable)
- Test edge cases (empty datasets, single equivalence class, etc.)

### Files to Create/Modify
1. **New**: `src/anonymization_manager/adapters/anjana/metrics.py`
2. **Modify**: `src/anonymization_manager/adapters/anjana/anjana.py`

---

## 3. Configuration Enhancements

### Objective
Add configuration validation, default hierarchies for common attributes, and programmatic hierarchy generation.

### Implementation Plan

#### Part A: Configuration Validation

#### Step 1: Create Validation Module
- **New File**: `src/anonymization_manager/utils/validation.py`
- **Purpose**: Validate configuration parameters

**Validation Functions:**
```python
def validate_config(config: AnonymizationConfig) -> list[str]:
    """Returns list of validation errors (empty if valid)."""
    
    errors = []
    
    # Validate file exists
    if not os.path.exists(config.data):
        errors.append(f"Data file not found: {config.data}")
    
    # Validate attribute lists are not empty
    if not config.quasi_identifiers:
        errors.append("At least one quasi-identifier is required")
    
    # Validate k, l, t values
    if config.k is not None and config.k < 1:
        errors.append("k must be >= 1")
    
    if config.l is not None and config.l < 1:
        errors.append("l must be >= 1")
    
    if config.t is not None and (config.t < 0 or config.t > 1):
        errors.append("t must be between 0 and 1")
    
    # Validate suppression_limit
    if config.suppression_limit is not None:
        if config.suppression_limit < 0 or config.suppression_limit > 100:
            errors.append("suppression_limit must be between 0 and 100")
    
    # Validate backend
    if config.backend not in [None, "arx", "anjana"]:
        errors.append(f"Invalid backend: {config.backend}")
    
    # Validate hierarchy files exist
    for attr, hierarchy_path in config.hierarchies.items():
        if not os.path.exists(hierarchy_path):
            errors.append(f"Hierarchy file not found: {hierarchy_path}")
        if attr not in config.quasi_identifiers:
            errors.append(f"Hierarchy defined for non-quasi-identifier: {attr}")
    
    # Validate attribute names don't overlap
    all_attrs = (config.identifiers + config.quasi_identifiers + 
                 config.sensitive_attributes + config.insensitive_attributes)
    if len(all_attrs) != len(set(all_attrs)):
        errors.append("Attribute names must be unique across all categories")
    
    return errors

def validate_hierarchy_file(hierarchy_path: str, attribute: str) -> list[str]:
    """Validates hierarchy file format."""
    errors = []
    # Check file format, required columns, etc.
    return errors
```

#### Step 2: Update AnonymizationConfig
- **File**: `src/anonymization_manager/config.py`
- **Changes**:
  - Add `validate()` method to `AnonymizationConfig` class
  - Raise `ValueError` or custom `ConfigurationError` with validation messages
  - Optionally add `validate=False` parameter to `__init__` to allow deferred validation

**Implementation:**
```python
@dataclass
class AnonymizationConfig:
    # ... existing fields ...
    
    def validate(self) -> None:
        """Validates the configuration and raises ValueError if invalid."""
        from anonymization_manager.utils.validation import validate_config
        errors = validate_config(self)
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
```

#### Step 3: Update AnonymizationManager
- **File**: `src/anonymization_manager/core.py`
- **Changes**: Call `config.validate()` before anonymization

**Implementation:**
```python
@staticmethod
def anonymize(config: AnonymizationConfig) -> AnonymizedData:
    config.validate()  # Validate before processing
    # ... rest of the method
```

#### Part B: Default Hierarchies

#### Step 1: Create Hierarchy Templates Module
- **New File**: `src/anonymization_manager/utils/hierarchy_templates.py`
- **Purpose**: Provide default hierarchies for common attributes

**Common Attributes:**
- Age (numeric ranges)
- ZIP Code (geographic levels)
- Date (temporal hierarchies)
- Income (numeric ranges)
- Education Level (ordinal)

**Third-Party Libraries:**
- `pandas` (already in use) - For creating hierarchy DataFrames
- `numpy` - For numeric range generation

**Implementation:**
```python
def generate_age_hierarchy(min_age: int = 0, max_age: int = 100) -> pd.DataFrame:
    """Generates a default age hierarchy."""
    # Create age ranges: specific -> decade -> half-century -> *
    pass

def generate_zip_hierarchy() -> pd.DataFrame:
    """Generates a default ZIP code hierarchy."""
    # US ZIP codes: 5-digit -> 3-digit -> state -> *
    pass

def get_default_hierarchy(attribute: str, **kwargs) -> pd.DataFrame:
    """Returns default hierarchy for common attribute types."""
    templates = {
        "age": generate_age_hierarchy,
        "zip": generate_zip_hierarchy,
        # ... more templates
    }
    # ...
```

#### Step 2: Update Configuration
- **File**: `src/anonymization_manager/config.py`
- **Changes**:
  - Add `use_default_hierarchy(attribute: str)` method
  - Modify `__init__` to accept `auto_generate_hierarchies: bool = False`

**Implementation:**
```python
def use_default_hierarchy(self, attribute: str) -> None:
    """Uses default hierarchy for specified attribute if not provided."""
    from anonymization_manager.utils.hierarchy_templates import get_default_hierarchy
    if attribute not in self.hierarchies:
        hierarchy_df = get_default_hierarchy(attribute)
        # Save to temp file or use in-memory representation
        self.hierarchies[attribute] = hierarchy_df  # or temp file path
```

#### Part C: Programmatic Hierarchy Generation

#### Step 1: Create Hierarchy Generator
- **New File**: `src/anonymization_manager/utils/hierarchy_generator.py`
- **Purpose**: Generate hierarchies programmatically

**Generation Functions:**
```python
def generate_numeric_hierarchy(
    min_value: float,
    max_value: float,
    levels: int = 3,
    method: str = "equal_width"
) -> pd.DataFrame:
    """Generates hierarchy for numeric attributes."""
    # Methods: equal_width, equal_frequency, custom
    pass

def generate_categorical_hierarchy(
    categories: list[str],
    levels: int = 2
) -> pd.DataFrame:
    """Generates hierarchy for categorical attributes."""
    # Group categories into broader categories
    pass

def generate_temporal_hierarchy(
    start_date: datetime,
    end_date: datetime,
    granularity: str = "day"
) -> pd.DataFrame:
    """Generates hierarchy for date/timestamp attributes."""
    # Levels: day -> week -> month -> year -> *
    pass
```

**Third-Party Libraries:**
- `pandas` - For DataFrame creation
- `numpy` - For numeric operations
- `dateutil` - `pip install python-dateutil` - For date handling

#### Step 2: Integrate with Configuration
- **File**: `src/anonymization_manager/config.py`
- **Changes**: Add methods to generate hierarchies on-the-fly

### Testing
- Test validation with invalid configurations
- Test default hierarchies for common attributes
- Test programmatic hierarchy generation
- Verify generated hierarchies work with anonymization

### Files to Create/Modify
1. **New**: `src/anonymization_manager/utils/validation.py`
2. **New**: `src/anonymization_manager/utils/hierarchy_templates.py`
3. **New**: `src/anonymization_manager/utils/hierarchy_generator.py`
4. **Modify**: `src/anonymization_manager/config.py`
5. **Modify**: `src/anonymization_manager/core.py`

---

## 4. Performance Optimization

### Objective
Add caching mechanisms, parallel processing for large datasets, and optimize memory usage.

### Implementation Plan

#### Part A: Caching Mechanisms

#### Step 1: Create Cache Module
- **New File**: `src/anonymization_manager/utils/cache.py`
- **Purpose**: Implement caching for expensive operations

**Cache Targets:**
- Loaded datasets (file loading)
- Hierarchy files (parsed hierarchies)
- Configuration validation results
- Computed metrics (for repeated access)

**Third-Party Libraries:**
- `functools.lru_cache` (built-in) - For function-level caching
- `diskcache`: `pip install diskcache` - For persistent disk-based caching
- `joblib`: `pip install joblib` - For caching with serialization

**Implementation:**
```python
from functools import lru_cache
import hashlib
import diskcache

class AnonymizationCache:
    """Cache manager for anonymization operations."""
    
    def __init__(self, cache_dir: str = ".anonymization_cache"):
        self.cache = diskcache.Cache(cache_dir)
    
    def get_cache_key(self, config: AnonymizationConfig) -> str:
        """Generate cache key from configuration."""
        # Hash config parameters
        key_data = f"{config.data}_{config.k}_{config.l}_{config.t}_{config.backend}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_result(self, config: AnonymizationConfig) -> AnonymizedData | None:
        """Retrieve cached anonymization result."""
        key = self.get_cache_key(config)
        return self.cache.get(key)
    
    def cache_result(self, config: AnonymizationConfig, result: AnonymizedData) -> None:
        """Store anonymization result in cache."""
        key = self.get_cache_key(config)
        self.cache.set(key, result)
```

#### Step 2: Integrate Caching
- **File**: `src/anonymization_manager/core.py`
- **Changes**: Add optional caching to `AnonymizationManager.anonymize()`

**Implementation:**
```python
@staticmethod
def anonymize(config: AnonymizationConfig, use_cache: bool = False) -> AnonymizedData:
    if use_cache:
        from anonymization_manager.utils.cache import AnonymizationCache
        cache = AnonymizationCache()
        cached_result = cache.get_cached_result(config)
        if cached_result:
            return cached_result
    
    # Perform anonymization
    result = ...
    
    if use_cache:
        cache.cache_result(config, result)
    
    return result
```

#### Part B: Parallel Processing

#### Step 1: Identify Parallelization Opportunities
- Large dataset chunking
- Multiple sensitive attribute processing
- Metric calculations
- Batch processing multiple configurations

**Third-Party Libraries:**
- `multiprocessing`: `pip install multiprocessing` (built-in) - For process-based parallelism
- `concurrent.futures`: Built-in - High-level parallel execution
- `joblib`: `pip install joblib` - For parallel loops with shared memory
- `dask`: `pip install dask[dataframe]` - For out-of-core and parallel processing

#### Step 2: Implement Parallel Metric Calculation
- **File**: `src/anonymization_manager/adapters/anjana/metrics.py` (to be created)
- **Changes**: Use `joblib.Parallel` for independent metric calculations

**Implementation:**
```python
from joblib import Parallel, delayed

def compute_all_metrics_parallel(df, quasi_identifiers, sensitive_attributes):
    """Compute all metrics in parallel."""
    metrics = Parallel(n_jobs=-1)(
        delayed(get_max_equivalence_class_size)(df, quasi_identifiers),
        delayed(get_min_equivalence_class_size)(df, quasi_identifiers),
        # ... more metrics
    )
    return metrics
```

#### Step 3: Implement Dataset Chunking
- **New File**: `src/anonymization_manager/utils/parallel.py`
- **Purpose**: Handle large datasets by processing in chunks

**Implementation:**
```python
def anonymize_chunks(
    config: AnonymizationConfig,
    chunk_size: int = 10000
) -> pd.DataFrame:
    """Anonymize large dataset in chunks."""
    # Load data in chunks
    # Anonymize each chunk
    # Combine results (careful with k-anonymity across chunks)
    pass
```

**Note**: Chunking requires careful handling of k-anonymity, as equivalence classes may span chunks. Consider:
1. Pre-processing to identify chunk boundaries that preserve equivalence classes
2. Post-processing to merge chunks and verify k-anonymity
3. Using sliding windows instead of fixed chunks

#### Part C: Memory Optimization

#### Step 1: Optimize Data Loading
- **File**: `src/anonymization_manager/utils/file_loader.py` (to be created)
- **Changes**:
  - Use `chunksize` parameter in `pd.read_csv()` for large files
  - Implement streaming data processing
  - Use appropriate dtypes to reduce memory footprint

**Implementation:**
```python
def load_data_optimized(file_path: str, optimize_dtypes: bool = True) -> pd.DataFrame:
    """Load data with memory optimization."""
    df = pd.read_csv(file_path)
    
    if optimize_dtypes:
        # Convert numeric columns to appropriate dtypes
        for col in df.select_dtypes(include=['int64']):
            df[col] = pd.to_numeric(df[col], downcast='integer')
        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')
    
    return df
```

#### Step 2: Implement Memory-Efficient Processing
- **Files**: Both adapter files
- **Changes**:
  - Delete intermediate DataFrames when no longer needed
  - Use `del` statements and `gc.collect()` for explicit memory management
  - Process data in-place where possible

**Third-Party Libraries:**
- `gc` (built-in) - Garbage collection
- `psutil`: `pip install psutil` - For memory monitoring (optional)

### Testing
- Test caching with identical configurations
- Test parallel processing with large datasets
- Measure memory usage before and after optimizations
- Benchmark performance improvements

### Files to Create/Modify
1. **New**: `src/anonymization_manager/utils/cache.py`
2. **New**: `src/anonymization_manager/utils/parallel.py`
3. **Modify**: `src/anonymization_manager/core.py`
4. **Modify**: `src/anonymization_manager/utils/file_loader.py` (to be created)
5. **Modify**: `src/anonymization_manager/adapters/anjana/metrics.py` (to be created)

---

## 5. Additional Privacy Models

### Objective
Implement differential privacy, (α, k)-anonymity, m-invariance, and δ-presence privacy models.

### Implementation Plan

#### Research Phase
Each privacy model requires:
1. Understanding the mathematical definition
2. Identifying available libraries or algorithms
3. Determining integration approach with existing adapters

#### Part A: Differential Privacy

**Third-Party Libraries:**
- `diffprivlib`: `pip install diffprivlib` - IBM's differential privacy library
- `opendp`: `pip install opendp` - Open Differential Privacy library
- `pydp`: `pip install python-dp` - Google's differential privacy library

**Implementation:**
- **New File**: `src/anonymization_manager/adapters/differential_privacy/dp.py`
- **Purpose**: Implement differential privacy adapter

**Key Considerations:**
- Differential privacy uses noise addition (Laplace, Gaussian mechanisms)
- Requires epsilon (privacy budget) parameter
- Different from k-anonymity approach (global vs local privacy)

**Integration:**
- Add `epsilon: float` parameter to `AnonymizationConfig`
- Create `DifferentialPrivacyAnonymizer` class following adapter pattern
- Implement as separate adapter or extend existing adapters

#### Part B: (α, k)-Anonymity

**Implementation:**
- **Research**: Academic papers on (α, k)-anonymity
- **Algorithm**: Extend k-anonymity with alpha parameter (confidence level)
- **New File**: `src/anonymization_manager/adapters/alpha_k/alpha_k.py`

**Key Considerations:**
- Combines k-anonymity with probabilistic privacy guarantees
- Requires alpha parameter (0 ≤ α ≤ 1)
- May need custom implementation if no library exists

#### Part C: m-Invariance

**Implementation:**
- **Research**: Academic papers on m-invariance
- **Algorithm**: Ensures each equivalence class has at least m distinct sensitive values across updates
- **New File**: `src/anonymization_manager/adapters/m_invariance/m_inv.py`

**Key Considerations:**
- Designed for dynamic datasets (multiple releases)
- Requires tracking history of releases
- More complex than static anonymization

#### Part D: δ-Presence

**Implementation:**
- **Research**: Academic papers on δ-presence
- **Algorithm**: Ensures probability of presence/absence in dataset is bounded
- **New File**: `src/anonymization_manager/adapters/delta_presence/delta_presence.py`

**Key Considerations:**
- Requires delta parameter (0 ≤ δ ≤ 1)
- May need custom implementation

#### Integration Strategy

#### Step 1: Extend Configuration
- **File**: `src/anonymization_manager/config.py`
- **Changes**:
  - Add optional parameters: `epsilon`, `alpha`, `m`, `delta`
  - Update `from_json()` to support new parameters
  - Add validation for new parameters

#### Step 2: Update AnonymizationManager
- **File**: `src/anonymization_manager/core.py`
- **Changes**:
  - Add backend options: `"differential_privacy"`, `"alpha_k"`, etc.
  - Route to appropriate adapter based on privacy model

#### Step 3: Create Adapter Interface
- **New File**: `src/anonymization_manager/adapters/base.py`
- **Purpose**: Define common interface for all adapters

**Implementation:**
```python
from abc import ABC, abstractmethod

class AnonymizerAdapter(ABC):
    """Base class for all anonymization adapters."""
    
    @staticmethod
    @abstractmethod
    def anonymize(config: AnonymizationConfig) -> AnonymizedData:
        """Perform anonymization using this adapter."""
        pass
    
    @staticmethod
    @abstractmethod
    def supports_privacy_model(model: str) -> bool:
        """Check if adapter supports given privacy model."""
        pass
```

#### Step 4: Implement Each Privacy Model
- Create separate adapter for each privacy model
- Follow the adapter pattern established by ARX and ANJANA
- Ensure result objects implement the same interface

### Testing
- Test each privacy model with sample datasets
- Verify privacy guarantees (may require formal verification)
- Compare utility vs privacy tradeoffs
- Test parameter validation

### Files to Create/Modify
1. **New**: `src/anonymization_manager/adapters/base.py`
2. **New**: `src/anonymization_manager/adapters/differential_privacy/dp.py`
3. **New**: `src/anonymization_manager/adapters/alpha_k/alpha_k.py`
4. **New**: `src/anonymization_manager/adapters/m_invariance/m_inv.py`
5. **New**: `src/anonymization_manager/adapters/delta_presence/delta_presence.py`
6. **Modify**: `src/anonymization_manager/config.py`
7. **Modify**: `src/anonymization_manager/core.py`

---

## 6. Enhanced Analysis

### Objective
Add risk assessment metrics, privacy-utility tradeoff visualization, comparison tools, and statistical analysis.

### Implementation Plan

#### Part A: Risk Assessment Metrics

#### Step 1: Create Risk Assessment Module
- **New File**: `src/anonymization_manager/analysis/risk_assessment.py`
- **Purpose**: Calculate privacy risk metrics

**Risk Metrics:**
- Re-identification risk
- Attribute disclosure risk
- Record linkage risk
- Homogeneity risk

**Third-Party Libraries:**
- `scipy`: `pip install scipy` - For statistical calculations
- `numpy` - For numerical operations
- `pandas` - For data manipulation

**Implementation:**
```python
def calculate_reidentification_risk(
    anonymized_df: pd.DataFrame,
    quasi_identifiers: list[str],
    external_data: pd.DataFrame | None = None
) -> float:
    """Calculate re-identification risk."""
    # Analyze uniqueness of quasi-identifier combinations
    # Compare with external data if provided
    pass

def calculate_attribute_disclosure_risk(
    anonymized_df: pd.DataFrame,
    sensitive_attributes: list[str],
    quasi_identifiers: list[str]
) -> float:
    """Calculate risk of sensitive attribute disclosure."""
    # Analyze l-diversity and t-closeness violations
    pass
```

#### Step 2: Extend AnonymizedData
- **File**: `src/anonymization_manager/core.py`
- **Changes**: Add risk assessment methods to `AnonymizedData` wrapper

**Implementation:**
```python
def get_reidentification_risk(self) -> float:
    """Get re-identification risk score."""
    from anonymization_manager.analysis.risk_assessment import calculate_reidentification_risk
    return calculate_reidentification_risk(
        self.get_anonymized_data_as_dataframe(),
        self.config.quasi_identifiers
    )
```

#### Part B: Privacy-Utility Tradeoff Visualization

#### Step 1: Create Visualization Module
- **New File**: `src/anonymization_manager/analysis/visualization.py`
- **Purpose**: Generate plots and visualizations

**Visualizations:**
- Privacy-utility tradeoff curves
- Metric comparisons
- Equivalence class distributions
- Generalization level visualizations

**Third-Party Libraries:**
- `matplotlib`: `pip install matplotlib` - For plotting
- `seaborn`: `pip install seaborn` - For statistical visualizations
- `plotly`: `pip install plotly` - For interactive plots (optional)

**Implementation:**
```python
def plot_privacy_utility_tradeoff(
    k_values: list[int],
    utility_scores: list[float],
    privacy_scores: list[float]
) -> None:
    """Plot privacy-utility tradeoff curve."""
    import matplotlib.pyplot as plt
    # Create scatter plot or line plot
    pass

def visualize_equivalence_classes(
    anonymized_df: pd.DataFrame,
    quasi_identifiers: list[str]
) -> None:
    """Visualize equivalence class distribution."""
    # Create bar chart or histogram
    pass
```

#### Step 2: Add Visualization Methods
- **File**: `src/anonymization_manager/core.py`
- **Changes**: Add visualization methods to `AnonymizedData`

#### Part C: Comparison Tools

#### Step 1: Create Comparison Module
- **New File**: `src/anonymization_manager/analysis/comparison.py`
- **Purpose**: Compare different anonymization results

**Comparison Functions:**
- Compare two anonymization results
- Compare multiple configurations
- Generate comparison reports

**Implementation:**
```python
class AnonymizationComparison:
    """Compare multiple anonymization results."""
    
    def __init__(self, results: list[AnonymizedData]):
        self.results = results
    
    def compare_metrics(self) -> pd.DataFrame:
        """Compare metrics across results."""
        # Create DataFrame with metrics for each result
        pass
    
    def compare_utility(self) -> dict:
        """Compare utility metrics."""
        pass
    
    def generate_report(self, output_path: str) -> None:
        """Generate comparison report."""
        # Create markdown or HTML report
        pass
```

#### Part D: Statistical Analysis

#### Step 1: Create Statistical Analysis Module
- **New File**: `src/anonymization_manager/analysis/statistics.py`
- **Purpose**: Perform statistical analysis on anonymized data

**Analysis Functions:**
- Descriptive statistics
- Distribution comparisons (original vs anonymized)
- Correlation analysis
- Hypothesis testing capabilities

**Third-Party Libraries:**
- `scipy.stats`: For statistical tests
- `scikit-learn`: `pip install scikit-learn` - For machine learning metrics
- `pandas` - For statistical functions

**Implementation:**
```python
def compare_distributions(
    original_df: pd.DataFrame,
    anonymized_df: pd.DataFrame,
    attribute: str
) -> dict:
    """Compare distributions of attribute in original vs anonymized data."""
    from scipy.stats import ks_2samp, chi2_contingency
    # Perform Kolmogorov-Smirnov test, chi-square test, etc.
    pass

def calculate_utility_metrics(
    original_df: pd.DataFrame,
    anonymized_df: pd.DataFrame
) -> dict:
    """Calculate utility preservation metrics."""
    # Mean absolute error, correlation, etc.
    pass
```

### Testing
- Test risk assessment with known datasets
- Verify visualization outputs
- Test comparison tools with multiple results
- Validate statistical analysis accuracy

### Files to Create/Modify
1. **New**: `src/anonymization_manager/analysis/__init__.py`
2. **New**: `src/anonymization_manager/analysis/risk_assessment.py`
3. **New**: `src/anonymization_manager/analysis/visualization.py`
4. **New**: `src/anonymization_manager/analysis/comparison.py`
5. **New**: `src/anonymization_manager/analysis/statistics.py`
6. **Modify**: `src/anonymization_manager/core.py`

---

## 7. API Improvements

### Objective
Add REST API wrapper, batch processing capabilities, progress tracking, and result comparison utilities.

### Implementation Plan

#### Part A: REST API Wrapper

#### Step 1: Choose Framework
**Recommended**: FastAPI (modern, fast, automatic documentation)

**Third-Party Libraries:**
- `fastapi`: `pip install fastapi` - Web framework
- `uvicorn`: `pip install uvicorn` - ASGI server
- `pydantic`: Usually included with FastAPI - Data validation

#### Step 2: Create API Module
- **New File**: `src/anonymization_manager/api/__init__.py`
- **New File**: `src/anonymization_manager/api/main.py`
- **Purpose**: REST API endpoints

**API Endpoints:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class AnonymizationRequest(BaseModel):
    data: str
    identifiers: list[str]
    quasi_identifiers: list[str]
    # ... other config fields

@app.post("/anonymize")
async def anonymize(request: AnonymizationRequest):
    """Anonymize dataset via REST API."""
    config = AnonymizationConfig(**request.dict())
    result = AnonymizationManager.anonymize(config)
    return {
        "anonymized_data": result.get_anonymized_data_as_dataframe().to_dict(),
        "metrics": {...}
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

#### Step 3: Add Authentication (Optional)
- Use FastAPI security features
- Implement API key authentication
- Add rate limiting

**Third-Party Libraries:**
- `python-jose`: `pip install python-jose[cryptography]` - JWT tokens
- `passlib`: `pip install passlib[bcrypt]` - Password hashing

#### Part B: Batch Processing

#### Step 1: Create Batch Processing Module
- **New File**: `src/anonymization_manager/utils/batch.py`
- **Purpose**: Process multiple configurations

**Implementation:**
```python
def anonymize_batch(
    configs: list[AnonymizationConfig],
    parallel: bool = False,
    max_workers: int = 4
) -> list[AnonymizedData]:
    """Anonymize multiple configurations."""
    if parallel:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(AnonymizationManager.anonymize, configs))
    else:
        results = [AnonymizationManager.anonymize(config) for config in configs]
    return results
```

#### Step 2: Add API Endpoint
- **File**: `src/anonymization_manager/api/main.py`
- **Changes**: Add `/anonymize/batch` endpoint

#### Part C: Progress Tracking

#### Step 1: Implement Progress Callbacks
- **File**: `src/anonymization_manager/core.py`
- **Changes**: Add progress callback support

**Implementation:**
```python
from typing import Callable

@staticmethod
def anonymize(
    config: AnonymizationConfig,
    progress_callback: Callable[[int, int], None] | None = None
) -> AnonymizedData:
    """Anonymize with optional progress tracking."""
    if progress_callback:
        progress_callback(0, 100)  # Start
    
    # During anonymization, call:
    # progress_callback(current_step, total_steps)
    
    if progress_callback:
        progress_callback(100, 100)  # Complete
```

#### Step 2: Add WebSocket Support for Real-time Progress
- **File**: `src/anonymization_manager/api/main.py`
- **Changes**: Add WebSocket endpoint for progress updates

**Third-Party Libraries:**
- `websockets`: `pip install websockets` - WebSocket support (FastAPI includes this)

#### Part D: Result Comparison Utilities

#### Step 1: Extend Comparison Module
- **File**: `src/anonymization_manager/analysis/comparison.py` (from Enhancement 6)
- **Changes**: Add utility functions for common comparisons

#### Step 2: Add API Endpoint
- **File**: `src/anonymization_manager/api/main.py`
- **Changes**: Add `/compare` endpoint

### Testing
- Test REST API endpoints
- Test batch processing
- Verify progress tracking
- Test authentication (if implemented)

### Files to Create/Modify
1. **New**: `src/anonymization_manager/api/__init__.py`
2. **New**: `src/anonymization_manager/api/main.py`
3. **New**: `src/anonymization_manager/utils/batch.py`
4. **Modify**: `src/anonymization_manager/core.py`
5. **Modify**: `src/anonymization_manager/analysis/comparison.py` (from Enhancement 6)

---

## 8. Documentation and Examples

### Objective
Create comprehensive usage examples, best practices guide, performance benchmarks, and case studies.

### Implementation Plan

#### Part A: Usage Examples

#### Step 1: Create Examples Directory
- **New Directory**: `examples/`
- **Files to Create**:
  - `examples/basic_usage.py`
  - `examples/advanced_usage.py`
  - `examples/multi_backend_comparison.py`
  - `examples/custom_hierarchies.py`
  - `examples/risk_assessment_example.py`

#### Step 2: Create Jupyter Notebooks
- **New Directory**: `examples/notebooks/`
- **Files**:
  - `examples/notebooks/tutorial.ipynb`
  - `examples/notebooks/privacy_models_comparison.ipynb`
  - `examples/notebooks/visualization_examples.ipynb`

**Third-Party Libraries:**
- `jupyter`: `pip install jupyter` - For notebooks
- `ipykernel`: `pip install ipykernel` - Kernel for notebooks

#### Part B: Best Practices Guide

#### Step 1: Create Documentation
- **New File**: `docs/BEST_PRACTICES.md`
- **Content**:
  - Choosing appropriate k values
  - Hierarchy design guidelines
  - Backend selection criteria
  - Privacy-utility balancing
  - Common pitfalls and solutions

#### Part C: Performance Benchmarks

#### Step 1: Create Benchmark Suite
- **New File**: `benchmarks/benchmark_suite.py`
- **Purpose**: Automated performance testing

**Third-Party Libraries:**
- `pytest`: `pip install pytest` - Testing framework
- `pytest-benchmark`: `pip install pytest-benchmark` - Benchmarking plugin
- `memory_profiler`: `pip install memory-profiler` - Memory profiling

**Implementation:**
```python
import pytest
from anonymization_manager import AnonymizationManager, AnonymizationConfig

@pytest.mark.benchmark
def test_arx_performance(benchmark):
    config = AnonymizationConfig(...)
    result = benchmark(AnonymizationManager.anonymize, config)
```

#### Step 2: Generate Benchmark Reports
- **New File**: `benchmarks/generate_report.py`
- **Purpose**: Generate HTML/PDF reports from benchmarks

#### Part D: Case Studies

#### Step 1: Create Case Studies
- **New Directory**: `case_studies/`
- **Files**:
  - `case_studies/medical_data.md`
  - `case_studies/census_data.md`
  - `case_studies/financial_data.md`

Each case study should include:
- Dataset description
- Configuration choices
- Results and analysis
- Lessons learned

### Testing
- Ensure all examples run successfully
- Verify documentation accuracy
- Run benchmarks regularly
- Update case studies with real results

### Files to Create
1. **New**: `examples/basic_usage.py`
2. **New**: `examples/advanced_usage.py`
3. **New**: `examples/notebooks/tutorial.ipynb`
4. **New**: `docs/BEST_PRACTICES.md`
5. **New**: `benchmarks/benchmark_suite.py`
6. **New**: `case_studies/medical_data.md`

---

## 9. Testing and Validation

### Objective
Implement unit tests, integration tests, validation against benchmarks, and privacy guarantee verification.

### Implementation Plan

#### Part A: Unit Tests

#### Step 1: Set Up Testing Framework
- **New Directory**: `tests/`
- **Structure**:
  ```
  tests/
  ├── __init__.py
  ├── unit/
  │   ├── test_config.py
  │   ├── test_core.py
  │   ├── test_arx_adapter.py
  │   └── test_anjana_adapter.py
  ├── integration/
  │   ├── test_end_to_end.py
  │   └── test_multi_backend.py
  └── fixtures/
      └── sample_data.py
  ```

**Third-Party Libraries:**
- `pytest`: `pip install pytest` - Testing framework
- `pytest-cov`: `pip install pytest-cov` - Coverage reporting
- `pytest-mock`: `pip install pytest-mock` - Mocking
- `hypothesis`: `pip install hypothesis` - Property-based testing

#### Step 2: Write Unit Tests
- **File**: `tests/unit/test_config.py`
- **Test**: Configuration validation, JSON loading, parameter validation

- **File**: `tests/unit/test_core.py`
- **Test**: AnonymizationManager routing, AnonymizedData wrapper

- **File**: `tests/unit/test_arx_adapter.py`
- **Test**: ARX adapter methods, error handling

- **File**: `tests/unit/test_anjana_adapter.py`
- **Test**: ANJANA adapter methods, metric calculations

#### Part B: Integration Tests

#### Step 1: Create Integration Test Suite
- **File**: `tests/integration/test_end_to_end.py`
- **Test**: Complete anonymization workflows

**Implementation:**
```python
def test_end_to_end_k_anonymity():
    """Test complete k-anonymity workflow."""
    config = AnonymizationConfig(...)
    result = AnonymizationManager.anonymize(config)
    assert result.get_number_of_suppressed_records() >= 0
    assert len(result.get_anonymized_data_as_dataframe()) <= len(original_data)
```

#### Step 2: Test Multi-Backend Compatibility
- **File**: `tests/integration/test_multi_backend.py`
- **Test**: Compare ARX and ANJANA results for consistency

#### Part C: Validation Against Benchmarks

#### Step 1: Create Benchmark Datasets
- **New Directory**: `tests/benchmarks/`
- **Files**: Standard anonymization benchmark datasets
- **Sources**: Use publicly available anonymization benchmarks

#### Step 2: Implement Validation Tests
- **File**: `tests/validation/test_benchmarks.py`
- **Test**: Verify results match expected outputs from benchmarks

#### Part D: Privacy Guarantee Verification

#### Step 1: Create Verification Module
- **New File**: `tests/validation/privacy_verification.py`
- **Purpose**: Verify privacy guarantees are met

**Implementation:**
```python
def verify_k_anonymity(
    anonymized_df: pd.DataFrame,
    quasi_identifiers: list[str],
    k: int
) -> bool:
    """Verify k-anonymity guarantee."""
    eq_classes = anonymized_df.groupby(quasi_identifiers).size()
    return (eq_classes >= k).all()

def verify_l_diversity(
    anonymized_df: pd.DataFrame,
    quasi_identifiers: list[str],
    sensitive_attribute: str,
    l: int
) -> bool:
    """Verify l-diversity guarantee."""
    # Check each equivalence class has at least l distinct values
    pass
```

#### Step 2: Add Verification Tests
- **File**: `tests/validation/test_privacy_guarantees.py`
- **Test**: Verify all privacy models meet their guarantees

### Testing Infrastructure

#### Step 1: Create Test Configuration
- **New File**: `pytest.ini` or `pyproject.toml` section
- **Configuration**: Test discovery, coverage settings

#### Step 2: Set Up CI/CD
- **New File**: `.github/workflows/tests.yml` (if using GitHub)
- **Purpose**: Automated testing on commits

### Files to Create
1. **New**: `tests/__init__.py`
2. **New**: `tests/unit/test_config.py`
3. **New**: `tests/unit/test_core.py`
4. **New**: `tests/unit/test_arx_adapter.py`
5. **New**: `tests/unit/test_anjana_adapter.py`
6. **New**: `tests/integration/test_end_to_end.py`
7. **New**: `tests/validation/privacy_verification.py`
8. **New**: `pytest.ini`

---

## 10. User Experience

### Objective
Create CLI interface, configuration wizard, interactive result visualization, and template library.

### Implementation Plan

#### Part A: CLI Interface

#### Step 1: Choose CLI Framework
**Recommended**: Click or Typer (modern, type-hint friendly)

**Third-Party Libraries:**
- `typer`: `pip install typer[all]` - Modern CLI framework
- `rich`: Usually included with typer - Beautiful terminal output

#### Step 2: Create CLI Module
- **New File**: `src/anonymization_manager/cli/__init__.py`
- **New File**: `src/anonymization_manager/cli/main.py`
- **Purpose**: Command-line interface

**Implementation:**
```python
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def anonymize(
    config_file: str = typer.Option(..., "--config", "-c", help="Configuration file path"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
    backend: str = typer.Option("arx", "--backend", "-b", help="Backend to use"),
):
    """Anonymize a dataset."""
    config = AnonymizationConfig.from_json(config_file)
    config.backend = backend
    result = AnonymizationManager.anonymize(config)
    result.store_as_csv(output)
    console.print(f"[green]Anonymization complete![/green]")

@app.command()
def validate(
    config_file: str = typer.Option(..., "--config", "-c"),
):
    """Validate a configuration file."""
    try:
        config = AnonymizationConfig.from_json(config_file)
        config.validate()
        console.print("[green]Configuration is valid![/green]")
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
```

#### Step 3: Add Entry Point
- **File**: `pyproject.toml`
- **Changes**: Add CLI entry point

```toml
[project.scripts]
anonymize = "anonymization_manager.cli.main:app"
```

#### Part B: Configuration Wizard

#### Step 1: Create Interactive Wizard
- **New File**: `src/anonymization_manager/cli/wizard.py`
- **Purpose**: Interactive configuration creation

**Third-Party Libraries:**
- `inquirer`: `pip install inquirer` - Interactive prompts
- `rich` - For formatted output

**Implementation:**
```python
import inquirer

def create_config_interactive() -> AnonymizationConfig:
    """Interactive configuration wizard."""
    questions = [
        inquirer.Text("data", message="Path to dataset"),
        inquirer.Checkbox("identifiers", message="Select identifiers"),
        # ... more questions
    ]
    answers = inquirer.prompt(questions)
    # Create and return config
```

#### Step 2: Add CLI Command
- **File**: `src/anonymization_manager/cli/main.py`
- **Changes**: Add `wizard` command

#### Part C: Interactive Result Visualization

#### Step 1: Create Interactive Dashboard
- **New File**: `src/anonymization_manager/cli/visualize.py`
- **Purpose**: Interactive terminal-based visualization

**Third-Party Libraries:**
- `rich` - For terminal tables and charts
- `plotly`: `pip install plotly` - For interactive plots (if web-based)

**Implementation:**
```python
from rich.table import Table
from rich.console import Console

def display_results_interactive(result: AnonymizedData):
    """Display anonymization results interactively."""
    console = Console()
    
    # Create metrics table
    table = Table(title="Anonymization Metrics")
    table.add_column("Metric")
    table.add_column("Value")
    
    table.add_row("Suppressed Records", str(result.get_number_of_suppressed_records()))
    # ... more rows
    
    console.print(table)
```

#### Part D: Template Library

#### Step 1: Create Template System
- **New Directory**: `templates/`
- **Files**:
  - `templates/medical_data.json`
  - `templates/census_data.json`
  - `templates/financial_data.json`

#### Step 2: Add Template Management
- **New File**: `src/anonymization_manager/utils/templates.py`
- **Purpose**: Template loading and management

**Implementation:**
```python
def list_templates() -> list[str]:
    """List available templates."""
    templates_dir = Path(__file__).parent.parent.parent / "templates"
    return [f.stem for f in templates_dir.glob("*.json")]

def load_template(name: str) -> AnonymizationConfig:
    """Load a template configuration."""
    template_path = Path(__file__).parent.parent.parent / "templates" / f"{name}.json"
    return AnonymizationConfig.from_json(template_path)
```

#### Step 3: Add CLI Commands
- **File**: `src/anonymization_manager/cli/main.py`
- **Changes**: Add `list-templates` and `use-template` commands

### Testing
- Test CLI commands
- Test configuration wizard
- Verify template loading
- Test interactive visualizations

### Files to Create/Modify
1. **New**: `src/anonymization_manager/cli/__init__.py`
2. **New**: `src/anonymization_manager/cli/main.py`
3. **New**: `src/anonymization_manager/cli/wizard.py`
4. **New**: `src/anonymization_manager/cli/visualize.py`
5. **New**: `src/anonymization_manager/utils/templates.py`
6. **New**: `templates/medical_data.json`
7. **Modify**: `pyproject.toml`

---


## General Implementation Guidelines

### Code Style
- Follow existing code style (Google-style docstrings, type hints)
- Use `ruff` for linting (line length: 79)
- Maintain backward compatibility

### Testing
- Write tests alongside implementation
- Aim for >80% code coverage
- Test edge cases and error conditions

### Documentation
- Update docstrings for all new functions/classes
- Update `Documentation.md` with new features
- Add examples for new functionality

### Version Control
- Create feature branches for each enhancement
- Write descriptive commit messages
- Consider breaking large enhancements into smaller PRs

---

## Additional Resources

### Academic Papers
- K-anonymity: Sweeney (2002)
- L-diversity: Machanavajjhala et al. (2007)
- T-closeness: Li et al. (2007)
- Differential Privacy: Dwork (2006)

### Libraries and Tools
- ARX Documentation: https://arx.deidentifier.org/
- ANJANA Documentation: Check library repository
- Pandas Documentation: https://pandas.pydata.org/
- FastAPI Documentation: https://fastapi.tiangolo.com/

### Testing Resources
- Pytest Documentation: https://docs.pytest.org/
- Hypothesis Documentation: https://hypothesis.readthedocs.io/

---

*This document should be updated as enhancements are implemented and new requirements are identified.*

