import pytest 
import contextlib
from anonymization_manager import *
from pathlib import Path

TEST_DIR = Path(__file__).parent
PATH=str(TEST_DIR/"test_dataset/data/adult.csv")
HIERARCHY_PATH=TEST_DIR/"test_dataset/hierarchies"
AGE_PATH=str(HIERARCHY_PATH/"age.csv")
COUNTRY_PATH=str(HIERARCHY_PATH/"country.csv")
RACE_PATH=str(HIERARCHY_PATH/"race.csv")
SEX_PATH=str(HIERARCHY_PATH/"sex.csv")
MARITAL_PATH=str(HIERARCHY_PATH/"marital.csv")
OCCUPATION_PATH=str(HIERARCHY_PATH/"occupation.csv")
WORK_CLASS_PATH=str(HIERARCHY_PATH/"workclass.csv")
EDUCATION_PATH=str(HIERARCHY_PATH/"education.csv")