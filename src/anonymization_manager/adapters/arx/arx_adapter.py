"""
Dependencies.
"""
import pandas as pd
import os
import jpype
from jpype import JClass
from anonymization_manager.config import AnonymizationConfig

class ArxAdapterException(Exception):
    """
    This class is used to handle exceptions related to the ARX adapter.
    """
    pass


class ArxAdapter:
    """
    This class serves as an adapter for the ARX library, it is responsible for the integration and interaction with the ARX Java library.
    """

    """
    This is a reference to the Java class that is responsible for communicating with ARX.
    """
    java_adapter = None

    def __init__(self, config: AnonymizationConfig) -> None:
        """
        It initializes the ARX adapter.
        """

        # Gets the path of arx.
        arx_path = os.path.join(os.path.dirname(__file__), "ArxAdapter.jar")

        # Checks if the path exits.
        if not os.path.exists(arx_path):
            raise ArxAdapterException(f"ARX jar file not found at {arx_path}")
        
        # Stores the config.
        self.config = config

        # Starts the JVM with the jar file.
        jpype.startJVM(classpath=[arx_path])
        JavaAdapter = JClass("JavaArxAdapter")
        self.java_adapter = JavaAdapter()

    def _load_data(self, data_path: str):
        '''
        Loads the data from the given path to ARX.
        '''
        self.java_adapter.loadData(data_path)
    
    def anonymize(self) -> tuple[int, dict[str, int]]:
        '''
        Anonymizes the data using the configuration file.
        '''''
        self._load_data(self.config.data)
        self._define_identifiers()
        self._define_quasi_identifiers()
        self._define_sensitive_attributes()
        self._define_insensitive_attributes()
        self._define_hierarchies(self.config.hierarchies)
        return 1, self._make_anonymous()

    def _make_anonymous(self) -> dict[str, int]:
        '''
        Makes the data k-anonymous using ARX.
        '''
        Int = JClass("java.lang.Integer")
        Double = JClass("java.lang.Double")

        # Gets the anonymization parameters.
        k = Int(self.config.k) if self.config.k is not None else None
        l = Int(self.config.l) if self.config.l is not None else None
        t = Double(self.config.t) if self.config.t is not None else None

        # Arx requires that the suppression limit is between 0 and 1 instead of 0 to 100.
        s = Double(self.config.suppression_limit/100) if self.config.suppression_limit is not None else None

        # Makes the data anonymous and returns the transformations.
        result = self.java_adapter.makeAnonymous(k, l , t, s, self.config.anonymized_data)
        transformations = {str(entry.getKey()): int(entry.getValue()) for entry in result.entrySet()}
        return transformations

    def _define_identifiers(
        self
    ) -> None:
        """
        Defines the identifiers for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for identifier in self.config.identifiers:
            array_list.add(identifier)
        self.java_adapter.defineIdentifiers(array_list)

    def _define_quasi_identifiers(self) -> None:
        """
        Defines the quasi-identifiers for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for quasi_identifier in self.config.quasi_identifiers:
            array_list.add(quasi_identifier)
        self.java_adapter.defineQuasiIdentifiers(array_list)

    def _define_sensitive_attributes(self) -> None:
        """
        Initializes the sensitive attributes for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for sensitive_attribute in self.config.sensitive_attributes:
            array_list.add(sensitive_attribute)
        self.java_adapter.defineSensitiveAttributes(array_list)

    def update_config(self, new_config: AnonymizationConfig) -> None:
        """
        Updates the configuration of the adapter.
        """
        self.config = new_config
        
    def _define_hierarchies(self, hierarchies: dict[str, str]) -> None:
        """
        Defines the hierarchies for the ARX library.
        """
        HashMap = JClass("java.util.HashMap")
        java_map = HashMap()

        for attribute, hierarchy_path in hierarchies.items():
            java_map.put(attribute, hierarchy_path)
        self.java_adapter.defineHierarchies(java_map)

    def _define_insensitive_attributes(self) -> None:
        """
        Initializes the insensitive attributes for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for insensitive_attribute in self.config.insensitive_attributes:
            array_list.add(insensitive_attribute)
        self.java_adapter.defineInsensitiveAttributes(array_list)
    
    def __del__(self):
        """
        It shuts down the JVM when the adapter is deleted.
        """
        if jpype.isJVMStarted():
            jpype.shutdownJVM()

