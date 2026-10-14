from tests.common import *


class TestParameters:
    @pytest.mark.parametrize(
        "k,error",
        [
            (1, None),  # Smallest Valid
            (10, None),  # Typical Valid
            (50, None),  # Larger Valid
            (-1, ConfigurationError),  # Negative
            (0, ConfigurationError),  # Zero
            (0.5, ConfigurationError),  # Float
            ("10", None),  # String
            ([], ConfigurationError),  # List
        ],
    )
    def test_k_values(self, k, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, k=k)

    @pytest.mark.parametrize(
        "l,error",
        [
            (1, None),  # Smallest Valid
            (10, None),  # Typical Valid
            (50, None),  # Larger Valid
            (-1, ConfigurationError),  # Negative
            (0, ConfigurationError),  # Zero
            (0.5, ConfigurationError),  # Float
            ("10", None),  # String
            ([], ConfigurationError),  # List
        ],
    )
    def test_l_values(self, l, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, 
                                         sensitive_attributes=["foo"],
                                         l=l)

    @pytest.mark.parametrize(
        "t,error",
        [
            (0.0, None),  # Smallest Valid
            (1.0, None),  # Largest Valid
            (0.55, None),  # Typical Valid
            (-1, ConfigurationError),  # Negative
            (2, ConfigurationError),  # Integer
            ("0.22", None),  # String
            ([], ConfigurationError),  # List
        ],
    )
    def test_t_values(self, t, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, 
                                         sensitive_attributes=["foo"],
                                         t=t)

    @pytest.mark.parametrize(
        "suppression_limit,error",
        [
            (None, None),  # Default
            (10, ConfigurationError),  # Small Valid
            (55, ConfigurationError),  # Typical Valid
            (88, ConfigurationError),  # Large Valid
            (0, None),  # Smallest Valid
            (1, None),  # Largest Valid
            (100, ConfigurationError),  # Largest Valid
            (0.68, None),  # Float
            (111, ConfigurationError),  # Too Large
            (-5, ConfigurationError),  # Negative
            ("67", ConfigurationError),  # String
            ([], ConfigurationError),  # List
        ],
    )
    def test_suppression_values(self, suppression_limit, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, suppression_limit=suppression_limit,
                k=2
            )

    @pytest.mark.parametrize(
        "backend,error",
        [
            (None, None),  # None Is Not Accepted
            ("arx", None),  # Arx
            ("anjana", None),  # Anjana
            ("foo", ConfigurationError),  # Invalid String
            ([], ConfigurationError),  # List
        ],
    )
    def test_backend_values(self, backend, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, 
                backend=backend,
                k=2
            )

    @pytest.mark.parametrize(
        "attribute_weights,error",
        [
            (1, ConfigurationError),             # Int is not valid
            ({1,1}, ConfigurationError),         # Attribute name not a string
            ({"foo":"bar"}, ConfigurationError), # Weight not a number
            ({"foo":-0.5}, ConfigurationError), # Negative weight not allowed
            ({"foo":2, "bar":0.2}, None), # Valid weights
        ],
    )
    def test_attribute_weights(self, attribute_weights, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, 
                k=2,
                attribute_weights=attribute_weights, 
                backend="arx"
            )

    """
        The following checks do not check that the quality metric parameters, are valid!!

        They only check that the format is proper!!
    """
    @pytest.mark.parametrize("metric,error", [
        ("discernability", None),
        ("aecs", None),
        ("precision", None),
        ("height", None),
        ("loss", None),
        ("ambiguity", None),
        ("entropy", None),
        ("normalized-entropy", None),
    ])
    def test_quality_metrics(self, metric, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, 
                k=2,
                quality_metric={"name":metric},
                backend="arx"
            )

    @pytest.mark.parametrize("metric,gs_factor,error", [
        ("discernability", 0.5, None),
        ("aecs", 0.48, None),
        ("precision", 0.21, None),
        ("height", 0.3, None),
        ("loss", 0.12, None),
        ("ambiguity", 0.22, None),
        ("entropy", 0.33, None),
        ("normalized-entropy", 0.44, None),
    ])
    def test_quality_metrics_with_gs_factor(self, metric, gs_factor, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, 
                k=2,
                quality_metric={"name":metric, "params":{"gs_factor":gs_factor}},
                backend="arx"
            )

   