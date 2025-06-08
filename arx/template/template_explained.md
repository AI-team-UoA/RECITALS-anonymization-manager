# Preview
This is a preview of the structure of the .json file used for interacting with the arx api.
```json
{
    "data_path" : "path/to/data",

    "identifiers" : {
        "ids" : ["identifier1", "identifier2", "identifier3"],
        "qids" : ["qidentifier1", "qidentifier2", "qidentifier3"],
        "sids" : ["sidentifier1", "sidentifier2", "sidentifier3"],
        "iids" : ["iidentifier1", "iidentifier2", "iidentifier3"]
    },

    "hierarchies" : {
        "h1":"path/to/h1", 
        "h2":"path/to/h2",
        "h3":"path/to/h3"  
    },

    "privacy_model" : {
        "name" : "name", 

        "parameters" : {
            "param_name1" : "param_value1",
            "param_name2" : "param_value2",
            "param_name3" : "param_value3"
        },

        "quality_metric" : {
            "metric_name" : "name",
            "parameters" : {
                "param_name1" : "param_value1",
                "param_name2" : "param_value2",
                "param_name3" : "param_value3"
            }
        },

        "suppresion" : {
            "level" : "value"
        }
    },
    
    "anonymized_data_path" : "path/to/anonymized_data"
}
```
# Structure
1. `data_path` : Is the path to the input data.
2. `identifiers` : Contains information regarding the identifiers. We refer to quasi-identifiers as qids, to sensitive indentifiers as sids, and to identifying identifiers as iids.
3. `hierarchies` : Holds the paths to the user defined hierarchies.
4. `privacy_model` : Has all the necessary info regarding the privacy model that the user wants to be used. Such as the name of the model, any parameters it might need and any quality metrices that should be forced.
5. `anonymized_data_path` : Is the path to the anonymized data, so basically this path points to where the anonymized data should be stored.