"""
Dependencies.
"""
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
        arx_path = os.path.join(os.path.dirname(__file__), "arx_adapter_javaside.jar")

        # Checks if the path exits.
        if not os.path.exists(arx_path):
            raise ArxAdapterException(f"ARX jar file not found at {arx_path}")
        
        # Stores the config.
        self.config = config

        # Starts the JVM with the jar file.
        jpype.startJVM(classpath=[arx_path])
        JavaAdapter = JClass("JavaArxAdapter")
        self.java_adapter = JavaAdapter()

    def load_data(self, data_path: str):
        '''
        Loads the data from the given path to ARX.
        '''
        self.java_adapter.loadData(data_path)
    
    def anonymize(self):
        '''
        Anonymizes the data using the configuration file.
        '''''
        self.load_data(self.config.data)
        self.define_identifiers(self.config.identifiers.get("ids", []))
        self.define_quasi_identifiers(self.config.identifiers.get("qids", []))
        self.define_sensitive_attributes(self.config.identifiers.get("satts", []))
        self.define_insensitive_attributes(self.config.identifiers.get("iatts", []))
        self.define_hierarchies(self.config.hierarchies)
        self.make_anonymous(self.config.parameters, self.config.anonymized_data)

    def make_anonymous(self, parameters:dict[str, float], output_path:str) -> None:
        '''
        Makes the data k-anonymous using ARX.
        '''
        HashMap = JClass("java.util.HashMap")
        java_map = HashMap()

        for parameter, value in parameters.items():
            java_map.put(parameter, value)
        self.java_adapter.makeAnonymous(java_map, output_path)

    def define_identifiers(
        self, identifiers: list[str]
    ) -> None:
        """
        Defines the identifiers for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for identifier in identifiers:
            array_list.add(identifier)
        self.java_adapter.defineIdentifiers(array_list)

    def define_quasi_identifiers(self, quasi_identifiers: list[str]) -> None:
        """
        Defines the quasi-identifiers for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for quasi_identifier in quasi_identifiers:
            array_list.add(quasi_identifier)
        self.java_adapter.defineQuasiIdentifiers(array_list)

    def define_sensitive_attributes(
        self, sensitive_attributes: list[str]
    ) -> None:
        """
        Initializes the sensitive attributes for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for sensitive_attribute in sensitive_attributes:
            array_list.add(sensitive_attribute)
        self.java_adapter.defineSensitiveAttributes(array_list)

    def update_config(self, new_config: AnonymizationConfig) -> None:
        """
        Updates the configuration of the adapter.
        """
        self.config = new_config
        
    def define_hierarchies(
            self, hierarchies: dict[str, str]
    ) -> None:
        """
        Defines the hierarchies for the ARX library.
        """
        HashMap = JClass("java.util.HashMap")
        java_map = HashMap()

        for attribute, hierarchy_path in hierarchies.items():
            java_map.put(attribute, hierarchy_path)
        self.java_adapter.defineHierarchies(java_map)

    def define_insensitive_attributes(
        self, insensitive_attributes: list[str]
    ) -> None:
        """
        Initializes the insensitive attributes for the ARX library.
        """
        ArrayList = JClass("java.util.ArrayList")
        array_list = ArrayList()
        
        for insensitive_attribute in insensitive_attributes:
            array_list.add(insensitive_attribute)
        self.java_adapter.defineInsensitiveAttributes(array_list)
    
    def ping(self) -> None:
        """
        Pings the ARX adapter to check if it is alive.
        """
        adapter = jpype.JClass("JavaArxAdapter")
        adapter_instance = adapter()
        adapter_instance.ping()

        
    def __del__(self):
        """
        It shuts down the JVM when the adapter is deleted.
        """
        if jpype.isJVMStarted():
            jpype.shutdownJVM()

