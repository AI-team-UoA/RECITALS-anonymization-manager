from anonymization_manager.core import *

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
                                "arx"
                                 ) 
    
    res = AnonymizationManager.anonymize(config)
    print(res.get_as_dataframe())
    print("next", res.get_transformations())
    print(res.get_average_equivalence_class_size())
    print(res.get_number_of_suppressed_records())
    print(res.get_max_equivalence_class_size())
    print(res.get_min_equivalence_class_size())
    print(res.get_number_of_equivalence_classes())
    print(res.get_discernibility_metric())
    print(res.get_average_class_size_metric())
    print(res.get_granularity_metric("Age"))
    print(res.get_ssesst_metric())