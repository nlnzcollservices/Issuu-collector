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
from sys import platform
from rosetta_sip_factory.sip_builder import build_sip
from description_maker import make_description
import description_maker
from issuu_image_dict import issuu_dict
from my_settings import sip_folder, to_send_email, file_folder, email_address_line, report_folder_images, template_folder,logging, rosetta_folder, seas_dict, term_dict, months, reversed_season, months_dictionary,short_month_dict, not_processed_files

sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools
from email_maker import Gen_Emails
#sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\waterford\scripts')
import last_representation_getter
import send_email

from selenium import webdriver
from selenium.webdriver.common.by import By
from sys import platform
from selenium.common import exceptions
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)
print("Firefox Headless Browser Invoked")



logger = logging.getLogger(__name__)
base_url = r"https://issuu.com/"
search_url = r"http://search.issuu.com/api/2_0/document"
page_url = r"https://image.isu.pub/"
page_url_part2 = "/jpg/page_"
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
			# print(my_alma.xml_response_data)
			logger.info(my_alma.xml_response_data)
			logger.debug(my_alma.status_code)
			item_grab = bs(my_alma.xml_response_data, "lxml-xml")
			item_pid  = item_grab.find('item').find( 'item_data' ).find( 'pid' ).string 
			logger.info(item_pid + " - item created")		
			
			report_name = "report_items"+str(dt.now().strftime("_%d%m%Y"))+".txt"

			with open(os.path.join(report_folder_images, report_name),"a") as f:
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
		self.pref=""
		if self.pub_name in ["Asset"]:
			self.pref = "innz-"
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
			logger.info(self.output_folder)
			try:
				build_sip(
									ie_dmd_dict=[{"dc:date":self.chron_i, "dcterms:available":self.chron_j, "dcterms:issued":self.enum_c, "dc:coverage":self.chron_k,"dcterms:bibliographicCitation":self.enum_a,  "dc:title":self.pub_name,"dcterms:accrualPeriodicity":self.enum_b, "dcterms:bibliographicCitation":self.enum_a}],
									pres_master_dir=self.file_folder_place,
									generalIECharacteristics=[{"IEEntityType":"PeriodicIE","UserDefinedA":"issuu"}],
									objectIdentifier= [{"objectIdentifierType":"ALMAMMS", "objectIdentifierValue":issuu_dict[self.pub_name]["mms_id"]}],
									accessRightsPolicy=[{"policyId":"100"}],
									input_dir=self.file_folder_place ,
									digital_original=True,
									sip_title=self.pref+self.pub_name+"_"+self.description,
									output_dir=self.output_folder 
								)
				print('Done')

				report_name = "report_sips"+str(dt.now().strftime("_%d%m%Y"))+".txt"
				with open(os.path.join(report_folder_images, report_name),"a") as f:
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
	if len(os.listdir(os.path.join(sippath,  "content"))) == 0:
		logger.info("Attention - streem folder! {}".format(sippath))
		flag = True
	else:
		myfilepath = os.path.join(sippath, "content", "streams", os.listdir(os.path.join(sippath,  "content", "streams"))[0])
		if os.path.getsize(myfilepath) == 0:
				logger.info("Attention - 0 byte file! {}".format(myfilepath))
				flag = True				
	return flag

def check_for_payment(url):
		
			driver.get(url)
			sleep(5)
			try:
				print("here00")
				driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection").click()
				# <a id="CybotCookiebotDialogBodyButtonAccept" class="CybotCookiebotDialogBodyButton" href="#" tabindex="0" style="padding-left: 12px; padding-right: 12px;" lang="en">Allow all cookies</a>
				print("here00")
			except Exception as e:
				print(str(e))
				try:		
					print("here000")		
					driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept").click()
				except Exception as e:
					print(str(e))
					try:
						print("here0000")
						driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
					except Exception as e:
						print(str(e))

			sleep(7)
			driver.find_element(By.XPATH,"//button[contains(@aria-describedby, 'download_tooltip')]").click()
			sleep(7)
			html = driver.page_source
			if "The specified key does not exist" in html:
				return True
			else:
				r=requests.get(url)
				if len(re.findall("The publisher chose",r.text)) >0:
					return True
				return False
		

def request_title(pdf_url):
	r=requests.get(pdf_url)
	my_soup = bs(r.text,"lxml")
	# print(my_soup)
	web_title = my_soup.find_all("h1")[0].text
	return web_title

def request_title_date(pdf_url):
	r=requests.get(pdf_url)
	my_soup = bs(r.text,"lxml")
	web_title = my_soup.find_all("h1")[0].text
	published_stamp = my_soup.find_all("time")[0].attrs["datetime"]
	published = my_soup.find_all("time")[0].text
	return web_title, published,published_stamp

def download_wait(path_to_downloads):

    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 3500:
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

		# months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
		print(final_dict)
		enum_a = None
		enum_b = None
		enum_c = None
		chron_i = None
		chron_j = None
		chron_k = None
		if final_dict["season"]:
			chron_j = final_dict["season"]
		elif final_dict["term"]:
			chron_j=final_dict["term"]
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
	if issuu in ["Debate"]:
		seas_dict ["Summer"]="December"
		seas_dict["summer"] = "December"
		seas_dict["Raumati"]="December"
		seas_dict["Raumati"]="December"

	logger.info("Harvesting "+ issuu)
	try:
		alma_last_representation_list = last_representation_getter.last_repres_getter(issuu_dict[issuu]["mms_id"], issuu,False,seas_dict)
		print(alma_last_representation_list)
	except:
		alma_last_representation_list = [mktime(dt.fromtimestamp(0).timetuple()),0]
	if not alma_last_representation_list:
		alma_last_representation_list = [mktime(dt.fromtimestamp(0).timetuple()),0]
	logger.info("Last issue preserved on:")
	logger.info(alma_last_representation_list[1])
	try:
		if alma_last_representation_list[3] or alma_last_representation_list[5] or alma_last_representation_list[4]:
			logger.info(alma_last_representation_list[2])
	except IndexError:
		pass
	logger.info(issuu_dict[issuu]["url"])
	username = issuu_dict[issuu]["username"]
	params = {"username":username,"pageSize":"100"}
	r = requests.get(search_url,params = params)
	#logger.setLevel("DEBUG")
	logger.debug(r.text)
	my_dates = []
	try:
		# print(issuu)
		# print(os.path.join(report_folder_images,issuu + ".txt"))
		# print("here")
		with open(os.path.join(report_folder_images,issuu + ".txt"),"r")as f:
			data = f.read()
		for el in data.split("\n")[:-1]:
			my_dates.append(el)
	except Exception as e:
		# print("here2")
		print(str(e))
	if my_dates !=[]:
		print('Already harvested:')
		print(my_dates)

	my_docnames = []
	try:
		with open(os.path.join(report_folder_images,issuu + "_worked_out.txt"),"r")as f:
			data = f.read()
		for el in data.split("\n")[:-1]:
			my_docnames.append(el)
	except Exception as e:
		print(str(e))
	if my_docnames !=[]:
		print('Already in system:')
		print(my_docnames)
	for el in os.listdir(file_folder):
		os.remove(os.path.join(file_folder,el))


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
				term = None
				overflow_flag = False
				my_date = None
				custom_design = None
				others = []
				# print(doc["docname"])
				pdf_url =base_url+issuu_dict[issuu]["username"]+pdf_url_part2+doc["docname"]
				
				if not doc["docname"] in my_docnames:
					#######DO NOT REMOVE, USE IS WHEN ADDING NEW TITLE#######################
					# if issuu in ['']:
					# 	if "" in doc["docname"]:
					# 		print(doc["docname"])
					# 		web_title = request_title(pdf_url)
					# 		print(web_title)
					# 		year = web_title.split(" ")[-1]
					# 		month = web_title.split(" ")[-2]
							
					# 		my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					# 	else:
					# 		others.append(doc["docname"])
					
										#######DO NOT REMOVE, USE IS WHEN ADDING NEW TITLE#######################
					if issuu in ['AUT Millennium magazine']:
						if not "flame" in doc["docname"] and doc["docname"].startswith("mil"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							web_title = web_title.rstrip("Iissue ")
							if "/" in web_title:
								web_title = web_title.split("/")[-1]
							year = web_title.split(" ")[-1]

							month = web_title.split(" ")[-2]
							if "-" in month:
								month = month.split("-")[-1]
							if month.upper() in short_month_dict.keys():
								month=short_month_dict[month.upper()]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['AUT Millennium flame']:
						if "flame" in doc["docname"] and doc["docname"].startswith("mil"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							web_title = web_title.rstrip("issue ")
							year = web_title.split(" ")[-1]
							if "/" in year:
								year = web_title.split("/")[-1]
							season = web_title.split(" ")[-2]
							if season in months:
								month_numb = months_dictionary[season] 
								season = reversed_season[month_numb]
							month = seas_dict[season]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in [ "Guano the Bats programme"]:
						if not "impact" in doc["docname"]:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								month = dateparser.parse(published_stamp).strftime("%B")
								year = dateparser.parse(published_stamp).strftime("%Y")
								print(web_title)
								volume = web_title.split(" ")[-1]
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							except:
								with open(os.path.join(report_folder_images, "Guano_bat_skipped.txt"),"a")  as f:
									f.write(doc["docname"])
									f.write("\n")
						else:
							others.append(doc["docname"])

					if issuu in ['Onfilm']:
						if "onf" in doc["docname"] or  doc["docname"]=="production-lisintings-may2010":
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if  " - " in web_title:
								web_title=web_title.split("-")[0].rstrip(" ")
							year = web_title.split(" ")[-1]
							print(year)
							month = web_title.split(" ")[-2].capitalize()
							print(month)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
							others.append(doc["docname"])
					if issuu in ['Wainuiomata news']:
						if "wainui" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							day = web_title.split(" ")[0]
							month = web_title.split(" ")[1]
							year = dateparser.parse(published_stamp).strftime("%Y")
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

						else:
							others.append(doc["docname"])
					if issuu in ["What's the story"]:
						if doc["docname"].startswith("aaa"):
							print(doc["docname"])
							year = re.findall(r'\d{4}', doc["docname"])[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['New Zealand alpaca']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if web_title in ["Aanz december2015 final issuu"]:
								year = re.findall(r'\d{4}', web_title)[0]
								for el in web_title.split(" "):
									if year in el:
										month = el.strip(year)
							if month in seas_dict.keys():
								season = str(month)
								month = None
								my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

							else:			
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Explore south discover the South Island']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							if ("-") in year:
								year = year.split("-")[1]
							season = web_title.split(" ")[-2]
							if ("-") in season:
								season = season.split("-")[1]
							if len(year)==2:
								year="20"+year
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
					

					if issuu in ['Felis historica']:
						if not "theamericanshorthair" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							web_title = web_title.split("Historica")[1].lstrip(" -")
							year = re.findall(r'\d{4}', web_title)[0].rstrip(" ")
							web_titles = web_title.split(" ")
							for i,el in enumerate(web_titles):
								if "Volume" in el:
									volume = web_titles[i+1]
								if "Number" in el:
									number = web_titles[i+1]
								if el in months:
									month = el
							print(number, volume,month, year)

							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)

					
					if issuu in ["PUSH"]:
							print("here")
	
							web_title,published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							print(my_date)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
										#######DO NOT REMOVE, USE IS WHEN ADDING NEW TITLE#######################
					if issuu in ['Debate']:
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
							except:
								web_title = request_title(pdf_url)
							my_title_list = web_title.split("|")
							for el in my_title_list:
								try:
									year = re.findall(r'\d{4}', el)[0].rstrip(" ")
								except:
									pass
								if "Issue" in el and not "Elec" in el and not "Queer" in el:
									issue = el.strip("Issue ")
							if not year:
								try:
									year = doc["docname"].split("_")[-1]
								except:
									pass
							if not year or not year.isdigit() or len(year)!=4:
								if published_stamp:
									year = dateparser.parse(published_stamp).strftime("%Y")
								else:
									year = "2017"

							# print(my_date)
							my_date=0
						# else:
						# 	others.append(doc["docname"])


											
				if my_date or my_date==0:
					if my_date!=0:
						logger.debug(my_date.strftime("%d %B %Y"))
						try:
							my_date_stamp = mktime(my_date.timetuple())


						except OverflowError:
							overflow_flag = True
						print(alma_last_representation_list[0])
						if alma_last_representation_list[1] == 0:
							new_title = str(issuu)
						print(my_date_stamp)
						print(my_dates)
						if overflow_flag or (my_date_stamp > alma_last_representation_list[0] and my_date.strftime("%d %B %Y") not in my_dates) or issuu==new_title:
								my_dict["docname"] =doc["docname"]
								my_dict["document_id"] = doc["documentId"]
								my_dict["url"]=pdf_url
								my_dict["web_title"]=web_title
								my_dict["season"] = season
								my_dict["term"] = term
								my_dict["date"] = my_date.strftime("%d %B %Y")
								my_dict["year"]=my_date.strftime("%Y")
								my_dict["month"]=my_date.strftime("%B")
								my_dict["day"] = my_date.strftime("%d")
								my_dict["my_date_stamp"] = my_date_stamp
								my_dict["issue"] = issue
								my_dict["volume"] = volume
								my_dict["number"] = number
								my_dict["custom_design"] = custom_design
								if issuu in ["PUSH",'Debate','Felis historica','Explore south discover the South Island','New Zealand alpaca',"What's the story",'Onfilm',"Guano the Bats programme",'AUT Millennium flame']:
									my_dict["day"]=None
								if issuu in ['Debate',"What's the story",'AUT Millennium flame']:
									my_dict["month"] = None


					else:
						if my_design not in my_dates:
								my_dict["docname"] =doc["docname"]
								my_dict["document_id"] = doc["documentId"]
								my_dict["url"]=pdf_url
								my_dict["web_title"]=web_title
								my_dict["season"] = season
								my_dict["term"] = term
								my_dict["date"] = None
								my_dict["year"]=year
								my_dict["month"]=None
								my_dict["day"] = None
								my_dict["my_date_stamp"] = None
								my_dict["issue"] = issue
								my_dict["volume"] = volume
								my_dict["number"] = number
								if not (year > alma_last_representation_list[2]["year"] or (year==alma_last_representation_list[2]["year"] and issue> alma_last_representation_list[2]["issue"]))and issue in ['Debate']:
									my_dict={}
					if not my_dict in my_dict_list and my_dict !={}:
							my_dict_list.append(my_dict)
	print(my_dict_list)
	for el in others:
		if el not in my_docnames:
			with open(os.path.join(report_folder_images, issuu+"_worked_out.txt"),"a") as f:
				f.write(el)
				f.write("\n")
	for ind,pub in enumerate(my_dict_list):
		flag_to_do = False
		# if not check_for_payment(pub["url"]):

		end_flag = False
		size_dictionary ={}

		for i in range(500):
			if not end_flag:
				try:
					print("here4")
					my_link=page_url+pub["document_id"]+page_url_part2+str(i+1)+".jpg"
					
					r = requests.head(my_link)
					if r.status_code == 403:
						end_flag = True
					else:
						r = requests.head(my_link)
						size_dictionary["page_"+str(i+1)+".jpg"]=r.headers["Content-Length"]
						wget.download(my_link, out =file_folder)

				except urllib.error.HTTPError as e:
					pass
				except Exception as e:
					print(str(e))
		my_filenames = os.listdir(file_folder)
		for image in my_filenames:
			if os.path.getsize(os.path.join(file_folder, image)) == int(size_dictionary[image]):
				shutil.move(os.path.join(file_folder, image),os.path.join(file_folder, "page_" + image.split('.')[0].split("_")[1].zfill(2)+".jpg"))
			else:
				quit()



		enum_a, enum_b, enum_c, chron_i, chron_j, chron_k=parse_final_dictionary({"issue":pub["issue"], "volume":pub["volume"], "number":pub["number"],"season":pub["season"],"day":pub["day"],"month_string": pub["month"],"year":pub["year"],"term":pub["term"]}) 
		
		my_design = description_maker.make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)

		flname = os.path.join(file_folder, os.listdir(file_folder)[0])
		new_filename = flname.replace("","_")
		try:
			shutil.move(flname, new_filename)
		except Exception as e:
			print(str(e))
		my_sip = SIPMaker(issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design, file_folder)
		if my_sip.flag:
			for el in os.listdir(file_folder):
						os.remove(os.path.join(file_folder,el))
			my_item = ItemMaker()
			my_item.item_routine( issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design)
			if pub["date"]:
				with open(os.path.join(report_folder_images,issuu+".txt"),"a") as f:
					f.write(pub["date"])
					f.write("\n")
			else:
				with open(os.path.join(report_folder_images,issuu+".txt"),"a") as f:
					f.write(my_design)
					f.write("\n")
			with open(os.path.join(report_folder_images, issuu+"_worked_out.txt"),"a") as f:
				f.write(pub["docname"])
				f.write("\n")
		# else:
			
		# 	print("Payment detected")

	

def main():
	go_to_flag = False
	if len(os.listdir(file_folder))!=0:
		for el in os.listdir(file_folder):
			os.remove(os.path.join(file_folder, el))
	for issuu in issuu_dict:
		harvester_routine(issuu)
		sips_number = len(os.listdir(sip_folder))
		for sip in os.listdir(sip_folder):
			sippath = os.path.join(sip_folder,sip)
			sip_error_flag = sip_checker(sippath)
			if not sip_error_flag:
				try:
					shutil.move(sippath, rosetta_folder)
				except shutil.Error:
					print("SIP exists")
					go_to_flag = True
			else:
				quit()
		if not go_to_flag:			
			logger.info(str(sips_number)+' sips moved to '+rosetta_folder)
	driver.quit()



if __name__ == "__main__":			
	main()
