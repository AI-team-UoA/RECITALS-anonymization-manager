import pandas as pd
import os
import jpype
from jpype import JClass
from anonymization_manager.config import AnonymizationConfig

class ARXAnonymizerException(Exception):
    """
    This class is responsible for handling ARX related exceptions
    """
    pass

class ARXResult:
    """
    This is a wrapper for the ARXResult Java object.
    """

    def __init__(self, java_arx_result) -> None:
        self.arx_result = java_arx_result

    def get_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the anonymized data from ARX as a pandas dataframe.
        """
        data_handle = self.arx_result.getOutput()

        column_names = [data_handle.getAttributeName(i) for i in range(data_handle.getNumColumns())]

        data = []

        for i in range(data_handle.getNumRows()):
            row = [data_handle.getValue(i,j) for j in range(data_handle.getNumColumns())]
            data.append(row)

        df = pd.DataFrame(data, columns=column_names)
        return df
    
    def get_transformations(self) -> dict[str, int]:
        """
        Returns the transformations applied to each quasi-identifier.
        """
        output_data = self.arx_result.getOutput()
        quasi_identifiers = output_data.getDefinition().getQuasiIdentifyingAttributes().toArray()
        transformations = {quasi_identifier: self.arx_result.getOutput().getGeneralization(quasi_identifier) for quasi_identifier in quasi_identifiers}
        return transformations
    
    def store_as_csv(self) -> None:
        """
        Stores the anonymized dataset as .csv file.
        """
        pass

class ARXAnonymizer:
    """
    This class is responsible for anonymizing datasets using the ARX library.
    """

    @classmethod
    def _load_arx_library(cls) -> None:
        """
        Loads the ARX Java library and starts the JVM.
        """ 
        libarx = os.path.join(os.path.dirname(__file__), "libarx-3.9.2.jar")

        if not os.path.exists(libarx):
            raise ARXAnonymizerException(f"Could not locate libarx at {libarx}")
        
        jpype.startJVM(classpath = [libarx])

    @classmethod
    def _define_attribute_types(cls, data:JClass, config:AnonymizationConfig) -> None:
        """
        Defines the attribute types.
        """
        AttributeType = JClass("org.deidentifier.arx.AttributeType")

        # Declares identifiers.
        for identifier in config.identifiers:
            data.getDefinition().setAttributeType(identifier, AttributeType.IDENTIFYING_ATTRIBUTE)

        # Declares quasi-identifiers.
        for quasi_identifier in config.quasi_identifiers:
            data.getDefinition().setAttributeType(quasi_identifier, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE)
    
        # Declares sensitive attributes.
        for sensitive_attribute in config.sensitive_attributes:
            data.getDefinition().setAttributeType(sensitive_attribute, AttributeType.SENSITIVE_ATTRIBUTE)

        # Declares insensitive attributes.
        for insensitive_attribute in config.insensitive_attributes:
            data.getDefinition().setAttributeType(insensitive_attribute, AttributeType.INSENSITIVE_ATTRIBUTE)

    @classmethod
    def _define_hierarchies(cls, data:JClass, config:AnonymizationConfig) -> None:
        """
        Defines the hierarchies.
        """
        Hierarchy = JClass("org.deidentifier.arx.AttributeType.Hierarchy")
        CharSet = JClass("java.nio.charset.Charset")

        # Defines all of the hierarchies.
        for attribute, hierarchy_path in config.hierarchies.items():
            hierarchy = Hierarchy.create(hierarchy_path, CharSet.forName("UTF-8"), ',')
            data.getDefinition().setHierarchy(attribute, hierarchy)

    @classmethod
    def _create_arx_configuration(cls, config:AnonymizationConfig) -> JClass:
        """
        Creates the configuration for the anonymization process.
        """
        KAnonymity = JClass("org.deidentifier.arx.criteria.KAnonymity")
        LDiversity = JClass("org.deidentifier.arx.criteria.DistinctLDiversity")
        TCloseness = JClass("org.deidentifier.arx.criteria.EqualDistanceTCloseness")
        ARXConfiguration = JClass("org.deidentifier.arx.ARXConfiguration")
        configuration = ARXConfiguration.create()

        # Adds a supression limit.
        if config.suppression_limit is not None:
            configuration.setSuppressionLimit(config.suppression_limit)

        # Adds k-anonymity.
        if config.k is not None:
            configuration.addPrivacyModel(KAnonymity(config.k))
        
        # Adds l-diversity.
        if config.l is not None:
            for sensitive_attribute in config.sensitive_attributes:
                configuration.addPrivacyModel(LDiversity(sensitive_attribute, config.l))
        
        # Adds t-closeness.
        if config.t is not None:
            for sensitive_attribute in config.sensitive_attributes:
                configuration.addPrivacyModel(TCloseness(sensitive_attribute, config.t))
        
        return configuration
    
    @classmethod
    def _anonymize(cls, data:JClass, configuration:JClass) -> JClass:
        """
        Anonymizes the data by applying the configuration.
        """
        ARXAnonymizer = JClass("org.deidentifier.arx.ARXAnonymizer")
        anonymizer = ARXAnonymizer()
        return anonymizer.anonymize(data, configuration)
    
    @classmethod
    def anonymize(cls, config:AnonymizationConfig) -> ARXResult:
        """
        Anonymizes the dataset using the given configurations.
        """
        ARXAnonymizer._load_arx_library()
        Data = JClass("org.deidentifier.arx.Data")
        CharSet = JClass("java.nio.charset.Charset")

        # Creates the data.
        data = Data.create(config.data, CharSet.forName("UTF-8"), ',')

        # Defines the attribute types.
        ARXAnonymizer._define_attribute_types(data, config)

        # Defines the hierarchies.
        ARXAnonymizer._define_hierarchies(data, config)

        # Configures the privacy models.
        configuration = ARXAnonymizer._create_arx_configuration(config)

        # Runs the anonymization process.
        result = ARXAnonymizer._anonymize(data, configuration)

        # It returns the ARXResult.
        return ARXResult(result)
    
if __name__ == "__main__":
    config = AnonymizationConfig("/home/jimmys/RECITALS/RECITALS-anonymization-manager/examples/chatgpt_sample.csv"
                                , ["Name", "LastName"]
                                , ["Age"]
                                , ["Disease"]
                                , ["Gender"]
                                , {"Age" : "/home/jimmys/RECITALS/RECITALS-anonymization-manager/examples/age.csv"}
                                , 2
                                , 2
                                , 0.5
                                , 0.55,
                                "None",
                                "Arx"
                                 ) 
    
    res = ARXAnonymizer.anonymize(config)
    print(res.get_as_dataframe())
    print("next", res.get_transformations())