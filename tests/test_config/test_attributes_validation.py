from tests.common import *


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
            ([1], ValidationError),  # Integer Identifier
        ],
    )
    def test_identifier_values(self, identifiers, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, 
                                         identifiers=identifiers
                                         )

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
            ([1], ValidationError),  # Integer
        ],
    )
    def test_quasi_identifier_values(self, qidentifiers, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, 
                                         quasi_identifiers=qidentifiers
                                         )

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
            ([1], ValidationError),  # Integer Sensitive
        ],
    )
    def test_sensitive_values(self, sensitives, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, 
                                         sensitive_attributes=sensitives,
                                         l=2)

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
            ([1], ValidationError),  # Integer Insensitive
        ],
    )
    def test_insensitive_values(self, insensitives, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(data=PATH, 
                                         insensitive_attributes=insensitives, 
                                         )
