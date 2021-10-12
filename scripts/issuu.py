import os
import re
import time
import sys
import wget
import requests
import urllib
import shutil
import dateparser
import pyautogui
import keyboard
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from time import mktime, sleep
from selenium import webdriver
from sys import platform
from selenium.common import exceptions
from rosetta_sip_factory.sip_builder import build_sip
from description_maker import make_description
import description_maker
from issuu_dict import issuu_dict
from my_settings import sip_folder, temp_folder,report_folder, template_folder,logging, rosetta_folder, seas_dict, months, reversed_season, months_dictionary
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\waterford\scripts')
import last_representation_getter
import send_email



fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.helperApps.alwaysAsk.force", False)
fp.set_preference("browser.download.dir", temp_folder)
fp.set_preference("browser.download.useDownloadDir",True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
fp.set_preference("pdfjs.disabled",True)
fp.set_preference("browser.download.manager.showWhenStarting",False)
driver = webdriver.Firefox(firefox_profile=fp)

logger = logging.getLogger(__name__)
base_url = r"https://issuu.com/"
search_url = r"http://search.issuu.com/api/2_0/document"
# page_url = r"https://image.isu.pub/"
# page_url_part2 = "/jpg/page_"
pdf_url_part2 =r"/docs/"
key = "prod"


year_now =dt.now().strftime('%Y')
last_year =str(int(dt.now().strftime('%Y'))-1)

# http://search.issuu.com/api/2_0/document?username=username&pageSize=20&startIndex=20
class ItemMaker():

	"""This Class is making items for Waterford press"""
	def __init__(self):
		self.item_check = None
	
	def check_item_in_the_system(self, pub_name,description):

		"""This method checks if item is in Alma already
		Parameters:
			pub_name (str) - name of publication
			description (str) - for "description" field
		Returns:
			bool - True, if item found,False otherwise
		"""
		my_alma = AlmaTools(key)
		my_alma.get_items(issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"])
		total_count = int(re.findall(r'<items total_record_count="(.*?)"', my_alma.xml_response_data)[0]) 
		if total_count !="0":
			for ind in range(0, round(total_count+49,-2),100):
				my_alma.get_items(issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"],{"limit":100, "offset":ind})
				descriptions = re.findall(r"<description>(.*?)</description>", my_alma.xml_response_data)
				# print(descriptions)
				# print(description)
				# # v. 27, 1 (2021)
				# # v. 27, iss. 1 (2021)
				# print(description  in descriptions)
				if description in descriptions:
					self.item_check = True
					return True
				elif description.replace(",",", iss.") in descriptions:
					self.item_check = True
					return True
		return False


	def item_routine(self, pub_name, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, description ):
		"""

		Main function for making Alma item record with existing template and parameters, writes down report and prints item_id
		Parameters:
			pub_name (str) - magazine name
			enum_a (str) - enumeration a
			enum_b (str) - enumeration b
			enum_c (str) - enumeration c
			chron_i (str) - chronology i
			chron_j (str) - chronology j
			chron_k (str) - chronology k
			description (str) - description
		Returns:
			None


		"""
		print("#"*50)
		print(pub_name)
		if not self.check_item_in_the_system(pub_name, description):
			chron_i_stat = "<chronology_i></chronology_i>"
			chron_j_stat = "<chronology_j></chronology_j>"
			chron_k_stat = "<chronology_k></chronology_k>"
			enum_a_stat = "<enumeration_a></enumeration_a>"
			enum_b_stat = "<enumeration_b></enumeration_b>"
			enum_c_stat = "<enumeration_c></enumeration_c>"
			polstring = "<po_line>{}</po_line>".format(issuu_dict[pub_name]["po_line"])
			description_stat = "<description>{}</description>".format( description )
			if chron_i:
				chron_i_stat = "<chronology_i>{}</chronology_i>".format( chron_i )
			if chron_j:
				chron_j_stat = "<chronology_j>{}</chronology_j>".format( chron_j )
			if chron_k:
				chron_k_stat = "<chronology_k>{}</chronology_k>".format( chron_k )
			if enum_a:
				enum_a_stat = "<enumeration_a>{}</enumeration_a>".format( enum_a )
			if enum_b:
				enum_b_stat = "<enumeration_b>{}</enumeration_b>".format( enum_b)
			if  enum_c:
				enum_c_stat = "<enumeration_c>{}</enumeration_c>".format( enum_c)
			time_substitute_statement = "<creation_date>{}</creation_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
			receiving_stat = "<arrival_date>{}</arrival_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
			holding_stat = "<holding_id>{}</holding_id>".format(issuu_dict[pub_name]["holding_id"])
			with open(os.path.join(template_folder,"item.xml"), "r") as data:
					item_data = data.read()
					item_data = item_data.replace("<creation_date></creation_date>", time_substitute_statement)
					item_data = item_data.replace("<po_line></po_line>", polstring )
					item_data = item_data.replace("<enumeration_a></enumeration_a>", enum_a_stat )
					item_data = item_data.replace("<enumeration_b></enumeration_b>", enum_b_stat )
					item_data = item_data.replace("<enumeration_c></enumeration_c>", enum_c_stat )
					item_data = item_data.replace("<chronology_i></chronology_i>", chron_i_stat )
					item_data = item_data.replace("<chronology_j></chronology_j>", chron_j_stat )
					item_data = item_data.replace("<chronology_k></chronology_k>", chron_k_stat )
					item_data = item_data.replace("<description></description>", description_stat )
					item_data = item_data.replace("<holding_id></holding_id>", holding_stat )
			logger.info("Creating item")
			my_alma = AlmaTools(key)
			#print(item_data)
			my_alma.create_item_by_po_line(issuu_dict[pub_name]["po_line"], item_data)
			logger.info(my_alma.xml_response_data)
			logger.debug(my_alma.status_code)
			item_grab = bs(my_alma.xml_response_data, "lxml-xml")
			item_pid  = item_grab.find('item').find( 'item_data' ).find( 'pid' ).string 
			logger.info(item_pid + " - item created")		
			
			report_name = "report_items"+str(dt.now().strftime("_%d%m%Y"))+".txt"

			with open(os.path.join(report_folder, report_name),"a") as f:
				f.write("{}|{}|{}|{}|{}".format(pub_name, description, issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"], item_pid))
				f.write("\n")		


class SIPMaker():


# Volume = dcterms:bibliographicCitation
# Issue = dcterms:issued
# Number = dcterms:accrualPeriodicity
# Year = dc:date
# Month = dcterms:available
# Day = dc:coverage


	def __init__(self, pub_name, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k,description, file_folder_place ):

		"""This class is used for making SIPs from existing foler
		Parameters:
			pub_name (str) - magazine name
			enum_a (str) - enumeration a
			enum_b (str) - enumeration b
			enum_c (str) - enumeration c
			chron_i (str) - chronology i
			chron_j (str) - chronology j
			chron_k (str) - chronology k
			description (str) - description
		Returns:
			None

	"""

		
		self.flag = False
		self.pub_name = pub_name
		self.enum_a = enum_a
		self.enum_b = enum_b
		self.enum_c = enum_c
		self.chron_i = chron_i
		self.chron_j = chron_j
		self.chron_k = chron_k
		self.description = description
		print(description)
		print("description")
		self.file_folder_place = file_folder_place
		self.make_SIP()


	def make_SIP(self):
			"""Method is used for making SIPs from description information

			Returns:
				bool  - True, if built, False otherwise
			"""
			logger.info("Making sips")
			
			self.output_folder = os.path.join(sip_folder, self.pub_name.replace(" ","_") + "_"+self.description.replace(" ","").replace(".","_").replace("(","-").replace(")","-").replace(",","-").rstrip("-").rstrip("_"))
			print(self.file_folder_place)
			print(self.output_folder)
			try:
				build_sip(
									
									ie_dmd_dict=[{"dc:date":self.chron_i, "dcterms:available":self.chron_j, "dcterms:issued":self.enum_c, "dc:coverage":self.chron_k,"dcterms:bibliographicCitation":self.enum_a,  "dc:title":self.pub_name,"dcterms:accrualPeriodicity":self.enum_b, "dcterms:bibliographicCitation":self.enum_a}],
									pres_master_dir=self.file_folder_place,
									generalIECharacteristics=[{"IEEntityType":"PeriodicIE"}],
									objectIdentifier= [{"objectIdentifierType":"ALMAMMS", "objectIdentifierValue":issuu_dict[self.pub_name]["mms_id"]}],
									accessRightsPolicy=[{"policyId":"100"}],
									input_dir=self.file_folder_place ,
									digital_original=True,
									sip_title=self.pub_name+"_"+self.description,
									output_dir=self.output_folder 
								)
				print('Done')

				report_name = "report_sips"+str(dt.now().strftime("_%d%m%Y"))+".txt"
				with open(os.path.join(report_folder, report_name),"a") as f:
					f.write("{}|{}|{}".format(self.pub_name,issuu_dict[self.pub_name]["mms_id"], self.description))
					f.write("\n")
				self.flag =  True


			except Exception as e:
				print(str(e))
				logger.error(str(e))


def sip_checker(sippath):

	"""Checks if met files are empty, or no_file
		Parameters:
		sippath(str) - path to sip
		Returns:
		flag(bool) - True if error found.  False if size of file is wrong or audio file or met file are empty.
	"""
	flag = False

	if os.path.getsize(os.path.join(sippath, "content", "mets.xml")) == 0:
		logger.info("Attention - empty met! {} ".format(sippath))
		flag = True
	if os.path.getsize(os.path.join(sippath, "content", "dc.xml")) == 0:
		logger.info("Attention - empty  dc met! {}".format(sippath))
		flag = True
	if len(os.listdir(os.path.join(sippath,  "content", "streams"))) == 0:
		logger.info("Attention - no file! {}".format(sippath))
		flag = True
	if len(os.listdir(os.path.join(sippath,  "content", "streams"))) >1:
		logger.info("Attention - more then 1 file in the! {}".format(sippath))
		flag = True
	if len(os.listdir(os.path.join(sippath,  "content"))) == 0:
		logger.info("Attention - streem folder! {}".format(sippath))
		flag = True
	else:
		myfilepath = os.path.join(sippath, "content", "streams", os.listdir(os.path.join(sippath,  "content", "streams"))[0])
		if os.path.getsize(myfilepath) == 0:
				logger.info("Attention - 0 byte file! {}".format(myfilepath))
				flag = True				
	return flag

			# 	self.flag = False
# def title_parser(title,web_title,issuu):

# 	"""Parses title from web
# 	Parameters:
# 		title(str) - title which comes from web
# 	Returns:

# 		dict - contains "volume","issue","season","day","month","year" keys

# 	"""
# 	month = None
# 	day=None
# 	issue=None
# 	year = None
# 	my_date= None
# 	season=None
# 	months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
# 	my_title_list = title.split(" ")
# 	print(my_title_list)

# 	for i,el in enumerate(my_title_list):
# 		print(el)
# 		if el == "Issue":
# 			issue = my_title_list[i+1]
# 	for i,el in enumerate(my_title_list):
# 		if "." in el:
# 			try:
# 				my_date = dateparser.parse(el)
# 				print(my_date)
# 			except:
# 				pass
# 		if my_date:
# 			print("here")
# 			month = my_date.strftime("%B")
# 			year = my_date.strftime("%Y")
# 			day = my_date.strftime("%d")
# 	for i,el in enumerate(my_title_list):
# 		if el in months:
# 			month = str(el)
# 	for i,el in enumerate(my_title_list):
# 		try:
# 			year_list = re.findall(r"\d\d\d\d", el)
# 			if len(year_list) == 1:
# 				year = year_list[0].lstrip(" ").rstrip(" ")
# 		except Exception as e:
# 			print(str(e))
# 	for i,el in enumerate(my_title_list):
# 		if "th" in el or "nd" in el or "rd" in el:
# 			day = el.rstrip("th").rstrip("nd").rstrip("rd")
# 	for i,el in enumerate(my_title_list):
# 		day_re= re.findall(r"\d{1,2}",el.split(year)[-1])
# 		if len(day_re) == 1:
# 			day=day_re[0]
# 			if day == issue:
# 				day = None

# 	return{"issue":issue,  "season":season, "day":day,"month_string": month,"year":year}


def download_wait(path_to_downloads):

    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 2000:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('part'):
                dl_wait = True
        seconds += 1
    return seconds

def parse_final_dictionary(final_dict):

		"""Converts dictionary from designation from web title to enumeration and chronology
		Parameters:
			final_dict (dict) - dictionary from parsed web title
		Returns:
			enum_a (str) - enumeration a
			enum_b (str) - enumeration b
			enum_c (str) - enumeration c
			chron_i (str) - chronology i
			chron_j (str) - chronology j
			chron_k (str) - chronology k
		"""

		months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
		print(final_dict)
		enum_a = None
		enum_b = None
		enum_c = None
		chron_i = None
		chron_j = None
		chron_k = None
		if "season" in final_dict.keys():
			chron_j = final_dict["season"]
		if not chron_j and "month" in final_dict.keys():
			chron_j = final_dict["month"]
		if not chron_j and "month_string" in final_dict.keys() and final_dict["month_string"]:
			chron_j=str(months.index(final_dict["month_string"])+1).zfill(2)
		if "year" in final_dict.keys():
			chron_i  = final_dict["year"]
		if "volume" in final_dict.keys():
			enum_a = final_dict["volume"]
		if "issue" in final_dict.keys():
			enum_c = final_dict["issue"]
		if not enum_c and "number" in final_dict.keys():
			enum_b = final_dict["number"]
		if "day" in final_dict.keys():
			chron_k = final_dict["day"]

		return enum_a, enum_b, enum_c, chron_i, chron_j, chron_k

def harvester_routine(issuu):

	"""Main harvester which is taking metadata from issuu search API and combines it to images link, downloads images,
	checks them, makes SIPs and makes items
	Parameters:
		issuu(str) - publication name
	"""
	logger.info("Harvesting "+ issuu)
	try:
		alma_last_representation_list = last_representation_getter.last_repres_getter(issuu_dict[issuu]["mms_id"], issuu,False)
	except:
		alma_last_representation_list = [mktime(dt.fromtimestamp(0).timetuple()),0]
	if not alma_last_representation_list:
		alma_last_representation_list = [mktime(dt.fromtimestamp(0).timetuple()),0]
	logger.info("Last issue preserved on:")
	logger.info(alma_last_representation_list[1])
	username = issuu_dict[issuu]["username"]
	params = {"username":username,"pageSize":"100"}
	r = requests.get(search_url,params = params)
	#logger.setLevel("DEBUG")
	logger.debug(r.text)
	my_dates = []
	try:
		with open(os.path.join(report_folder,issuu + ".txt"),"r")as f:
			data = f.read()
		for el in data.split("\n")[:-1]:
			my_dates.append(el)
	except Exception as e:
		print(str(e))
	if my_dates !=[]:
		print('Already harvested:')
		print(my_dates)

	my_docnames = []
	try:
		with open(os.path.join(report_folder,issuu + "_worked_out.txt"),"r")as f:
			data = f.read()
		for el in data.split("\n")[:-1]:
			my_docnames.append(el)
	except Exception as e:
		print(str(e))
	if my_docnames !=[]:
		print('Already in system:')
		print(my_docnames)
	for el in os.listdir(temp_folder):
		os.remove(os.path.join(temp_folder,el))


	my_json = r.json()
	num_found = my_json["response"]["numFound"]
	my_dict_list = []
	my_dict = {}
	for ind in range(int(num_found)//100+2):
		start_index = ((int(num_found)//100)-ind)*100
		params["startIndex"]=start_index
		r = requests.get(search_url, params)
		my_doc_json = r.json()["response"]["docs"]
		logger.debug(my_doc_json)
		for doc in my_doc_json:

			if not doc in my_docnames:

				my_dict={}
				web_title = ""
				flag_ses = False
				issue = None
				volume = None
				number = None
				year = None
				month = None
				my_design = None
				year = None
				season = None
				my_date = None
				# print(doc["docname"])
				pdf_url = base_url+issuu_dict[issuu]["username"]+pdf_url_part2+doc["docname"]
				if issuu in ['Active retirees']:
					if "active" in doc["docname"] and "retirees" in doc["docname"] and not doc["docname"] in my_docnames:
						print(doc["docname"])
						print(pdf_url)
						r=requests.get(pdf_url)
						my_soup = bs(r.text,"lxml")
						web_title = my_soup.find_all("h1")[0].text
						print(web_title)
						title = web_title.replace("Active Retirees New Zealand Magazine","").replace("Active Retirees Digital Magazine","")
						try:
							year= re.findall('\d{4}', title)[0].rstrip(" ")
							title.replace(year,"")
						except:
							year= re.findall('\d{4}', doc["docname"])[0].rstrip(" ")
						print(year)
						month_seas = title.lstrip(" ").split(" ")[0]
						print(month_seas)
						if month_seas in months:
							month = month_seas
						elif month_seas in seas_dict.keys():
							month_string = seas_dict[month_seas]
							month = months_dictionary[month_string]
							flag_ses = True
							print(month)
						else:
							quit()
						print("01 "+ month + " "+ title)
						my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
						print(my_date)
				if issuu in ["Explore Dunedin"]:# {'publisher': 'Allied Press Ltd', 'web_title': 'Explore Dunedin \xa0', 'mms_id': '9919061063502836', 'holding_id': '22366692760002836', 'po_line': 'POL-167410', 'pattern': '', 'days': '', 'url': 'https://issuu.com/alliedpress/docs/exploredunedin2020', 'username': 'exploredunedin2020'},"]
					if "exploredunedin" in doc["docname"] and not doc["docname"] in my_docnames:
						my_date = dateparser.parse("01 01 "+ doc["docname"].replace("exploredunedin",""))

				if issuu in ["Ponsonby news"]:
					if "ponsonby_news_" in doc["docname"] and not doc["docname"] in my_docnames:
						web_date = doc["docname"].replace("ponsonby_news_","").replace("_website","").replace("_"," ")
						my_date = dateparser.parse("01 "+web_date, settings={'DATE_ORDER': 'DMY'})
						print(my_date)
	
				if issuu in ["Taranaki farming lifestyles"]:
					if "tfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("tfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Taranaki farming lifestyles, ",""))

		
				if issuu in ["Hawke's Bay farming lifestyles"]:
					if "hbfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("hbfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Hawke's Bay farming lifestyles ",""))

				if issuu in ["Northern farming lifestyles"]:
					if "nfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("nfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Northern Farming Lifestyles, ",""))



				if issuu in ["Waikato farming lifestyles"]:
					if "wfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("wfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Waikato farming lifestyles ",""))

		
				if issuu in ["Hawke's Bay farming lifestyles"]:
					if "hbfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("hbfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Hawke's Bay farming lifestyles ",""))

				if issuu in ["Northern farming lifestyles"]:
					if "nfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("nfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Northern Farming Lifestyles, ",""))

				if issuu in ["The weekend lifestyler"]:
					if "wl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("wl_",""),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("The Weekend Lifestyler ",""))
				if issuu in ["Manawatu farming lifestyles"]:
					if "mfl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("mfl_","01"),settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Manawatu Farming Lifestyles, ",""))
				if issuu in ["Education Gazette"]:
					#print(doc["docname"])
					r = requests.get(pdf_url)
					my_soup = bs(r.text, "lxml")
					web_title = my_soup.find_all("h1")[0].text
					print(web_title)
					my_vol_num = re.sub("[A-Za-z]", "", web_title).rstrip(" ").lstrip(' ')
					try:
						volume = my_vol_num.split(".")[0]
						number = my_vol_num.split('.')[1]
						if not number.isdigit() and " " in number:
							number = number.split(" ")[0]
						my_date=0
						my_design = description_maker.make_description(volume, number, None, None, None, None)
					except:
						with open('to_process_manually.txt',"a") as f:
							f.write(issuu+"|"+web_title+pdf_url)
							f.write("\n")

						my_date=None
					#print(my_date)	
				if issuu in ["Waimea Weekly"]:
					if "ww" in doc["docname"] and not "rural" in doc["docname"]and not "0219" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("ww","").rstrip("_-"),settings={'DATE_ORDER': 'MDY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							if year_now in web_title or last_year in web_title:
								my_date=dateparser.parse(web_title)
							# if not my_date:
							# 	print(web_title)
							# 	quit()
				if issuu in ["Dressage NZ Bulletin"]:
					r=requests.get(pdf_url)
					my_soup = bs(r.text,"lxml")
					web_title = my_soup.find_all("h1")[0].text
					#print(web_title)
					my_pub = web_title.lstrip("Dressage NZ Bulletin").lstrip("DressageNZ Bulletin").lstrip( )
					if "Issue" in my_pub:
						issue = my_pub.split(' ')[1]
						my_date = dateparser.parse("1 "+" ".join(my_pub.split(' ')[2:]))
						print(my_pub)
						print(my_date)
						print(issue)
				if issuu in ["Weekend Sun"]:
					#print('Please wait, "Weekend sun" takes more time....')
					if doc["docname"].startswith("ws") and (year_now[2:] in doc["docname"] or last_year[2:] in doc["docname"]):
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							if "the weekend sun" in web_title.lower() and (year_now in web_title or last_year in web_title):
								my_date = dateparser.parse(web_title.lower().replace("the weekend sun","").lstrip('- '))
							# if "ws" in web_title.lower():
							# 	print(pdf_url)
				if issuu in ["Kaipara Lifestyler"]:
					if "kl" in doc["docname"]:
						my_date = dateparser.parse(doc["docname"].replace("kl_",""),settings={'DATE_ORDER': 'MDY'})
						if not my_date:
							r=requests.get(pdf_url)
							my_soup = bs(r.text,"lxml")
							web_title = my_soup.find_all("h1")[0].text
							my_date=dateparser.parse(web_title.replace("Kaipara Lifestyler, ",""))
				if issuu in ["Guardian – Motueka"]:
					my_date = dateparser.parse(doc["docname"])
					if not my_date:
						r=requests.get(pdf_url)
						my_soup = bs(r.text,"lxml")
						web_title = my_soup.find_all("h1")[0].text
						my_date =dateparser.parse(web_title)
				if issuu in ["Geraldine news"]:
					# if "12pp" in doc["docname"]:
					# 	doc["docname"]=doc["docname"].split("12pp")[0]
					api_date = re.sub("[A-Za-z]", "", doc["docname"])
					api_date=api_date.rstrip("_").rstrip('_-').lstrip("_")
					if "-" in api_date:
						api_date = api_date.split("-")[0]
					if  "_" in api_date:
						api_date = api_date.split("_")[0]

					my_date = dateparser.parse(api_date,settings={'DATE_ORDER': 'MDY'})
					if "12pp" in doc["docname"]:
						r=requests.get(pdf_url)
						my_soup = bs(r.text,"lxml")
						web_title = my_soup.find_all("h1")[0].text
						my_date=dateparser.parse(web_title.replace("GNews ",""))


					# if "ww" in doc["docname"] and "2021" in doc["docname"] and not "rural" in doc["docname"]:
				# 	logger.debug(doc["docname"])
				# 	my_date = dateparser.parse(" ".join(doc["docname"].split('_')[0:3]))
				# 	logger.debug(my_date)
				# 	my_date_stamp = mktime(my_date.timetuple())
				if my_date or my_date==0:
					if my_date!=0:
						logger.debug(my_date.strftime("%d %B %Y"))
						my_date_stamp = mktime(my_date.timetuple())
						if (my_date_stamp > alma_last_representation_list[0] and my_date.strftime("%d %B %Y") not in my_dates):# or issuu=="Education Gazette":
								my_dict["docname"] =doc["docname"]
								my_dict["document_id"] = doc["documentId"]
								my_dict["url"]=pdf_url
								my_dict["web_title"]=web_title
								my_dict["season"] = season
								my_dict["date"] = my_date.strftime("%d %B %Y")
								my_dict["year"]=my_date.strftime("%Y")
								my_dict["month"]=my_date.strftime("%B")
								my_dict["day"] = my_date.strftime("%d")
								my_dict["my_date_stamp"] = my_date_stamp
								my_dict["issue"] = issue
								my_dict["volume"] = None
								my_dict["number"] = None
								if issuu in ["Active retirees","Taranaki farming lifestyles","Waikato Farming Lifestyle","Hawke's Bay farming lifestyles","Northern farming lifestyles", "Dressage NZ Bulletin","Manawatu farming lifestyles","Ponsonby news","Explore Dunedin"]:
									my_dict["day"]=None
								if issue in ["Explore Dunedin"]:
									my_dict["month"] = None
								if issue in ["Active retirees"]:
									if flag_ses:
										my_dict["month"] = None
										my_dict["season"] = reversed_season["month"]

					else:
						if my_design not in my_dates:
								my_dict["docname"] =doc["docname"]
								my_dict["document_id"] = doc["documentId"]
								my_dict["url"]=pdf_url
								my_dict["web_title"]=web_title
								my_dict["season"] = season
								my_dict["date"] = None
								my_dict["year"]=None
								my_dict["month"]=None
								my_dict["day"] = None
								my_dict["my_date_stamp"] = None
								my_dict["issue"] = None
								my_dict["volume"] = volume
								my_dict["number"] = number
					if not my_dict in my_dict_list and my_dict !={}:
						my_dict_list.append(my_dict)
	print(my_dict_list)
	for i,pub in enumerate(my_dict_list):
		print(pub)
		flag_to_do = False
		r=requests.get(pub["url"])
		if pub["web_title"]=="":
			my_soup = bs(r.text, "lxml")
			web_title = my_soup.find_all("h1")[0].text
			my_dict_list[i]["web_title"] = web_title
		driver.get(pub["url"])		
		sleep(10)
		try:
			driver.find_element_by_id("CybotCookiebotDialogBodyButtonAccept").click()
		except Exception as e:
			print(str(e))
		try:
			driver.find_element_by_xpath("//button[contains(@aria-label, 'Download')]").click()
			sleep(20)
			pyautogui.moveTo(1720,980)
			pyautogui.move(1,1)
			pyautogui.click()
			sleep(10)
			#pyautogui.hotkey('enter')
			if len(os.listdir(temp_folder))!=1:
				try:
					pyautogui.hotkey('tab')
					pyautogui.hotkey('tab')
					pyautogui.hotkey('tab')
					pyautogui.hotkey('tab')
					pyautogui.hoftkey('enter')
				except:
					pass
			seconds =download_wait(temp_folder)
			print("Downloading process took",seconds, "seconds")
		except exceptions.NoSuchElementException:
			with open(os.path.join(report_folder,"download_not_enabled_by_publisher.txt"),"a") as f:
				f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
				f.write("\n")
			with open(os.path.join(report_folder,"docnames_not_enabled_by_publisher.txt"),"a") as f:
				f.write(pub["docname"])
				f.write("\n")
		for fname in os.listdir(temp_folder):
			if not fname.endswith('part'):
				flag_to_do = True
		if len(os.listdir(temp_folder))==1 and flag_to_do:
			enum_a, enum_b, enum_c, chron_i, chron_j, chron_k=parse_final_dictionary({"issue":pub["issue"], "volume":pub["volume"], "number":pub["number"],"season":pub["season"],"day":pub["day"],"month_string": pub["month"],"year":pub["year"]}) 
			my_design = description_maker.make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
			print(my_design)
			print(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
			my_sip = SIPMaker(issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design, temp_folder)
			if my_sip.flag:
				for el in os.listdir(temp_folder):
							os.remove(os.path.join(temp_folder,el))
				my_item = ItemMaker()
				my_item.item_routine( issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design)
				if pub["date"]:
					with open(os.path.join(report_folder,issuu+".txt"),"a") as f:
						f.write(pub["date"])
						f.write("\n")
				else:
					with open(os.path.join(report_folder,issuu+".txt"),"a") as f:
						f.write(my_design)
						f.write("\n")
				with open(os.path.join(report_folder, issuu+"_worked_out.txt"),"a") as f:
					f.write(pub["docname"])
					f.write("\n")
def main():

	for issuu in issuu_dict:
		harvester_routine(issuu)
		sips_number = len(os.listdir(sip_folder))
		for sip in os.listdir(sip_folder):
			sippath = os.path.join(sip_folder,sip)
			sip_error_flag = sip_checker(sippath)
			if not sip_error_flag:
				shutil.move(sippath, rosetta_folder)
			else:
				quit()
		logger.info(str(sips_number)+' sips moved to '+rosetta_folder)
	with open(os.path.join(report_folder,"download_not_enabled_by_publisher.txt"),"r") as f:
		data = f.read()

	#send_email.send_email(data)
	driver.close()


if __name__ == "__main__":
	main()
