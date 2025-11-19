import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import *

class TestParameters:
    @pytest.mark.parametrize("k,error", [
        (None, None),         # Default
        (1, None),            # Smallest Valid
        (10, None),           # Typical Valid
        (50, None),           # Larger Valid
        (-1, ValueError),     # Negative
        (0, ValueError),      # Zero
        (0.5, TypeError),     # Float
        ("10", TypeError),    # String
        ([], TypeError),      # List
    ])
    def test_k_values(self, k, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, k=k
            )

    @pytest.mark.parametrize("l,error", [
        (None, None),         # Default
        (1, None),            # Smallest Valid
        (10, None),           # Typical Valid
        (50, None),           # Larger Valid
        (-1, ValueError),     # Negative
        (0, ValueError),      # Zero
        (0.5, TypeError),     # Float
        ("10", TypeError),    # String
        ([], TypeError),      # List
    ])
    def test_l_values(self, l, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, l=l
            )


    @pytest.mark.parametrize("t,error", [
        (None, None),         # Default
        (0.0, None),          # Smallest Valid
        (1.0, None),          # Largest Valid
        (0.55, None),         # Typical Valid
        (-1, ValueError),     # Negative
        (2, ValueError),      # Integer
        ("0.22", TypeError),  # String
        ([], TypeError),      # List
    ])
    def test_t_values(self, t, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, t=t
            )

    @pytest.mark.parametrize("suppression_limit,error", [
        (None, None),         # Default
        (10, None),           # Small Valid
        (55, None),           # Typical Valid
        (88, None),           # Large Valid
        (0, None),            # Smallest Valid
        (100, None),          # Largest Valid
        (0.68, TypeError),    # Float
        (111, ValueError),    # Too Large
        (-5, ValueError),     # Negative
        ("67", TypeError),    # String
        ([], TypeError),      # List
    ])
    def test_suppression_values(self, suppression_limit, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, suppression_limit=suppression_limit
            )

    @pytest.mark.parametrize("backend,error", [
        (None, TypeError),       # None Is Not Accepted
        ("arx", None),           # Arx
        ("anjana", None),        # Anjana
        ("foo", ValueError),     # Invalid String
        ([], TypeError),         # List
    ])
    def test_backend_values(self, backend, error):
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], [], {}, backend=backend
            )