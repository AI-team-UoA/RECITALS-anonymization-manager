from common import *

class TestAttributes:
    @pytest.mark.parametrize("identifiers,should_raise", [
        ([], False),         # Default
        (["Name"], False),   # One Identifier
        (
            [
                "Name",      # Many Identifiers
                "Last Name",
                "ID",
                "Phone Number"
            ], 
            False
        ),
        ([1], True),         # Integer Identifier
    ])
    def test_identifier_values(self, identifiers, should_raise) -> None:
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, identifiers, [], [], [], {}
            )

    @pytest.mark.parametrize("qidentifiers,should_raise", [
        ([], False),        # Default
        (["Age"], False),   # One Quasi-Identifier
        (
            [
                "Age",      # Many Quasi-Identifiers
                "ZIPCode",
                "Sex",
                "BirthDate"
            ],
            False
        ),
        ([1], True),        # Integer
    ])
    def test_quasi_identifier_values(self, qidentifiers, should_raise) -> None:
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], qidentifiers, [], [], {}
            )

    @pytest.mark.parametrize("sensitives,should_raise", [
        ([], False),           # Default
        (["Disease"], False),  # One Sensitive
        (
            [
                "Income",      # Many Sensitives
                "Disease",
                "Voted For",
            ], 
            False
        ),
        ([1], True),         # Integer Sensitive
    ])
    def test_sensitive_values(self, sensitives, should_raise) -> None:
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], sensitives, [], {}
            )

    @pytest.mark.parametrize("insensitives,should_raise", [
        ([], False),         # Default
        (["Color"], False),  # One Insensitive
        (
            [
                "Color",      # Many Insensitives
                "Food",
                "Account Type",
            ], 
            False
        ),
        ([1], True),         # Integer Insensitive
    ])
    def test_insensitive_values(self, insensitives, should_raise) -> None:
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], [], [], insensitives, {}
            )
        