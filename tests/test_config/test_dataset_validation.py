import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import *


class TestDataset:
    @pytest.mark.parametrize(
        "dataset,error",
        [
            (PATH, None),  # Exists.
            ("dummy", FileNotFoundError),  # Does Not Exists.
            (123, TypeError),  # Integer
        ],
    )
    def test_dataset(self, dataset, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(dataset, [], [], [], [], {})
