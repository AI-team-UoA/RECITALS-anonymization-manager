from loguru import logger

from anonymization_manager.adapters.anjana.anjana import (
    AnjanaAnonymizer,
    AnjanaResult,
)
from anonymization_manager.adapters.arx.arx import ARXAnonymizer, ARXResult
from anonymization_manager.config import AnonymizationConfig


class AnonymizedData:
    """
    Wrapper around the backend-specific result object.

    Forwards all attribute access to the underlying ARXResult or AnjanaResult
    instance. This presents a unified interface to the user regardless of which backend produced
    the result.
    """

    def __init__(self, result: ARXResult | AnjanaResult):
        """
        Initializes the AnonymizedData wrapper.

        Args:
            result (ARXResult | AnjanaResult): The backend result object.
        """
        self._result = result

    def __getattr__(self, name):
        """
        Forwards attribute access to the wrapped result object.

        Args:
            name (str): The name of the attribute or method.
        Returns:
            Any: The corresponding attribute or method from the underlying
            object.
        """
        return getattr(self._result, name)


class AnonymizationManager:
    """
    Entry point for the anonymization workflow.

    Directs execution to the appropriate backend adapter, wraps
    the result, and returns it to the caller.
    """

    def anonymize(config: AnonymizationConfig) -> AnonymizedData:
        """
        Anonymizes the dataset using the anonymization config.
        
        Args: 
            config (AnonymizationConfig):
                The configuration the anonymization manager must respect.

        Returns:
            AnonymizedData: A unified wrapper around the backend-specific result object.
        
        Raises:
            Exception: If the underlying anonymization engine fails.
        """
        if config.backend == None or config.backend == "arx":
            return AnonymizedData(ARXAnonymizer.anonymize(config))
        elif config.backend == "anjana":
            return AnonymizedData(AnjanaAnonymizer.anonymize(config))
        else:
            logger.warning(f"Unsupported backend: {config.backend}, using ARX")
            return AnonymizedData(ARXAnonymizer.anonymize(config))
