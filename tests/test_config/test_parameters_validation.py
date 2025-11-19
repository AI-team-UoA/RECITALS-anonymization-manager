from common import *

class TestParameters:
    @pytest.mark.parametrize("k,should_raise", [
        (None, False), # Default
        (1, False),    # Smallest Valid
        (10, False),   # Typical Valid
        (50, False),   # Larger Valid
        (-1, True),    # Negative
        (0, True),     # Zero
        (0.5, True),   # Float
        ("10", True),  # String
        ([], True),    # List
    ])
    def test_k_values(self, k, should_raise):
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, k=k
            )

    @pytest.mark.parametrize("l,should_raise", [
        (None, False), # Default
        (1, False),    # Smallest Valid
        (10, False),   # Typical Valid
        (50, False),   # Larger Valid
        (-1, True),    # Negative
        (0, True),     # Zero
        (0.5, True),   # Float
        ("10", True),  # String
        ([], True),    # List
    ])
    def test_l_values(self, l, should_raise):
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, l=l
            )


    @pytest.mark.parametrize("t,should_raise", [
        (None, False),  # Default
        (0.0, False),   # Smallest Valid
        (1.0, False),   # Largest Valid
        (0.55, False),  # Typical Valid
        (-1, True),     # Negative
        (2, True),      # Integer
        ("0.22", True), # String
        ([], True),     # List
    ])
    def test_t_values(self, t, should_raise):
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, t=t
            )

    @pytest.mark.parametrize("suppression_limit,should_raise", [
        (None, False),  # Default
        (10, False),    # Small Valid
        (55, False),    # Typical Valid
        (88, False),    # Large Valid
        (0, False),     # Smallest Valid
        (100, False),   # Largest Valid
        (0.68, True),   # Float
        (111, True),    # Too Large
        (-5, True),     # Negative
        ("67", True),   # String
        ([], True),     # List
    ])
    def test_suppression_values(self, suppression_limit, should_raise):
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, suppression_limit=suppression_limit
            )

    @pytest.mark.parametrize("backend,should_raise", [
        (None, False),      # Default
        ("arx", False),     # Arx
        ("anjana", False),  # Anjana
        ("foo", True),      # Invalid String
        ([], True),         # List
    ])
    def test_suppression_values(self, backend, should_raise):
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, backend=backend
            )