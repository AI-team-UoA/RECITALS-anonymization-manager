'''
    Dependencies.
'''
from py4j.java_gateway import JavaGateway, GatewayParameters
import os
'''
    This class is used to handle exceptions related to the ARX adapter.
'''
class ArxAdapterException(Exception):
    pass

'''
    This class serves as an adapter for the ARX library, it is responsible for the integration and interaction with the ARX Java library.
'''
class ArxAdapter:
    '''
        It initializes the ARX adapter.

        This includes starting the JVM and loading the appropriate ARX Java classes.
    '''
    def __init__(self):
        # Connect to the Java server
        gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))

        # Access the server's entry point
        adapter_server = gateway.entry_point

        result = adapter_server.ping()  # assumes your server has a public hello()

    def anonymize(self):
        pass

    '''
        Initializes the quasi-identifiers for the ARX library.
    '''
    def initialize_quasi_identifiers(self, quasi_identifiers:list[str]) -> None:
        pass

    '''
        Initializes the identifiers for the ARX library.
    '''
    def initialize_identifiers(self, identifiers:list[str]) -> None:
        pass

    '''
        Initializes the sensitive attributes for the ARX library.
    '''
    def initialize_sensitive_attributes(self, sensitive_attributes:list[str]) -> None:
        pass

    '''
        Initializes the insensitive attributes for the ARX library.
    '''   
    def initialize_insensitive_attributes(self, insensitive_attributes:list[str]) -> None:
        pass

if __name__ == "__main__":
    adapter = ArxAdapter()