from tests.common import *


class TestParameters:
    @pytest.mark.parametrize(
        "k,error",
        [
            (None, None),  # Default
            (1, None),  # Smallest Valid
            (10, None),  # Typical Valid
            (50, None),  # Larger Valid
            (-1, ValidationError),  # Negative
            (0, ValidationError),  # Zero
            (0.5, ValidationError),  # Float
            ("10", None),  # String
            ([], ValidationError),  # List
        ],
    )
    def test_k_values(self, k, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, k=k)

    @pytest.mark.parametrize(
        "l,error",
        [
            (None, None),  # Default
            (1, None),  # Smallest Valid
            (10, None),  # Typical Valid
            (50, None),  # Larger Valid
            (-1, ValidationError),  # Negative
            (0, ValidationError),  # Zero
            (0.5, ValidationError),  # Float
            ("10", None),  # String
            ([], ValidationError),  # List
        ],
    )
    def test_l_values(self, l, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, l=l)

    @pytest.mark.parametrize(
        "t,error",
        [
            (None, None),  # Default
            (0.0, None),  # Smallest Valid
            (1.0, None),  # Largest Valid
            (0.55, None),  # Typical Valid
            (-1, ValidationError),  # Negative
            (2, ValidationError),  # Integer
            ("0.22", None),  # String
            ([], ValidationError),  # List
        ],
    )
    def test_t_values(self, t, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, t=t)

    @pytest.mark.parametrize(
        "suppression_limit,error",
        [
            (None, None),  # Default
            (10, ValidationError),  # Small Valid
            (55, ValidationError),  # Typical Valid
            (88, ValidationError),  # Large Valid
            (0, None),  # Smallest Valid
            (1, None),  # Largest Valid
            (100, ValidationError),  # Largest Valid
            (0.68, None),  # Float
            (111, ValidationError),  # Too Large
            (-5, ValidationError),  # Negative
            ("67", ValidationError),  # String
            ([], ValidationError),  # List
        ],
    )
    def test_suppression_values(self, suppression_limit, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, suppression_limit=suppression_limit
            )

    @pytest.mark.parametrize(
        "backend,error",
        [
            (None, None),  # None Is Not Accepted
            ("arx", None),  # Arx
            ("anjana", None),  # Anjana
            ("foo", ValidationError),  # Invalid String
            ([], ValidationError),  # List
        ],
    )
    def test_backend_values(self, backend, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, backend=backend
            )

    @pytest.mark.parametrize(
        "attribute_weights,error",
        [
            (1, ValidationError),             # Int is not valid
            ({1,1}, ValidationError),         # Attribute name not a string
            ({"foo":"bar"}, ValidationError), # Weight not a number
            ({"foo":-0.5}, ValidationError), # Negative weight not allowed
            ({"foo":2, "bar":0.2}, None), # Valid weights
        ],
    )
    def test_attribute_weights(self, attribute_weights, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, 
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
                quality_metric={"name":metric, "params":{"gs_factor":gs_factor}},
                backend="arx"
            )

   