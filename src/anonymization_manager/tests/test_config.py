import pytest 
from anonymization_manager import *

class TestConfiguration:
    @pytest.mark.parametrize("k,should_raise", [
        (1, False),
        (10, False),
        (-1, True),
        (0, True),
        (-10, True),
        (0.5, True),
    ])
    def test_k_values(self, k, should_raise):
        if should_raise:
            with pytest.raises(ValueError):
                config = AnonymizationConfig("dummy", [], [], [], [], {}, k=k)
        else:
            config = AnonymizationConfig("dummy", [], [], [], [], {}, k=k)

    @pytest.mark.parametrize("l,should_raise", [
        (1, False),
        (10, False),
        (-1, True),
        (0, True),
        (-10, True),
        (0.5, True),
    ])
    def test_l_values(self, l, should_raise):
        if should_raise:
            with pytest.raises(ValueError):
                config = AnonymizationConfig("dummy", [], [], [], [], {}, l=l)
        else:
            config = AnonymizationConfig("dummy", [], [], [], [], {}, l=l)


    @pytest.mark.parametrize("t,should_raise", [
        (1.0, False),
        (0.55, False),
        (-1, True),
        (0.0, False),
        (-10, True),
        (0.69, False),
    ])
    def test_t_values(self, t, should_raise):
        if should_raise:
            with pytest.raises(ValueError):
                config = AnonymizationConfig("dummy", [], [], [], [], {}, t=t)
        else:
            config = AnonymizationConfig("dummy", [], [], [], [], {}, t=t)

    @pytest.mark.parametrize("suppression_limit,should_raise", [
        (11, False),
        (55, False),
        (-1, True),
        (0.68, True),
        (111, True),
        (0, False),
        (67, False),
    ])
    def test_suppression_values(self, suppression_limit, should_raise):
        if should_raise:
            with pytest.raises(ValueError):
                config = AnonymizationConfig("dummy", [], [], [], [], {}, suppression_limit=suppression_limit)
        else:
            config = AnonymizationConfig("dummy", [], [], [], [], {}, suppression_limit=suppression_limit)

    @pytest.mark.parametrize("backend,should_raise", [
        ("arx", False),
        ("anjana", False),
        ("foo", True),
        ("bar", True),
    ])
    def test_suppression_values(self, backend, should_raise):
        if should_raise:
            with pytest.raises(ValueError):
                config = AnonymizationConfig("dummy", [], [], [], [], {}, backend=backend)
        else:
            config = AnonymizationConfig("dummy", [], [], [], [], {}, backend=backend)
        