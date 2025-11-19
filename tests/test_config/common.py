import pytest 
import contextlib
from anonymization_manager import *
from pathlib import Path

TEST_DIR = Path(__file__).parent.parent
PATH=str(TEST_DIR/"test_dataset/data/adult.csv")
AGE_PATH=str(TEST_DIR/"test_dataset/hierarchies/age.csv")
COUNTRY_PATH=str(TEST_DIR/"test_dataset/hierarchies/country.csv")
RACE_PATH=str(TEST_DIR/"test_dataset/hierarchies/race.csv")