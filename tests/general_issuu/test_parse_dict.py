import pytest
import os
import sys
test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from issuu import parse_final_dictionary



def test_parse_final_dictionary():
    # Test case 1
    final_dict = {"season": "Summer", "year": "2022", "volume": "5", "issue": "10","number": None ,"term":None }
    expected_output = ("5", None, "10", "2022", "Summer", None)
    assert parse_final_dictionary(final_dict) == expected_output

    # Test case 2
    final_dict = {"season": None, "volume": None, "issue": None, "term": "One", "year": "2021", "number": "50"}
    expected_output = (None, "50", None,  "2021","One", None)
    assert parse_final_dictionary(final_dict) == expected_output

    # Test case 3
    final_dict = {"month": "03", "year": "2023", "day": "16","season": None, "volume": None, "issue": None,"number":None, "term":None}
    expected_output = (None, None, None, "2023", "03", "16")
    assert parse_final_dictionary(final_dict) == expected_output

    # Test case 4
    final_dict = {"month_string": "April", "year": "2022", "volume": "8","issue": None,"number":None, "month":"04","term":None,"season": None}
    expected_output = ("8", None, None, "2022", "04", None)
    assert parse_final_dictionary(final_dict) == expected_output


