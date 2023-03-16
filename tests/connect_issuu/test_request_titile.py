import pytest
import os
import sys
test_folder = os.path.abspath(__file__)
project_folder = os.path.abspath(os.path.join(__file__ ,"..\..\.."))
script_folder = os.path.join(project_folder,"scripts")
sys.path.insert(0,script_folder)
from issuu import request_title, request_title_date
from time import mktime
from datetime import datetime as dt


@pytest.fixture
def pdf_url():
    return [

        "https://issuu.com/mediahawkesbaylimited/docs/nz_manufacturer_march_23",
        "https://issuu.com/forestandbird/docs/f_b_mag_382_summer_2021",
        "https://issuu.com/devonportflagstaffnewspaper/docs/issuu_rangiobserver_17feb2023"
    ]

def test_request_title(pdf_url):
    expected_titles = [

        "NZ Manufacturer March 2023",
        "Forest & Bird Magazine Issue 382 Summer 2021",
        "17 February 2023 Rangitoto Observer"
    ]
    for i, url in enumerate(pdf_url):
        assert request_title(url) == expected_titles[i]

def test_request_title_date(pdf_url):
    expected_titles = [

        "NZ Manufacturer March 2023",
        "Forest & Bird Magazine Issue 382 Summer 2021",
        "17 February 2023 Rangitoto Observer"
    ]
    expected_published = [

        "Mar 12, 2023",
        "Nov 17, 2021",
        "Feb 17, 2023"
    ]
    expected_published_stamp = [dt.strptime(el, "%b %d, %Y").strftime("%Y-%m-%dT%H:%M:%S.000Z") for el in expected_published ]

    for i, url in enumerate(pdf_url):
        actual_title, actual_published, actual_published_stamp = request_title_date(url)
        assert actual_title == expected_titles[i]
        assert actual_published == expected_published[i]
        assert actual_published_stamp == expected_published_stamp[i]

