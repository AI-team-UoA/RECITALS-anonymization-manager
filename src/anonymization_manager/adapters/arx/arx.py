import os

import jpype
import pandas as pd
from typing import Any
from jpype import JClass

from anonymization_manager.config import AnonymizationConfig


class ARXAnonymizerException(Exception):
    """
    This class is responsible for handling ARX related exceptions
    """

    pass


class ARXResult:
    """
    Wrapper for the ARX Java Result object.

    Provides Pythonic access to anonymization results, equivalence class
    statistics, and various quality metrics.
    """

    def __init__(self, java_arx_result) -> None:
        """
        Initializes the ARXResult wrapper.

        Args:
            java_arx_result (jpype._jclass.org.deidentifier.arx.ARXResult):
                The Java Arx result object.
        """
        self.arx_result = java_arx_result

    @staticmethod
    def _data_handle_to_dataframe(data_handle: JClass) -> pd.DataFrame:
        """
        Converts a Java ARX DataHandle object to a pandas DataFrame.

        Args:
            data_handle (jpype._jclass.org.deidentifier.arx.DataHandle):
                The ARX DataHandle Object.

        Returns:
            pd.DataFrame: The dataset as a pandas DataFrame.
        """
        column_names = [
            str(data_handle.getAttributeName(i))
            for i in range(data_handle.getNumColumns())
        ]

        data = []

        for i in range(data_handle.getNumRows()):
            row = [
                str(data_handle.getValue(i, j))
                for j in range(data_handle.getNumColumns())
            ]
            data.append(row)

        df = pd.DataFrame(data, columns=column_names)
        return df

    def get_anonymized_data_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the anonymized dataset as a pandas DataFrame.

        Returns:
            pd.Dataframe: Anonymized data.
        """
        data_handle = self.arx_result.getOutput()
        return ARXResult._data_handle_to_dataframe(data_handle)

    def get_raw_data_as_dataframe(self) -> pd.DataFrame:
        """
        Returns the original (raw) dataset as a pandas DataFrame.

        Returns:
            pd.DataFrame: Original data.
        """
        data_handle = self.arx_result.getInput()
        return ARXResult._data_handle_to_dataframe(data_handle)

    def get_transformations(self) -> dict[str, int]:
        """
        Gets the generalization levels applied to quasi-identifiers.

        Returns:
            dict[str, int]: Mapping of quasi-identifier names to their generalization level.
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
        Returns the wall-clock time taken for anonymization.

        Returns:
            int: Time in milliseconds.
        """
        return self.arx_result.getTime()

    def store_as_csv(self, output_path: str) -> None:
        """
        Stores the anonymized dataset as CSV file.

        Args:
            output_path (str): File path to save the CSV.
        """
        output = self.arx_result.getOutput()
        output.save(output_path, ",")

    def get_average_equivalence_class_size(self) -> float:
        """
        Returns the average size of equivalence classes.

        Returns:
            float: Average equivalence class size.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getAverageEquivalenceClassSize()
        )

    def get_number_of_suppressed_records(self) -> int:
        """
        Returns the number of suppressed (removed) records.

        Returns:
            int: Number of suppressed records.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getNumberOfSuppressedRecords()
        )

    def get_max_equivalence_class_size(self) -> int:
        """
        Returns the maximum equivalence class size.

        Returns:
            int: Maximum equivalence class size.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getMaximalEquivalenceClassSize()
        )

    def get_min_equivalence_class_size(self) -> int:
        """
        Returns the minimum equivalence class size.

        Returns:
            int: Minimum equivalence class size.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getMinimalEquivalenceClassSize()
        )

    def get_number_of_equivalence_classes(self) -> int:
        """
        Returns the number of equivalence classes.

        Returns:
            int: Number of equivalence classes.
        """
        return (
            self.arx_result.getOutput()
            .getStatistics()
            .getEquivalenceClassStatistics()
            .getNumberOfEquivalenceClasses()
        )

    def get_discernability_metric(self) -> float:
        """
        Returns the discernability metric, a measure of information loss.

        Returns:
            float: discernability metric value.
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
        Returns the average class size metric.

        Note:
            This metric is different from the average equivalence class size.

        Returns:
            float: Average class size metric value.
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
        Returns the granularity metric for a specific attribute.

        Args:
            attribute (str): The attribute name.

        Returns:
            float: Granularity metric value.
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
        Returns the SSESST metric value.

        Returns:
            float: SSESST metric value.
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
        Returns the record-level squared error metric.

        Returns:
            float: Record-level squared error value.
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
        Returns the attribute level squared metric for a specific attribute.

        Args:
            attribute (str): The attribute name.

        Returns:
            float: Attribute-level squared error value.
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
        Returns the non-uniform entropy metric for a specific attribute.

        Args:
            attribute (str): The attribute name.

        Returns:
            float: Non-uniform entropy value.
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
        Returns the generalization intensity metric for a specific attribute.

        Args:
            attribute (str): The attribute name.

        Returns:
            float: Generalization intensity value.
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
        Returns the ambiguity metric.

        Returns:
            float: Ambiguity metric value.
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
    Class responsible for anonymizing datasets using the ARX library.
    """

    @classmethod
    def _load_arx_library(cls) -> None:
        """
        Loads the ARX Java library and starts the JVM if not already running.

        Raises:
            FileNotFoundError: If the ARX Jar file is not found.
        """
        libarx = os.path.join(os.path.dirname(__file__), "libarx-3.9.2.jar")

        if not os.path.exists(libarx):
            raise FileNotFoundError(f"Could not locate libarx at {libarx}")

        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[libarx])

    @classmethod
    def _define_attribute_types(
        cls, data: JClass, config: AnonymizationConfig
    ) -> None:
        """
        Sets the attribute types for identifiers, quasi-identifiers, and sensitive/insensitive attributes.

        Args:
            data (JClass): The ARX Data object.
            config (AnonymizationConfig): The anonymization configuration.
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
        Defines the generalization hierarchies for the dataset attributes.

        Args:
            data (JClass): The ARX Data Object.
            config (AnonymizationConfig): The anonymization configuration.
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
        Creates an ARXConfiguration object with privacy models (k-anonymity, l-diversity, t-closeness).

        Args:
            config (AnonymizationConfig): The anonymization configuration.

        Returns:
            JClass: The ARXConfiguration object ready for the anonymization.
        """
        # Important types.
        KAnonymity = JClass("org.deidentifier.arx.criteria.KAnonymity")
        LDiversity = JClass("org.deidentifier.arx.criteria.DistinctLDiversity")
        TCloseness = JClass(
            "org.deidentifier.arx.criteria.EqualDistanceTCloseness"
        )
        Metric = JClass("org.deidentifier.arx.metric.Metric")
        ARXConfiguration = JClass("org.deidentifier.arx.ARXConfiguration")
        configuration = ARXConfiguration.create()
        agg_func = Metric.AggregateFunction

        # Adds a supression limit.
        if config.suppression_limit is not None:
            configuration.setSuppressionLimit(config.suppression_limit)
        
        # Adds a quality metric.
        if config.quality_metric is not None:
            # Maps the quality metrics to the appropriate constructor.
            quality_metric_map = {
                "discernability": Metric.createDiscernabilityMetric,
                "aecs": Metric.createAECSMetric,
                "precision": Metric.createPrecisionMetric,
                "height": Metric.createHeightMetric,
                "loss": Metric.createLossMetric,
                "ambiguity": Metric.createAmbiguityMetric,
                "entropy": Metric.createEntropyMetric,
                "normalized-entropy": Metric.createNormalizedEntropyMetric,
                "precomputed-entropy": Metric.createPrecomputedEntropyMetric,
                "publisher-payout": Metric.createPublisherPayoutMetric,
                "static": Metric.createStaticMetric,
                "precomputed-loss": Metric.createPrecomputedLossMetric,
                "kldivergence": Metric.createKLDivergenceMetric
            }

            # Maps the aggregate functions to the java appropriate classes.
            agg_func_map = {
                "SUM": agg_func.SUM,
                "ARITHMETIC_MEAN": agg_func.ARITHMETIC_MEAN,
                "GEOMETRIC_MEAN": agg_func.GEOMETRIC_MEAN,
                "RANK": agg_func.RANK,
                "MAXIMUM": agg_func.MAXIMUM

            }

            # Maps Java types to JPype types.
            java_to_jpype_map = {
                "double": jpype.JDouble,
                "float": jpype.JFloat,
                "int": jpype.JInt,
                "long": jpype.JLong,
                "boolean": jpype.JBoolean,
                "AggregateFunction": JClass("org.deidentifier.arx.metric.Metric$AggregateFunction")
            }

            # Gets the name and parameters.
            name = config.quality_metric.name
            params = config.quality_metric.params

            # Resolves the metric constructor.
            create_metric = quality_metric_map.get(name)
            if create_metric is None:
                raise ValueError(
                    f"Unsupported quality metric '{name}'!, "
                    f"Valid options are {list(quality_metric_map)}"
                )
            
            # Resolves the aggregate function if present.
            if "function" in params:
                func_name = params["function"]
                if func_name not in agg_func_map:
                    raise ValueError(
                        f"Unsupported aggregate function '{func_name}'!, "
                        f"Valid options are {list(agg_func_map)}"
                    )
                params["function"] = agg_func_map[func_name]

            # Collects the signatures.
            signatures = ARXAnonymizer._get_metric_signatures(create_metric.__doc__)

            possible_signs = [sign for sign in signatures if len(sign) == len(params)]

            # Narrows does by matching signatures.
            match = next(
                (sign for sign in possible_signs if ARXAnonymizer._validate_signature(params, sign)),
                None
            )
            
            # Checks if a match was found.
            if match is None:
                raise ValueError(
                    f"No overload of '{name}' matches the provided parameter types!, "
                    f"Check the arx documentation. Available overloads are {create_metric.__doc__}."
                )
            
            # Casts the values to JPype to get exact matching. 
            # It then tries to call the appropriate constructor.
            try:
                casted_params = [
                    java_to_jpype_map[t](v) if t != "AggregateFunction" else v
                    for t,v in zip(match, params.values())
                ]
                configuration.setQualityModel(create_metric(*casted_params))
            except Exception as e:
                raise ValueError(
                    f"Invalid quality metric configuration for '{name}'!, "
                    f"Parameters {params} are not valid!, "
                    f"Reason is {type(e).__name__}: {e}"
                )
            
        # Adds attribute weights.
        if config.attribute_weights is not None:
            for attribute, weight in config.attribute_weights.items():
                configuration.setAttributeWeight(attribute, weight)

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
        Executes the anonymization process using ARX.

        Args:
            data (JClass): The ARX Data object.
            configuration (JClass): The ARXConfiguration object.

        Returns:
            JClass:
                The ARX Java result object containing the anonymized data and metrics.
        """
        ARXAnonymizer = JClass("org.deidentifier.arx.ARXAnonymizer")
        anonymizer = ARXAnonymizer()
        return anonymizer.anonymize(data, configuration)

    @staticmethod
    def _get_metric_signatures(doc: str) -> list[list[str]]:
        """Parses JPype docstring to extract parameter lists per overload.
            e.g. from org.deidentifier.arx.metric.Metric createLossMetric(boolean)
            Args:
                doc (str): The description of the method.
            Returns:
                list[list[str]]:
                    The types of the parameters. 
        """
        signatures = []

        # Goes over all the lines.
        for line in doc.splitlines():
            line = line.strip()

            # We expect signatures to start with *.
            if not line.startswith("*"):
                continue
            
            # Deriving only the parameter types.
            types_start = line.index("(")+1
            types_end = line.index(")")
            types = line[types_start:types_end].strip()

            # Gets the types
            if not types:
                signatures.append([])
                continue
            else:
                types = [
                    t.strip().split(".")[-1]
                    for t in types.split(",")
                ]

            # Collect the types.
            signatures.append(types)

        return signatures
    
    @staticmethod
    def _validate_signature(params:dict[str,Any], types: list[Any]) -> bool:
        """
            Validates that the provided parameters match the given types.
            Args:
                params (dict[str, Any]): The parameters.
                types (list[Any]): The expected java types from the signature.

            Returns:
                bool: True if the params match the types of the signature.
        """
        java_to_python_map = {
            "double": (float, int),
            "float": (float, int),
            "int": int,
            "long": int,
            "boolean": bool,
            "AggregateFunction": JClass(
                "org.deidentifier.arx.metric.Metric$AggregateFunction"
            )
        }

        # Checks the parameter count.
        if len(params) != len(types):
            return False
        
        # Checks the types.
        for val, java_type in zip(params.values(), types):
            if java_type not in java_to_python_map:
                return False
            
            if isinstance(val, bool) and java_type != "boolean":
                return False
            
            if not isinstance(val, java_to_python_map[java_type]):
                return False
            
        return True
            
            
            
    
    @classmethod
    def anonymize(cls, config: AnonymizationConfig) -> ARXResult:
        """
        Anonymizes the dataset using the given configurations.

        This method loads the ARX library, sets up the data, defines attribute types and hierarchies,
        applies privacy models, and runs the anonymization process.

        Args:
            config (AnonymizationConfig): The anonymization configuration.

        Returns:
            ARXResult: A wrapper for the ARX Java result object.
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
