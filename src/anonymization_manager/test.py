from anonymization_manager import *

if __name__ == "__main__":
    manager = AnonymizationManager.from_json("/home/jimmys/RECITALS/RECITALS-anonymization-manager/examples/template.json")
    manager.anonymize()