from anonymization_manager.exceptions import NoSolutionError
from tests.common import *


class TestNoSolution:
    def _infeasible_config(self, backend: str) -> AnonymizationConfig:
        # `salary-class` has only 2 distinct values, so l=7 cannot be satisfied
        # not even with suppression.
        return AnonymizationConfig(
            data=PATH,
            quasi_identifiers=["age", "sex"],
            sensitive_attributes=["salary-class"],
            hierarchies={
                "age": AGE_PATH,
                "sex": SEX_PATH,
            },
            l=7,
            suppression_limit=0.5,
            backend=backend,
        )

    @pytest.mark.parametrize("backend", ["arx", "anjana"])
    def test_infeasible_privacy_model_raises_no_solution(self, backend) -> None:
        with pytest.raises(NoSolutionError) as e_info:
            AnonymizationManager.anonymize(self._infeasible_config(backend))

        assert e_info.value.backend == backend

    @pytest.mark.parametrize("backend", ["arx", "anjana"])
    def test_no_solution_is_backend_error(self, backend) -> None:
        with pytest.raises(BackendError):
            AnonymizationManager.anonymize(self._infeasible_config(backend))
