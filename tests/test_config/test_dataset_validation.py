from common import *

class TestDataset:
    @pytest.mark.parametrize("dataset,should_raise", [
        (PATH, False),      # Exists.
        ("dummy", True),    # Does Not Exists.
        (123, True)         # Integer
    ])
    def test_dataset(self, dataset, should_raise) -> None:
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                dataset, [], [], [], [], {}
            )
