## Overview
RECITALS Anonymization Manager is a privacy-preserving data anonymization toolkit that supports key techniques such as k-anonymity, l-diversity and t-closeness. It enables users to protect sensitive information in datasets while maintaining data utility.

The toolkit is designed to simplify the anonymization process by providing reusable templates, allowing users to easily apply privacy transformations without manually configuring complex rules. This makes it suitable for researchers and developers who need fast, consistent, and reliable data anonymization workflows.
### Supported Techniques
- **k-anonymity**: Ensures that each record is indistinguishable from at least *k-1* other records with repsect to identifying/quasi-identifying attributes, reducing the risk of re-identification.
- **l-diversity**: Extends k-anonymity by ensuring that sensitive attributes within each group have at least *l* well-represented values.
- **t-closeness**: Strengthens privacy further by requiring that the distribution of sensitive attributes in each group is within a threshold *t* of the overall dataset distribution.