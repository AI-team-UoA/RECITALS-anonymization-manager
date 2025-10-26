import os

import jpype
import pandas as pd
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

    def _data_handle_to_dataframe(data_handle: JClass) -> pd.DataFrame:
        """
        Converts a datahandle to a dataframe.
        """
        column_names = [
            data_handle.getAttributeName(i)
            for i in range(data_handle.getNumColumns())
        ]

        data = []

        for i in range(data_handle.getNumRows()):
            row = [
                data_handle.getValue(i, j)
                for j in range(data_handle.getNumColumns())
            ]
            data.append(row)

        df = pd.DataFrame(data, columns=column_names)
        return df

    def get_anonymized_data_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the anonymized data from ARX as a pandas dataframe.
        """
        data_handle = self.arx_result.getOutput()
        return ARXResult._data_handle_to_dataframe(data_handle)

    def get_raw_data_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the original dataset as a dataframe.
        """
        data_handle = self.arx_result.getInput()
        return ARXResult._data_handle_to_dataframe(data_handle)

    def get_transformations(self) -> dict[str, int]:
        """
        Returns the transformations applied to each quasi-identifier.
        """
        output_data = self.arx_result.getOutput()
        quasi_identifiers = (
            output_data.getDefinition()
            .getQuasiIdentifyingAttributes()
            .toArray()
        )
        transformations = {
            quasi_identifier: self.arx_result.getOutput().getGeneralization(
                quasi_identifier
            )
            for quasi_identifier in quasi_identifiers
        }
        return transformations

    def get_anonymization_time(self) -> int:
        """
        Returns the time it took to anonymize the dataset (Wall Clock).
        """
        return self.arx_result.getTime()

    def store_as_csv(self, output_path: str) -> None:
        """
        Stores the anonymized dataset as .csv file.
        """
        output = self.arx_result.getOutput()
        output.save(output_path, ",")

    def get_average_equivalence_class_size(self) -> float:
        """
        Returns the average equivalence class size.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getAverageEquivalenceClassSize()
        )

    def get_number_of_suppressed_records(self) -> int:
        """
        Returns the number of suppressed records, i.e. removed from the dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getNumberOfSuppressedRecords()
        )

    def get_max_equivalence_class_size(self) -> int:
        """
        Returns the maximum size of an equivalence class present in the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getMaximalEquivalenceClassSize()
        )

    def get_min_equivalence_class_size(self) -> int:
        """
        Returns the minimum size of an equivalence class present in the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getMinimalEquivalenceClassSize()
        )

    def get_number_of_equivalence_classes(self) -> int:
        """
        Returns the number of equivalence classes present in the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getNumberOfEquivalenceClasses()
        )

    def get_discernibility_metric(self) -> float:
        """
        Returns the discernibility metric for the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getDiscernibility()
            .getValue()
        )

    def get_average_class_size_metric(self) -> float:
        """
        Returns the average class metric, not to be confused with the other similarly named method.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getAverageClassSize()
            .getValue()
        )

    def get_granularity_metric(self, attribute: str) -> float:
        """
        Returns the granularity metric for the specific attribute.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getGranularity()
            .getValue(attribute)
        )

    def get_ssesst_metric(self) -> float:
        """
        Returns the ssesst metric for the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getSSESST()
            .getValue()
        )

    def get_record_level_squared_error_metric(self) -> float:
        """
        Returns the record level squared metric for the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getRecordLevelSquaredError()
            .getValue()
        )

    def get_attribute_level_squared_error_metric(
        self, attribute: str
    ) -> float:
        """
        Returns the attribute level squared metric for the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getAttributeLevelSquaredError()
            .getValue(attribute)
        )

    def get_non_uniform_entropy_metric(self, attribute: str) -> float:
        """
        Returns the non uniform entropy metric for the specific attribute in the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getNonUniformEntropy()
            .getValue(attribute)
        )

    def get_generalization_intensity_metric(self, attribute: str) -> float:
        """
        Returns the generalization intensity metric for the specific attribute in the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getGeneralizationIntensity()
            .getValue(attribute)
        )

    def get_ambiguity_metric(self) -> float:
        """
        Returns the ambiguity metric for the anonymized dataset.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getQualityStatistics()
            .getAmbiguity()
            .getValue()
        )


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
            raise ARXAnonymizerException(
                f"Could not locate libarx at {libarx}"
            )

        jpype.startJVM(classpath=[libarx])

    @classmethod
    def _define_attribute_types(
        cls, data: JClass, config: AnonymizationConfig
    ) -> None:
        """
        Defines the attribute types.
        """
        AttributeType = JClass("org.deidentifier.arx.AttributeType")

        # Declares identifiers.
        for identifier in config.identifiers:
            data.getDefinition().setAttributeType(
                identifier, AttributeType.IDENTIFYING_ATTRIBUTE
            )

        # Declares quasi-identifiers.
        for quasi_identifier in config.quasi_identifiers:
            data.getDefinition().setAttributeType(
                quasi_identifier, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE
            )

        # Declares sensitive attributes.
        for sensitive_attribute in config.sensitive_attributes:
            data.getDefinition().setAttributeType(
                sensitive_attribute, AttributeType.SENSITIVE_ATTRIBUTE
            )

        # Declares insensitive attributes.
        for insensitive_attribute in config.insensitive_attributes:
            data.getDefinition().setAttributeType(
                insensitive_attribute, AttributeType.INSENSITIVE_ATTRIBUTE
            )

    @classmethod
    def _define_hierarchies(
        cls, data: JClass, config: AnonymizationConfig
    ) -> None:
        """
        Defines the hierarchies.
        """
        Hierarchy = JClass("org.deidentifier.arx.AttributeType.Hierarchy")
        CharSet = JClass("java.nio.charset.Charset")

        # Defines all of the hierarchies.
        for attribute, hierarchy_path in config.hierarchies.items():
            hierarchy = Hierarchy.create(
                hierarchy_path, CharSet.forName("UTF-8"), ","
            )
            data.getDefinition().setHierarchy(attribute, hierarchy)

    @classmethod
    def _create_arx_configuration(cls, config: AnonymizationConfig) -> JClass:
        """
        Creates the configuration for the anonymization process.
        """
        KAnonymity = JClass("org.deidentifier.arx.criteria.KAnonymity")
        LDiversity = JClass("org.deidentifier.arx.criteria.DistinctLDiversity")
        TCloseness = JClass(
            "org.deidentifier.arx.criteria.EqualDistanceTCloseness"
        )
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
                configuration.addPrivacyModel(
                    LDiversity(sensitive_attribute, config.l)
                )

        # Adds t-closeness.
        if config.t is not None:
            for sensitive_attribute in config.sensitive_attributes:
                configuration.addPrivacyModel(
                    TCloseness(sensitive_attribute, config.t)
                )

        return configuration

    @classmethod
    def _anonymize(cls, data: JClass, configuration: JClass) -> JClass:
        """
        Anonymizes the data by applying the configuration.
        """
        ARXAnonymizer = JClass("org.deidentifier.arx.ARXAnonymizer")
        anonymizer = ARXAnonymizer()
        return anonymizer.anonymize(data, configuration)

    @classmethod
    def anonymize(cls, config: AnonymizationConfig) -> ARXResult:
        """
        Anonymizes the dataset using the given configurations.
        """
        ARXAnonymizer._load_arx_library()
        Data = JClass("org.deidentifier.arx.Data")
        CharSet = JClass("java.nio.charset.Charset")

        # Creates the data.
        data = Data.create(config.data, CharSet.forName("UTF-8"), ",")

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
