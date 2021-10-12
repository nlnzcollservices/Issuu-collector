# ISSUU
## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Collaboration and integration](#collaboration-and-integration)
5. [FAQs](#faqs)
## General Info
***
The script is collecting pdfs from Issuu platform. Foo detailed information read ["Technical_notes.txt"](/documentation/Technical_notes.txt)
### Pipeline
![Issuu](/documentation/Issuu.png)
## Technologies
***
A list of technologies used within the project:
* [Python](https://www.python.org/downloads/release/python-370/): Version  3.7.2 
* [Rosetta sip factory](https://github.com/NLNZDigitalPreservation/rosetta_sip_factory): Version 0.1.9
* [beautifulsoup4](https://https://www.crummy.com/software/BeautifulSoup/bs4/doc/): Version 4.9.1
* [configparser](https://docs.python.org/3/library/configparser.html): Version 5.0.0
* [dateparser](https://pypi.org/project/dateparser/): Version 0.7.6
* [lxml](https://pypi.org/project/lxml/): Version 4.5.2
* [requests](https://pypi.org/project/requests/): Version 2.24.0
* [description_maker](https://github.com/nlnzcollservices/bulk_item_ingester/tree/master/tools/description_maker.py)
* [alma_tools](https://github.com/nlnzcollservices/Alma-tools/alma_tools_v2.py)
* [last_representation_getter](https://github.com/nlnzcollservices/last_representation_getter/last_representation_getter.py)
## Installation
***

Clone the repository from GitHub. 
```
$ git clone https://github.com/nlnzcollservices/issuu_collecting
```
Enter the documentation directory
```
$ cd issuu/documentation
```
Install requirements.txt
```
$ pip install requirements.txt
```
Enter the scripts directory
```
$ cd ..
$ cd issuu/scripts
```
Open settings.py for editing (for cmd)
```
$ notepad settings.py
```
Change all the full paths to yours

Folders where Exlibris Rosetta takes the SIPs from production and sandbox in the setting paths section
```
rosetta_folder = r"your\production\Rosetta\path"
rosetta_sb_folder = r"your\sandbox\Rosetta\path"
```
Folder with secrets in credentials section
```
secrets_and_credentials_fold = r'path\to\your\secret\folder'
```
Save it, close and run. (It will create a project folder tree)
```
$ python settings.py
```
Move modified with your keys for Alma and Google Sheets secret file to  "path\to\your\secret\folder"
```
$ cd ..
$ move secrets "path\to\your\secret\folder"

```

Cross fingers and run!
```
$ python issuu.py
```
## Collaboration and integration

Read ["Technical_notes.txt"](/documentation/Technical_notes.txt) TODO section
