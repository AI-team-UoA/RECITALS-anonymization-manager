from common import *

class TestHierarchies:
    @pytest.mark.parametrize("hierarchies,quasi_identifiers,should_raise", [
        ({}, [], False),            # Default.
        (
            {
                "age":AGE_PATH     # Single Hierarchy
            },
            ["age"],
            False
        ),
        (
            {
                "age":AGE_PATH,
                "country":COUNTRY_PATH,
                "race":RACE_PATH
            },
            [
                "age",
                "country",
                "race"
            ],
            False
        ),
        (
            {
                "age":"age.csv"     # Hierarchy File Does Not Exist
            },
            [],
            True
        ),
        (
            {
                "age":AGE_PATH     # Hierarchy Quasi Identifier Not Defined
            },
            [],
            True
        ),
        (
            {
                123:AGE_PATH       # Quasi Identifier Not A String
            },
            ["age"],
            True
        ),
        (
            {
                "age":123          # Hierarchy Path Not A String
            },
            ["age"],
            True
        ),
    ])
    def test_hierarchies(self, hierarchies, quasi_identifiers, should_raise) -> None:
        with pytest.raises(ValueError) if should_raise else contextlib.nullcontext():
            config = AnonymizationConfig(
                PATH, [], quasi_identifiers, [], [], hierarchies
            )