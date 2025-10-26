"""
The public-facing API of the Anonymization Manager component, part of the open
source RECITALS platform.
"""

import json

import pandas as pd

from anonymization_manager.adapters.anjana.anjana import (
    AnjanaAnonymizer,
    AnjanaResult,
)
from anonymization_manager.adapters.arx.arx import ARXAnonymizer, ARXResult
from anonymization_manager.config import AnonymizationConfig


class AnonymizedData:
    """
    This is a wrapper class for ARXResult, AnjanaResult.
    """

    def __init__(self, result: ARXResult | AnjanaResult):
        self._result = result

    def __getattr__(self, name):
        return getattr(self._result, name)


class AnonymizationManager:
    """
    This is the class representing the anonymization manager.
    """

    def anonymize(self, config: AnonymizationConfig) -> AnonymizedData:
        if config.backend == None or config.backend == "arx":
            return AnonymizedData(ARXAnonymizer.anonymize(config))
        else:
            return AnonymizedData(AnjanaAnonymizer.anonymize(config))
