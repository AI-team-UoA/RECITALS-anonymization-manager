import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import *


class TestAttributes:
    @pytest.mark.parametrize(
        "identifiers,error",
        [
            ([], False),  # Default
            (["Name"], False),  # One Identifier
            (
                [
                    "Name",  # Many Identifiers
                    "Last Name",
                    "ID",
                    "Phone Number",
                ],
                False,
            ),
            ([1], TypeError),  # Integer Identifier
        ],
    )
    def test_identifier_values(self, identifiers, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(PATH, identifiers, [], [], [], {})

    @pytest.mark.parametrize(
        "qidentifiers,error",
        [
            ([], False),  # Default
            (["Age"], False),  # One Quasi-Identifier
            (
                [
                    "Age",  # Many Quasi-Identifiers
                    "ZIPCode",
                    "Sex",
                    "BirthDate",
                ],
                False,
            ),
            ([1], TypeError),  # Integer
        ],
    )
    def test_quasi_identifier_values(self, qidentifiers, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(PATH, [], qidentifiers, [], [], {})

    @pytest.mark.parametrize(
        "sensitives,error",
        [
            ([], False),  # Default
            (["Disease"], False),  # One Sensitive
            (
                [
                    "Income",  # Many Sensitives
                    "Disease",
                    "Voted For",
                ],
                False,
            ),
            ([1], TypeError),  # Integer Sensitive
        ],
    )
    def test_sensitive_values(self, sensitives, error) -> None:
        with pytest.raises(TypeError) if error else contextlib.nullcontext():
            config = AnonymizationConfig(PATH, [], [], sensitives, [], {}, l=2)

    @pytest.mark.parametrize(
        "insensitives,error",
        [
            ([], False),  # Default
            (["Color"], False),  # One Insensitive
            (
                [
                    "Color",  # Many Insensitives
                    "Food",
                    "Account Type",
                ],
                False,
            ),
            ([1], TypeError),  # Integer Insensitive
        ],
    )
    def test_insensitive_values(self, insensitives, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(PATH, [], [], [], insensitives, {})
