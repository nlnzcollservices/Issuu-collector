Summary

This tool is designed to collect pdf files from https://issuu.com/ platform specifically for organizational environment. 
It is identifying last issue preserved and collecteing all the issues
after the last which was found in Alma, making SIPs, moving it to Rosetta folder, making items in Alma, saving information about processed materails
 and reporting not available or not collected issues.

Written on python3.9 (should be compatible with earlier versions)
for  Win10 platform

It consistes from 
Scripts:
 "issuu.pu" - main script
 "issuu_dict.py" - editable file which contains information about each publication
 "my_settings.py"  -  and settings  file

to do:
 Email notification
 Memorizing and reading document names not used for the process
 Tool for time gaps inside one publication
 Tests - doing.

Notes

Design notes:

issuu.py

Classes:

class ItemMaker():
  Methods:
	def __init__(self)
	def check_item_in_the_system(self)
`       def item_routine(self)

class SIPMaker():
  Methods:
	def __init__(self):
        def make_SIP(self)

Functions:
 main():
 harvester_routine()
 parse_final_dictionary()
 download_wait()
 sip_checker()



1. Script is iterating trough dictionaries in "issuu_dict.py".
2. Calls for the last Alma representation via "last_representation_getter.py"
3. Uses selenium and web-driver to grab last publications docnames and aws docnames from publisher page.
4. Parses document names to identify particular publiscation and possibly date based on rules
5. Constructs link to particular issue and makes request for title, if date was not identified on previous stage
6. Compares date of issue with the last preserved and all collected by script and produces dictionary with document names to collect.
7. Collects all the publications which are satisfied with the conditions to the temporary folder and write notes for those which were not collected.
8. Makes SIP from each file
9. Makes item, writes to item report
10. Writes descriptions collected for each issue for script use.
11. Cleans the temporary folder and goes for next publication
12. Checks all SIPs for particular publication, moves them to Rosetta folder 
to do:
(13. Should send notification about not collected issue to assigned people)

The design allows to add new rules for new titles from issuu platform to harvester_routine function and for future developing add emailing and gaps idetification tools.
It is not currently designed to identified gaps between preserved materials.

2. dictionary.py
Contains dictionary of dictionaries with information about each publication in the following format

Dictionary format:
     {...,<publication name>:{"publisher":<publisher_name>","mms_id":<mms_id>,"po_line":<pol_number>, "holding_id":<holdings_id>, "pattern":<pattern>, "days":<days>, "url":<all publication by publisher url>, "username":<user name from url,...}
Example:
     {...,"Weekend Sun":{"publisher":	"Sun Media","web_title":"The Weekend Sun", "mms_id":"9915789603502836","holding_id":"22183434080002836","po_line":"286240-ilsdb","suppements":True, "pattern":"predictive", "days":None,"url":"https://issuu.com/sunmedia","username":"sunmedia"},...}

"publisher name" and "web_title" are currently not in use however potentially could be applicable during title parsing.
"pattern" and "days" are also given for informative purpose but potentially could be used for "gap" identification

3.my_settings.py


Scope notes:
	The scope of collecting  are all the magzines which have dictionary in dictionary.py file
	The scope for publication  all the publiction identified with Issuu search API ( http://search.issuu.com/api/2_0)and published after the last preserved publication.
Content notes:
	The project consists fro the following folders:
	-script
	-assets----|
		   |templates
	-reports
	-temp_files
        -SIP

Dependances:
 "alma_tools.py" - Alma API handler
  "description_maker.py" - Bulk ingester tool script to make description
  "last_representation_getter.py" (parse_date_design_label) - Parsing labels from Alma digital representation instances for digital magazines
  "geckodriver.exe" - web driver 
Note:

   Selenium is working with FireFox webdriver geckodriver https://github.com/mozilla/geckodriver/releases. (It also could be set to work with a Chrome webdriver https://chromedriver.chromium.org/downloads with on Virtual Box)
   Pyatogui is currently in use to preform "Save as" mouse click, as FireFox profile could not be set to save files without showing pop up windows in the current system. It is posible to set it in Oracle VB, but in this case would not be direct connection to Rosetta foldr(only if to set as shared folder Rosetta Cascade folder)
