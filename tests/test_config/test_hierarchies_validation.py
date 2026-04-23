from tests.common import *


class TestHierarchies:
    @pytest.mark.parametrize(
        "hierarchies,quasi_identifiers,error",
        [
            ({}, [], False),  # Default.
            (
                {
                    "age": AGE_PATH  # Single Hierarchy
                },
                ["age"],
                False,
            ),
            (
                {"age": AGE_PATH, "country": COUNTRY_PATH, "race": RACE_PATH},
                ["age", "country", "race"],
                False,
            ),
            (
                {
                    "age": "age.csv"  # Hierarchy File Does Not Exist
                },
                ["age"],
                FileNotFoundError,
            ),
            (
                {
                    "age": AGE_PATH  # Hierarchy Quasi Identifier Not Defined
                },
                [],
                ValueError,
            ),
            (
                {
                    123: AGE_PATH  # Quasi Identifier Not A String
                },
                ["age"],
                ValidationError,
            ),
            (
                {
                    "age": 123  # Hierarchy Path Not A String
                },
                ["age"],
                ValidationError,
            ),
        ],
    )
    def test_hierarchies(self, hierarchies, quasi_identifiers, error) -> None:
        with pytest.raises(error) if error else contextlib.nullcontext():
            config = AnonymizationConfig(
                data=PATH, 
                quasi_identifiers=quasi_identifiers,
                hierarchies=hierarchies
            )
