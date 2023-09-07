import os
import re
import time
import json
import sys
import wget
import requests
import shutil
import urllib
import dateparser
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from time import mktime, sleep
from sys import platform
from rosetta_sip_factory.sip_builder import build_sip
from description_maker import make_description
import description_maker
from issuu_image_dict import issuu_dict
from my_settings import to_send_email, file_sip_folder, file_folder, email_address_line, report_folder_images, template_folder,logging, rosetta_folder, seas_dict, term_dict, months, reversed_season, months_dictionary,short_month_dict, not_processed_files
from my_settings  import sip_folder_images as sip_folder
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\alma_tools')
from alma_tools import AlmaTools
from email_maker import Gen_Emails
import filetype
#sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\waterford\scripts')
import last_representation_getter
import send_email
from issuu_cover_displayer_all import routine as covers_routine
from selenium import webdriver
from selenium.webdriver.common.by import By
from sys import platform
from selenium.common import exceptions
from selenium.webdriver.firefox.options import Options
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# import ctypes

# # prevent
# ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
# # set back to normal
# # ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)
print("Firefox Headless Browser Invoked")



logger = logging.getLogger(__name__)
base_url = r"https://issuu.com/"
search_url = r"https://search.issuu.com/api/2_0/document"
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
			receive_date = dt.now().strftime("%Y-%m-%d")
			my_alma.create_item_by_po_line(issuu_dict[pub_name]["po_line"], item_data,{"receive_date":receive_date})
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
			enum_b (str) - enumeration brequest
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
			os.chdir("..")
			os.getcwd()
			self.sip_name_folder = self.pub_name.replace(" ","_") + "_"+self.description.replace(" ","").replace(".","_").replace("(","-").replace(")","-").replace(",","-").rstrip("-").rstrip("_")
			self.output_folder = os.path.join(sip_folder, self.sip_name_folder )
			logger.info(self.output_folder)
			try:
				build_sip(
									ie_dmd_dict=[{"dc:date":self.chron_i, "dcterms:available":self.chron_j, "dcterms:issued":self.enum_c, "dc:coverage":self.chron_k,"dcterms:bibliographicCitation":self.enum_a,  "dc:title":self.pub_name,"dcterms:accrualPeriodicity":self.enum_b, "dcterms:bibliographicCitation":self.enum_a}],
									pres_master_dir=self.file_folder_place,
									generalIECharacteristics=[{"IEEntityType":"PeriodicIE","UserDefinedA":"issuu"}],
									objectIdentifier= [{"objectIdentifierType":"ALMAMMS", "objectIdentifierValue":issuu_dict[self.pub_name]["mms_id"]}],
									accessRightsPolicy=[{"policyId":issuu_dict[self.pub_name]["access"]}],
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
			os.chdir("scripts")
			os.getcwd()
def get_my_doc_json(url):

	print(url)
	driver.get(url)
	driver.implicitly_wait(13)
	#scroll_down(driver)
	#driver.implicitly_wait(5)
	#############################################
	#change to [-2] when listing pages for backlogs as link will be ended with /2 ,/3,/4
	username = url.split("/")[-1]
	##############################################
	html = driver.page_source
	soup = bs(html, "html.parser")
	links = soup.find_all("a", href=True)
	matched_links = []
	for link in links:

		href = link.get("href")

		if "{}/docs/".format(username) in href:
		    image_link = link.find("div").find("div").find("img").get("src")
	
		    image_id = image_link.split("/")[-3]
		    docname = href.split("/")[-1]
		    matched_links.append({"docname":docname, "documentId":image_id})
	# print(matched_links)
	return matched_links



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
			print("CHECK FOR PAYMENT")
		
			driver.get(url)
			sleep(10)
			try:

				driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection").click()
				# <a id="CybotCookiebotDialogBodyButtonAccept" class="CybotCookiebotDialogBodyButton" href="#" tabindex="0" style="padding-left: 12px; padding-right: 12px;" lang="en">Allow all cookies</a>
			except Exception as e:
				#print(str(e))
				try:		
	
					driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept").click()
				except Exception as e:
					#print(str(e))
					try:
						driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
					except Exception as e:
						print(str(e))

			sleep(7)
			# driver.find_element(By.XPATH,"//button[contains(@aria-describedby, 'download_tooltip')]").click()
			# sleep(7)
			html = driver.page_source
			print("here1")
			#print(html)
			if "The specified key does not exist" in html:
				print("here2")
				return True
			# else:
			# 	print("here3")
			# 	r=requests.get(url, verify=False)
			# 	if len(re.findall("The publisher chose",r.text)) >0:
			# 		return True
			return False

def scroll_down(driver):

	"""
	A method for scrolling the page.
	Origin: #https://stackoverflow.com/questions/48850974/selenium-scroll-to-end-of-page-in-dynamically-loading-webpage
	"""

	last_height = driver.execute_script("return document.body.scrollHeight")

	while True:
	# for i in range(3):

	    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	    sleep(6)
	    new_height = driver.execute_script("return document.body.scrollHeight")
	    if new_height == last_height:
	         break
	    last_height = new_height		

def request_title(pdf_url):
	r=requests.get(pdf_url ,verify=False)
	print(r.url)
	#print(r.text)
	my_soup = bs(r.text,"lxml")
	# print(my_soup)
	try:
		web_title = my_soup.find_all("h1")[0].text
	except:
		try:
			web_title = my_soup.find_all("h3")[0].text
		except:
			web_title = my_soup.find_all("title")[0].text
	return web_title

def request_title_date(pdf_url):
	r=requests.get(pdf_url,verify=False)
	#print(r.text)

	my_soup = bs(r.text,"html.parser")
	try:
		web_title = my_soup.find_all("h1")[0].text
	except:
		web_title = my_soup.find_all("h3")[0].text
	try:
		published_stamp = my_soup.find_all("time")[0].attrs["datetime"]
		published = my_soup.find_all("time")[0].text
	except:
			# data = json.loads(my_soup.find('script'))#, type='application/ld+json').text)
		data = my_soup.find_all('script')[9]["data-json"]#, type='application/ld+json').text)
		#print(data)
		json_object = json.loads(data)
		# for el  in json_object["initialDocumentData"]["document"].keys():
		# 	print("_____________")
		# 	print(el)
		# 	try:
		# 		print(json_object["initialDocumentData"]["document"][el])
		# 	except:
		# 		pass
		published_stamp = json_object["initialDocumentData"]["document"]["originalPublishDateInISOString"]
		published = published_stamp.split("T")[0]
		web_title = json_object["initialDocumentData"]["document"]["title"]

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
	if issuu in ["Otaki street scene","Debate","Ōtaki street scene",'Carterton and South Wairarapa street scene',"Nourish magazine",'Real Estate','The MAP']:
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
	pub_url = issuu_dict[issuu]["url"]
	params = {"username":username,"pageSize":"100"}
	# r = requests.get(search_url,params = params,verify=False)
	# print(search_url)
	# print(params)
	# print(r)
	# print(r.url)
	# quit()

	
	#logger.setLevel("DEBUG")
	#logger.debug(r.text)
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
		# print("here2").
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
		with open(os.path.join(report_folder_images,issuu + "_worked_out2.txt"),"r")as f:
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

	my_docs =  get_my_doc_json(pub_url)

	# my_json = r.json()
	# num_found = my_json["response"]["numFound"]
	my_dict_list = []
	my_dict = {}
	others = []
	# for ind in range(int(num_found)//100+2):
	# 	start_index = ((int(num_found)//100)-ind)*100
	# 	params["startIndex"]=start_index
	# 	r = requests.get(search_url, params,verify=False)
	# 	my_doc_json = r.json()["response"]["docs"]
	# 	logger.debug(my_doc_json)
	for doc in my_docs:

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
				my_date = "None"
				day = None
				custom_design = None
				others = []
				published_stamp = None
				# print(doc["docname"])
				pdf_url =base_url+issuu_dict[issuu]["username"]+pdf_url_part2+doc["docname"]
				print(doc["docname"])
				print(my_docnames)

				if not doc["docname"] in my_docnames:
					print("here4444")
					#######DO NOT REMOVE, USE THE TEMPLATE WHEN ADDING NEW TITLE#######################
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
					
					#######DO NOT REMOVE, USE THE TEMPLATE WHEN ADDING NEW TITLE#######################
					if issuu in ['Arthritis annual review report']:
						if not "join" in doc["docname"] and ("annual" in doc["docname"] or "review" in doc["docname"]):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
						
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Joint support']:
						if "join" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Te Whatu Ora panui Health New Zealand Canterbury news']:
						if "-cant" in doc["docname"] and "news" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							if " / " in web_title:
								web_title = web_title.split(" / ")[0]
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
							
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])





					if issuu in ['Academic freedom survey']:
						if "" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])

					
					if issuu in ["Auto channel"]:
						if "ac_" in doc["docname"] or "auto" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							issue = web_title.split(" ")[-1].strip("#")			
							year = dateparser.parse(published_stamp).strftime("%Y")
							month_num= str(int(dateparser.parse(published_stamp).strftime("%m"))+1).zfill(2)
							if month_num == "13":
								month_num = "01"
								year = str(int(year)+1)
							print(month_num)
							for el in months_dictionary:
								if months_dictionary[el] == month_num:
									month = str(el)

							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

						else:	
							others.append(doc["docname"])
					if issuu in ['Student voice']:
						if  doc["docname"].startswith("student") or doc["docname"]=="etla_2019_spring_issuu" or doc["docname"]=="education_day_student_voice_2021_2021_summer_editi" or doc["docname"] == "education_today_magazine_spring_2020_issuu_updated" :
							print(doc["docname"])
							year = re.findall(r'\d{4}', doc["docname"])[0]	
							seas_list = doc["docname"].split("_")
							for ses in seas_list:
								if ses in seas_dict.keys():
									season = str(ses).capitalize()
							if doc["docname"] == "student_voice_2022_issuu":
								season = "Summer"
							if doc["docname"] == "education_today_magazine_spring_2020_issuu_updated":
								season = "Spring"
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Learning Auckland']:
						if doc["docname"].startswith("la") or doc["docname"].startswith("learning"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(",")[-1].strip(" ")
							issue = web_title.split(",")[-2].lstrip("LA ")
							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['New Zealand apparel trade directory']:
						if doc["docname"].startswith("ap") and ("trade" in doc["docname"] or "_td" in doc["docname"]):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							year = re.findall(r'\d{4}', web_title)[0]	
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Otuihau News']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							issue = web_title.split(" ")[-3]
							if "/" in year:
								year = "20" + year.split("/")[-1]
							if month in seas_dict.keys():
								season = str(month)
								month = None
								my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})



					if issuu in ['Dawn chorus']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							title_words = web_title.split(" ")

							try:
								issue = re.findall(r'\s(\d{3})\s', web_title)[0]
							except:
								issue = re.findall(r'\s(\d{3}),', web_title)[0]
							try:
								year = re.findall(r'\d{4}', web_title)[0]
							except:
								year=None
							for wrd in title_words:
								wrd=wrd.strip("()")
								if wrd.capitalize() in short_month_dict.keys():
									month = short_month_dict[wrd.capitalize()]
							if not month or not year:
								web_title, published, published_stamp = request_title_date(pdf_url)
								if not year:
									year = dateparser.parse(published_stamp).strftime("%Y")
								if not month:
								    month = dateparser.parse(published_stamp).strftime("%B")	
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ["Tira ora"]:
						if "year" in doc["docname"] and "book" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							try:
								year = re.findall(r'\d{4}', web_title)[0]
							except:
								year = re.findall(r'\d{4}', doc["docname"])[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])					
	
					if issuu in ['St Josephs Maori Girls College']:
						if "mag" in doc["docname"] or "year" in doc["docname"] and not "portf" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])					
					if issuu in ["Yearbook"]:
						if "yearbook" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])

					if issuu in ['The Fringe']:

							print(doc["docname"])
							web_title = request_title(pdf_url)
							if "/" in web_title:
								web_title = web_title.split("/")[-1]
							web_title = web_title.rstrip(".")
							year = web_title.split(" ")[-1]
							print(year)
							try:
								month = web_title.split(" ")[-2]
								
							except:
								pass
							print(month)
							if not year.isdigit() or year.startswith("1") or  not  month or (month and month  not in months_dictionary.keys()):
								# try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
								month = dateparser.parse(published_stamp).strftime("%B")
								print(year)
								print(month)
								# except:
								# 	if doc["docname"] in [""]:
								# 		year = 
								# 		month = 
							if doc["docname"] == "fringe_1703":
								year = "2017"
								month = "March"
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ['Leaders']:
						if doc["docname"].startswith("leader") or (doc["docname"].startswith("lnz") and "mag" in doc["docname"]):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
					
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])

					if issuu in ["Nelson City guide"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if "-" in web_title:
								year = web_title.split("-")[-1]
							elif "/" in web_title:
								year = web_title.split("/")[-1]
							else:
								year =web_title.split(" ")[-1]
							if len(year) == 2:
								year = "20"+year														
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})

					
					if issuu in ["Metropol"]:
						if not "bridal" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							date_string = web_title.replace("Metropol","").replace("Magazine","").replace("-","").rstrip(" ").lstrip(" ")
							date_list = date_string.split(" ")
							if len(date_list) ==3:
								year = date_list[2]
								month = date_list[1]
								day = date_list[0]
							if len(date_list) ==2:
								month = date_list[1]
								day = date_list[0]
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							if len(year) <4:
								year= doc["docname"].split("_")[-1]
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['The MAP']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							if "/" in year:
								year = year.split("/")[-1]
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

					
					if issuu in ['Canterbury farming']:
						web_title = request_title(pdf_url)
						year = web_title.split(" ")[-1]
						month = web_title.split(" ")[-2]
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})


					if issuu in ['Art Beat Christchurch and Canterbury']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							# try:
							year = re.findall(r'\d{4}', web_title)[0].rstrip(" ")
							print (year)
							# except:
							# 	try:
							# 		year = re.findall(r'\d{4}', doc["docname"])[0]
							# 	except:
									# year = "20"+re.findall(r'\d{4}', doc["docname"])[0]
							other_part = web_title.split(year)[0].rstrip()
							month = other_part.split(" ")[-1]
							print(month)
							if "/"in month:
								month = month.split("/")[0]
								if month == "December":
									year = str(int(year)-1)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)




					if issuu in ['B plus d xin zhu, zhu zin']:
						if "yiju" in doc["docname"] and not "prop" in doc["docname"]:
							print(doc["docname"])
							try:	
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							except:
								year = dt.now().strftime("%Y")
							issue = web_title.split(" ")[-1]
							if not issue.isdigit():
								issue= re.findall(r'\d{2}', web_title)[0]
							my_date = 0
						else:	
							others.append(doc["docname"])
					if issuu in ['Joiners magazine']:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							web_title = web_title.rstrip("Issue")
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Nexus']:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							web_title = web_title.rstrip(" ")
							year = web_title.split(" ")[-3]
							issue = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})



					if issuu in ["Prospectus imagine your future"]:
						if "prospect" in doc["docname"] and not "intern" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
						
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Loud']:
						if doc["docname"].startswith("loud") and not "gall" in doc["docname"]:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
								number= re.findall(r'\d{2}', web_title)[0]
								my_date=0
							except:
								print("Loud process manually")
								print(doc["docname"])
						else:	
							others.append(doc["docname"])
					if issuu in ['Pipiwharauroa']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.replace(")2",") 2")
							print(web_title)
							title_list = web_title.split(" ")
							for el in title_list:
								if el.isdigit():
									year = str(el)
								if el.strip("()").capitalize() in list(months_dictionary.keys())+list(short_month_dict.keys()):
									month = el.capitalize()
							if not month or not year:
								print("here")
								docname_list  = doc["docname"].split("_")
								for el in docname_list:
									if el.isdigit():
										year = str(el)
									if el.strip("()").capitalize() in list(months_dictionary.keys())+list(short_month_dict.keys()):
										month = el.capitalize()
							if doc["docname"]=="feb_2021_pipi":
								month = "February"
								year = "2021"
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Rodnik Russian Cultural Herald']:

							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							try:
								year = re.findall(r'\d{4}', web_title)[0]
							except:
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							issue = re.findall(r'\d{2}', doc["docname"])[0]
							print(issue)
							print(year)

							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Te panui runaka']:
						if "tpr" in doc["docname"] or "te_p" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month:
									month = month.split("/")[0]
							if "-" in month:
									month = month.split("-")[0]
							if not year.isdigit():
								year = re.findall(r'\d{4}', doc["docname"])[0]
								if not year.startswith("20"):
									year = re.findall(r'\d{4}', doc["docname"])[-1]
							if not month.capitalize() in list(months_dictionary.keys())+list(short_month_dict.keys()):
								for el in doc["docname"].split("_"):
									if el.capitalize().strip("()") in list(months_dictionary.keys())+list(short_month_dict.keys()):
										month = el.capitalize()
							print (year, month)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Luminate festival']:
						if "festival" in doc["docname"] and "luminate" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]					
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ["Kamo connect"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							if not year.isdigit() or len(year)<4:
								try:
									web_title, published, published_stamp = request_title_date(pdf_url)
									year = dateparser.parse(published_stamp).strftime("%Y")
								except:
									print(doc["docname"])
									print("!!!!!!!!!!!!!!!!!!!!!!!!!!! please  preserve manually")
							if year:
								title_list = web_title.split(" ")
								for el in title_list:
									if el.capitalize() in months_dictionary.keys():
										month = el.capitalize()
									if el.capitalize() in seas_dict.keys():
										season = el.capitalize()
								if "issuu" in web_title.lower():
									issue = web_title.lower().split("issue")[-1].lstrip(" ")
									if not issue.isdigit():
										issue= None
								if "edition" in web_title.lower():
									number = web_title.lower().split("edition")[-1].lstrip(" ")
									if not number.isdigit():
										number= None
								if month:
									my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
								else:	
									if not season:
										try:
											web_title, published, published_stamp = request_title_date(pdf_url)
											month = dateparser.parse(published_stamp).strftime("%B")
											my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
										except:
											print(doc["docname"])
											print("!!!!!!!!!!!!!!!!!!!!!!!!!!! please  preserve manually")
									else:
										my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Hotel']:
						if (doc["docname"].startswith("hotel") or doc["docname"].startswith("ht")) and not "gift" in doc["docname"] and not "christ" in doc["docname"] and not "valentines" in doc["docname"] and not "guide" in doc["docname"] and not "buy" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							if not year.isdigit() or len(year)<4:
								year = re.findall(r'\d{4}', doc["docname"])[0]

								if "issue" in web_title.lower():
									issue = web_title.lower().split("issue")[-1]

							if "no." in web_title.lower():
								number = web_title.lower().split("no.")[-1].split(" ")[0]
							if "vol." in web_title.lower():
								volume = web_title.lower().split("vol.")[-1].split(" ")[0]					
							my_design = description_maker.make_description(volume, number, None, year, None,None)
							my_date=0
						else:	
							others.append(doc["docname"])
					if issuu in ["Fennec"]:
						if (doc["docname"].startswith("fen") or doc["docname"].startswith("ff")) and not "gift" in doc["docname"] and not "christ" in doc["docname"] and not "valentines" in doc["docname"] and not "guide" in doc["docname"] and not "buy" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							year = dateparser.parse(published_stamp).strftime("%Y")
							number = web_title.rstrip(" ").split(" ")[-1].lstrip("Nno.")
							if "vol" in web_title.lower():
								print("here")
								print(web_title)
								volume = web_title.lower().split("vol")[-1].lstrip(" .").split(" ")[0].rstrip(".")
								print(volume)
							my_date=0
						else:	
							others.append(doc["docname"])			

					if issuu in ["Supermarketnews"]:
							print(doc["docname"])
							if doc["docname"].startswith("sn") and doc["docname"].startswith("super") and not "buyer" in doc["docname"] and not "guide" in doc["docname"]:
								web_title = request_title(pdf_url)
								print(web_title)
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2].capitalize()
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:	
								others.append(doc["docname"])	
					if issuu in ["New Zealand apparel"]:
						if doc["docname"].startswith("ap") and not "gift" in doc["docname"] and not "bayer" in doc["docname"] and not "guide" in doc["docname"] and not doc["docname"].endswith("_td") and not "trade_d" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month:
								if "Dec" in month:
									month = month.split("/")[-1]
								else:
									month = month.split("/")[0]
							if month in seas_dict:
								my_date=dateparser.parse("01 "+seas_dict[month]+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['F and B technology']:
						if doc["docname"].startswith("f_b") and not "guid" in doc["docname"] and not "_bg_" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month:
								if "Dec" in month:
									month = month.split("/")[-1]
								else:
									month = month.split("/")[0]
							if "-" in month:
									month = month.split("-")[0]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Restaurant and cafe buyer guide']:
						if doc["docname"].startswith("r_c"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							print(year)
							if not year.isdigit():
								year = re.findall(r'\d{4}', web_title)[0]
							print(year)										
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Restaurant and cafe']:
						if doc["docname"].startswith("r_c") and not "guid" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month and "Dec" in month:
								month = month.split("/")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Agedplus village']:
						if doc["docname"].startswith("ag"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							if not "buyer" in web_title.lower():
								print(web_title)
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2]
								if "/" in month:
									month = month.split("/")[0]
								if "-" in month:
									month = month.split("-")[0]

								print(year)
								print(month)
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Agedplus village business']:
						if doc["docname"].startswith("ag"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							if not "buyer" in web_title.lower():
								print(web_title)
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2]
								if "/" in month:
									month = month.split("/")[0]
								if "-" in month:
									month = month.split("-")[0]
								print(year)
								print(month)
								
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Family times']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ['Avenues the magazine Christchurch lives by']:
						if doc["docname"].startswith("aven"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							if "/" in month:
								month = month.split("/")[0]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Rural living handbook']:
						if doc["docname"].startswith("rl") or "rural" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)

							year = web_title.split(" ")[-1]
							if "-" in web_title:
								print("- in title")
								month= web_title.split("-")[-2].rstrip(" ").split(" ")[-1]
								if month.isdigit():
									print(month, "digit")
									year= web_title.split("-")[-2].rstrip(" ").split(" ")[-1]
									month= web_title.split("-")[-2].rstrip(" ").split(" ")[-2] 
							if "/" in web_title:
								print("/ int title")
								month= web_title.split("/")[-2].rstrip(" ").split(" ")[-1]
								if month.isdigit():
									print(month, "digit")
									year= web_title.split("/")[-2].rstrip(" ").split(" ")[-1]
									month= web_title.split("/")[-2].rstrip(" ").split(" ")[-2]
							if not "-" in web_title and not "/" in web_title:
								print("/- not in title")
								month = web_title.split(" ")[-3]
								if month not in months_dictionary.keys():
									month = web_title.split(" ")[-2]
							if doc["docname"]	== "rlaugust-september19":
								month = "August"				
							if doc["docname"] == "rloctober-november19":
								month = "October"
							print(month)
							print(year)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])


					if issuu in ['Eastlife Howick, Botany, Pakuranga and surrounds']:
						if doc["docname"].startswith("el") or doc["docname"].startswith("east"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if "-"  in web_title:
								web_title=web_title.split("-")[-1]
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month:
								month = month.split("/")[0]
							if doc["docname"] in ["eastlifejuly23_mocks"]:
								year = "2023"
								month = "July"
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Design and build South East']:
						if doc["docname"].startswith("des"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							print(year)
							if "/" in year:
								year = year.split("/")[0]
							if "-" in year:
								year = year.split("-")[0]
							print(year)
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])



					if issuu in ['Tract  landscape and architecture research work']:
						if doc["docname"].startswith("yearbook"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0]						

							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ["Finalist stories"]:
						if "rhm" in doc["docname"] or "finalist" in doc["docname"] or "ronald" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0]
							if doc["docname"] in ["2017_rhm_finalist_stories"]:
								year = "2017"							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])
					if issuu in ['Salient Victoria University']:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)

							year = dateparser.parse(published_stamp).strftime("%Y")
							print(year)
							issue  = web_title.lstrip("SalientIssue ").split(" ")[0].strip(":-_")
							print(issue)
							my_date=0
					
					if issuu in ['Showcircuit ultimate equestrian magazine']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if "/" in web_title:
								web_title = web_title.replace(" / ","/")
								web_title = web_title.split("/")[0]

							year = web_title.split(" ")[-1]
							if len(year) ==2:
								year = "20"+year
							month = web_title.split(" ")[-2]
							if "/" in month:
								month = month.split("/")[0]
							if month in short_month_dict.keys():
								month = short_month_dict[month]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					

					if issuu in ['The Observer']:
						web_title, published, published_stamp = request_title_date(pdf_url)
						print(web_title)
						web_title_list = web_title.split(" ")
						print(web_title_list)
						for el in web_title_list:
							if el in months_dictionary.keys():
								month = str(el.capitalize())
							if el in short_month_dict.keys():
								month = short_month_dict[el]
							if el.isdigit() and len(el) ==4:
								year = str(el)
							if not year:
								try:
									year = re.findall(r'\d{4}', doc["docname"])[0]
								except:
									pass

							if not year:
								year = dateparser.parse(published_stamp).strftime("%Y")
	
						print(year, month)
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})


					if issuu in ['Real Estate']:

							print(doc["docname"])
							web_title = request_title(pdf_url)
							if "/" in web_title:
								web_title =web_title.split("/")[0]
							year = web_title.split(" ")[-1]
							season= web_title.split(" ")[-2].capitalize()
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

					# if issuu in ["Design and build South East"]:
					# 	if "" in doc["docname"]:
					# 		print(doc["docname"])
					# 		web_title = request_title(pdf_url)
					# 		print(web_title)
					# 		year = web_title.split(" ")[-1]
					# 		month = web_title.split(" ")[-2]
							
					# 		my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					# 	else:	
					# 		others.append(doc["docname"])

					if issuu in ['Raglan chronicle Raglan community news']:
						if "chronic" in doc["docname"]:
							print(doc["docname"])
							doc["docname"] = doc["docname"].rstrip("-swebcopy").rstrip("_converted")
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								print(web_title)
								year = dateparser.parse(published_stamp).strftime("%Y")
								month = dateparser.parse(published_stamp).strftime("%B")
								day = doc["docname"][-2:]
								if not day.isdigit():
									day = doc["docname"][-1]
							except:
								if doc["docname"] == "chronicle_week_2_march_11_1":
									year = "2021"
									month = "March"
									day = "11"
								elif doc["docname"] == "chronicle_week_9_june":
									day = "9"
									month= "June"
									year = "2022"
								elif doc["docname"] == "chronicle_week_2_august_13_3":
									day = "13"
									month= "August"
									year = "2020"
								elif doc["docname"] == "chronicle_week_2_january_17":
									day = "17"
									month= "January"
									year = "2019"
								elif doc["docname"] == "chronicle_week_1_nov1":
									day = "1"
									month= "November"
									year = "2018"
								elif doc["docname"] == "chronicle_february_23_week_4s":
									day ="23"
									month = "February"
									year ="2023"

							# month = doc["docname"].split("_")[-2].capitalize()
							# day=doc["docname"].split("_")[-1]
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])

					if issuu in ["Playmarket annual"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							if " NO. " in web_title.upper():
								issue = web_title.upper().split(" NO. ")[-1]
								year = web_title.upper().split(" ")[-3]
							
								my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
							if " NO " in web_title.upper():
								issue = web_title.upper().split(" NO ")[-1]
								year = web_title.upper().split(" ")[-3]
							
								my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})

					
					if issuu in ['Nourish magazine']:
						if "bop" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							web_title_list = web_title.split(" ")
							for el in web_title_list:
								if el.capitalize() in seas_dict.keys():
									season = str(el).capitalize()
								elif el.isdigit() and len(el) == 4:
									year = str(el)
								elif el.isdigit() and len(el)==2:
									year = "20"+str(el)
							if doc["docname"] in ["sum18_-_bop_-_web"]:
								year = "2018"
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

										
					if issuu in ['Chat 21 Down Syndrome community']:
							month = None
							season = None
							print(doc["docname"])

							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							print(year)
							print(season)
							if "-" in year:
								year = year.split("-")[0]
							if year.lower()=="edition":
								year = dateparser.parse(published_stamp).strftime("%Y")
							if season.lower() == "christmas":
								season = "Summer"
							if season.lower() == "edition":
								season = web_title.split(" ")[-3]
							if season in months_dictionary.keys():
								month = str(season.upper())	
								season = None	
							if month:	
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['NZBPT news']:
						if "news" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							my_title_list = web_title.split(" ")
							for el in my_title_list:
								if el.capitalize() in months:
									month = el.capitalize()
								else:
									if el.isdigit and len(el)==4:
										year = str(el)
							print(year)
							print(month)
							if not year:
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							print(year)
							print(month)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
							others.append(doc["docname"])
					if issuu in ['New Zealand Business and Parliament Trust']:
						if "annual" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0].rstrip(" ")
						
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Nelson weekly"]:
						if "nelwk" in doc["docname"] or "nelson_we" in doc["docname"] or "nw" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.rstrip("- Nelson wWeekly").lstrip("Nelson Wweekly-")

							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					
					if issuu in ["Nelson magazine"]:
						if "nelson_mag" in doc["docname"] or "nls" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					
					if issuu in ["The lion Mount Albert Grammar School"]:
						if "lion" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['The maritimes newsletter of the Maritime Union of New Zealand']:
						if not "worker" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if "maritimes" in doc["docname"]:
								try:
									issue= doc["docname"].split("_")[1]
								except:

									try:
									 	issue = re.findall(r'\d{2}', doc["docname"])[0]
									except:
									 	pass

								if not issue.isdigit():
									issue = None
							if "vol" in doc["docname"]:
								if doc["docname"].split("_")[-1].isdigit():
									volume = doc["docname"].split("_")[-1]
							
							
							year = web_title.split(" ")[-1]
							if "/" in year:
								year = year.split("/")[-1]
							month_season = web_title.split(" ")[-2]
							if "/" in month_season:
								month_season = month_season.split("/")[0]
							if month_season in months_dictionary.keys():
								month = str(month_season).capitalize()
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							elif month_season in seas_dict.keys():
								season = str(month_season).capitalize()
								my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['The maritime worker Wellington branch']:
						if "worker" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]

							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					
					if issuu in ['Otaki street scene']:
						if "taki_st" in doc["docname"] or "oss" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2].capitalize()
							if "-" in year:
								year = year.split("-")[0]
							if not year.isdigit():
								year = doc["docname"].split("_")[-1]
							if season.capitalize() not in seas_dict.keys():
								season = doc["docname"].split("_")[-2].capitalize()
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Otaki today Nga korero o Otaki"]:
						if "today" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if doc["docname"] in ["_taki_today_sept_2021"]:
								month = "September"
								year = "2021"
							elif "," in web_title:
								year = web_title.split(" ")[-1]
								day = web_title.split(" ")[-2].rstrip(",")
								month = web_title.split(" ")[-3]
							else:
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2]
							if month  in short_month_dict.keys():
								month = short_month_dict[month]
							if not day:
								day = "01"
							my_date=dateparser.parse(day+" " +month+ " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])									

					if issuu in ['NZGrower']:
						if "nzgrower" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])


					if issuu in ['The Orchardist']:
						if "orchard" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							issue = doc["docname"].split("_")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Heritage quarterly heritage']:
						if "quarterly" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['Heritage New Zealand']:

						if "heritagenz" in doc["docname"]:
							issue = doc["docname"].split("_")[-1]
							if doc["docname"] == "heritagenz_168":
								season = "Autumn"
								year = "2023"
								my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								print(doc["docname"])
								web_title = request_title(pdf_url)
								print(web_title)
								year = web_title.split(" ")[-1]
								season = web_title.split(" ")[-2]
								issue = doc["docname"].split("_")[-1]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['New Zealand freemason']:
						
						print(doc["docname"])
						web_title, published, published_stamp = request_title_date(pdf_url)
						print(web_title)
						year = web_title.split(" ")[-1]
						month = web_title.split(" ")[-2]
						issue = web_title.split(" ")[-3]
						print(year)
						print(month)
						print(issue)
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

										
					if issuu in ['Featherston phoenix']:

						print(doc["docname"])
						web_title = request_title(pdf_url)
						print(web_title)
						year = web_title.split(" ")[-1]
						month = web_title.split(" ")[-2]
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['The farmlander']:
						if "farmlande" in doc["docname"] and not "plan" in doc["docname"]:
							print("-")
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.rstrip("SouthNr ")
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							print(year)
							print(month)
							if  month in seas_dict.keys():
								season = str(month)
								my_date=dateparser.parse("01 "+seas_dict[month]+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								if month=="Novmber":
									month = "November"
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['The Eastbourne herald']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ["Pacific powerBoat covering Australia and New Zealand"]:
						if "ppb" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if web_title in ["PWC"]:
								year = "2016"
								month = "February"
							else:
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-3]
							if "/" in web_title:
								month = web_title.split(" ")[-2].split("/")[0]
							if month in short_month_dict.keys():
								month = short_month_dict[month]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Alloy boat magazine']:
						if doc["docname"].startswith("allo"):
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							issue = web_title.split(" ")[-1]	
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['At the bar']:

							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month:
								month = month.split("/")[0]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['NZ manufacturer success through innovation']:
						if "nz" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title=web_title.rstrip("final")
							print(web_title)
							if "/" in web_title:
								web_title = web_title.split("/")[-1]
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if not year.isdigit() and month not in months_dictionary.keys():
								month = web_title.split(" ")[-1]
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")

							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Kete korero']:
						# if "" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							if doc["docname"] == "kete_-_augoct_2011":
								month = "August"
								year = "2011"
							if doc["docname"] == "dec_2011":
								month = "December"
								year = "2011"

							# year = web_title.split(" ")[-1]
							# month = web_title.split(" ")[-2].capitalize()
							my_correct_base= web_title.split("-")[0].rstrip(" ")
							other_part = web_title.split("-")[-1].lstrip(" ")
							year = my_correct_base.split(" ")[-1]
							if not len(year)==4:
								month = str(year)
								year = other_part.split(" ")[-1]
							else:
								month=my_correct_base.split(" ")[-2].capitalize()
							if not month in months_dictionary.keys():
								month = short_month_dict[month.upper()]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						# else:
						# 	others.append(doc["docname"])
					if issuu in ['Kaleidoscope Kristin community']:
						if (doc["docname"].startswith("kri") or doc["docname"].startswith("kale")) and not "handbo" in doc["docname"] and not "prospectus" in doc["docname"] and not "guide" in doc["docname"] and not "sch" in doc["docname"]:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								print(published)		
							except:
								web_title = request_title(pdf_url)	

							web_title = web_title.strip("-")
							my_title_list = web_title.split(" ")
							print(my_title_list)
							if doc["docname"] == "kristin_kaleidoscope_magazine_issue_69_jul20":
								issue = "69"
								year= "2020"
								month = "July"
							elif doc["docname"] == "kri97298_kaleidoscope_56":
								issue = "56"
								year = "2012"
								month = "01"
							elif doc["docname"] == "kaleideoscope_november_2015":
								issue = "62"
								year = "2015"
								month = "November"
							elif doc["docname"] == "kristin_kaleidoscope_issuu_digital_lo-res":
								issue = "70"
								year = "2021"
								month = "July"
							else:

								if  my_title_list[-2].lower() == "issue":
									issue = my_title_list[-1]
									month = dateparser.parse(published_stamp).strftime("%B")
									year = dateparser.parse(published_stamp).strftime("%Y")

								elif len(my_title_list)>3 and my_title_list[-4].lower() == "issue":
									issue = my_title_list[-3]
									year = web_title.split(" ")[-1]
									month = web_title.split(" ")[-2]

								elif len(my_title_list[-1])==4:
									year = web_title.split(" ")[-1]
									month = web_title.split(" ")[-2]
							if "/" in month:
										month = month.split("/")[0]
							if month is seas_dict.keys():
								season = str(month)
								month = seas_dict[month]

							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
	
						else:
							others.append(doc["docname"])
					if issuu in ['Channel North Shore']:
						# print(doc["docname"])
						if  ("cmag" in  doc["docname"] or "channel" in doc["docname"] or doc["docname"]=="issue_4") and not "bcmag" in doc["docname"] and not "bchan" in doc["docname"] and not "browns" in doc["docname"]:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)		
							except:
								web_title = request_title(pdf_url)	

							# print(web_title)
							my_title_list = web_title.split(" ")
							print(my_title_list)
							if web_title == 'Channel Magazine' or web_title=="Channel":
								month = dateparser.parse(published_stamp).strftime("%B")
								year = dateparser.parse(published_stamp).strftime("%Y")
							elif my_title_list[-2].lower() == "issue":
								issue = my_title_list[-1]
								year = my_title_list[-3]
								month = my_title_list[-4]
							else:
								year = web_title.split(" ")[-1]
								if "/" in year:
									year = year.split("/")[-1]

								month = web_title.split(" ")[-2]
								if "/" in month:
									month = month.split("/")[-1]
								if "-" in month:
									month = month.split("-")[-1]
								try:
									if my_title_list[-4].lower() == "issue":
										issue =  my_title_list[-3]
								except Exception as e:
									pass
							if issue:
								issue=issue.strip(", ")
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Covernote IBANZ']:
						if "covern" in doc["docname"]:

							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.rstrip("Iissue ")
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							print(month)
							if "/" in month:
								month = month.split("/")[-1]
							print(month)
							if month in short_month_dict.keys():
								month = short_month_dict[month]
							print(month)
							if month.lower() == "issue":
								month =web_title.split(" ")[-3]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
									
					if issuu in ['AUT Millennium magazine']:
						print(issuu)
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
								number = web_title.split(" ")[-1]
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
					

					
					if issuu in ["PUSH"]:
							print("here")
	
							web_title,published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							print(my_date)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
										#######DO NOT REMOVE, USE IS WHEN ADDING NEW TITLE#######################
					if issuu in ['Debate']:
							web_year = None
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							print(web_title)
							issue = web_title.split("|")[1].lstrip("Issue ").rstrip(" ")
							my_date=dateparser.parse("01 " + month + year, settings ={'DATE_ORDER': 'DMY'})
				
					if issuu in ['SLANZA collected']:
						print("SLANZA")
						if not "guide" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							issue = web_title.split("#")[-1]
							if doc["docname"] in ["collected_30readytopublish","collected31"]:
								year = "2023"
							else:						
								year = dateparser.parse(published_stamp).strftime("%Y")
							my_date=dateparser.parse("01 " + "01 "+ year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

				# print(my_date)
				if not my_date and my_date!=0:
					print("Check date parsing")
					quit()
				elif  my_date != "None" or my_date==0:
					if my_date!=0:
						logger.debug(my_date.strftime("%d %B %Y"))
						try:
							my_date_stamp = mktime(my_date.timetuple())


						except OverflowError:
							overflow_flag = True
						print(alma_last_representation_list[0])
						if alma_last_representation_list[1] == 0:
							new_title = str(issuu)
						else:
							new_title = None
						print(my_date_stamp)
						print(my_dates)
						if overflow_flag or (my_date_stamp > alma_last_representation_list[0] and my_date.strftime("%d %B %Y") not in my_dates) or issuu==new_title or issuu in ["Debate","The Observer","Playmarket annual","Channel North Shore"]:
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
								if issuu in ["PUSH",'Debate','Explore south discover the South Island','New Zealand alpaca',"What's the story",'Onfilm',"Guano the Bats programme",'AUT Millennium flame',"AUT Millennium magazine",'Channel North Shore','Kaleidoscope Kristin community',"Kete korero","SLANZA collected","NZ manufacturer success through innovation",'At the bar','Alloy boat magazine',"The Eastbourne herald","Pacific powerBoat covering Australia and New Zealand","The farmlander",'Featherston phoenix','New Zealand freemason',"Heritage New Zealand","The lion Mount Albert Grammar School","The Orchardist","Heritage quarterly heritage","Heritage New Zealand",'NZGrower',"Ōtaki street scene",'Otaki today Nga korero o Otaki','Canterbury farming','Kia ora India',"Covernote IBANZ","The maritime worker Wellington branch","The maritimes newsletter of the Maritime Union of New Zealand","Nelson magazine","New Zealand Business and Parliament Trust","NZBPT news",'Midwife Aotearoa New Zealand','Chat 21 Down Syndrome community',"Nourish magazine", 'Academic freedom survey' 'New Zealand apparel trade directory','Playmarket annual','Real Estate',"The Observer","Showcircuit ultimate equestrian magazine","Salient Victoria University","Finalist stories",'Tract  landscape and architecture research work',"Eastlife Howick, Botany, Pakuranga and surrounds",'Design and build South East','Rural living handbook',"Avenues the magazine Christchurch lives by","Family times",'Agedplus village business','Agedplus village',"Restaurant and cafe buyer guide","Restaurant and cafe","F and B technology","Fennec","New Zealand apparel",'Hotel',"Supermarketnews","Kamo connect",'Art Beat Christchurch and Canterbury', 'Otuihau News', "Auto channel",'Luminate festival', "Rodnik Russian Cultural Herald",'Te panui runaka','Pipiwharauroa',"Prospectus imagine your future","Nexus","Joiners magazine",'B + d = xin zhu, zhu zin',"Nelson City guide","The MAP",'Leaders','The Fringe',"Yearbook","St Josephs Maori Girls College","Tira ora","Dawn chorus","Learning Auckland",'Student voice','Arthritis annual review report','Joint support'] and my_dict["day"]=="01":
									my_dict["day"]=None
								if issuu in ['Debate',"What's the story",'AUT Millennium flame',"SLANZA collected",'Alloy boat magazine',"Ōtaki street scene","Carterton and South Wairarapa street scene","Heritage quarterly heritage","Heritage New Zealand","New Zealand Business and Parliament Trust",'Playmarket annual',"Salient Victoria University","Finalist stories",'Tract  landscape and architecture research work','Design and build South East',"Restaurant and cafe buyer guide","Fennec",'Luminate festival',"Rodnik Russian Cultural Herald","Prospectus imagine your future",'Nexus','B + d = xin zhu, zhu zin',"Chat 21 Down Syndrome community","Nelson City guide",'Leaders',"Yearbook","St Josephs Maori Girls College","Tira ora",'New Zealand apparel trade directory','Learning Auckland', 'Academic freedom survey','Arthritis annual review report'] and (my_dict["season"] or my_dict["month"]=="January" ):
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

								if alma_last_representation_list[0]!=0:
									if issue:

										print(alma_last_representation_list[2])
										print(year)
										print(issue)
										if not (year > alma_last_representation_list[2]["year"] or (year==alma_last_representation_list[2]["year"] and issue> alma_last_representation_list[2]["issue"]))and issuu not in ['Build & renovate today',"Awhi",'Inspect - industrial and logistics',"Concrete"]:
											my_dict={}
									elif  number:
										if not (year > alma_last_representation_list[2]["year"] or (year==alma_last_representation_list[2]["year"] and number> alma_last_representation_list[2]["number"])) and issuu not in ['Asset', "Nexus"]:
											my_dict={}

					if not my_dict in my_dict_list and my_dict !={}:
							my_dict_list.append(my_dict)


	print(my_dict_list)
	for el in others:
		if el not in my_docnames:
			with open(os.path.join(report_folder_images, issuu+"_worked_out2.txt"),"a") as f:
				f.write(el)
				f.write("\n")
	for ind,pub in enumerate(my_dict_list):
		flag_to_do = False
		if not check_for_payment(pub["url"]):

			end_flag = False
			size_dictionary ={}
			max_pages = 0
			for i in range(500):
				if not end_flag:
					try:
						print("Collecting page ",i+1)
						
						my_link=page_url+pub["document_id"]+page_url_part2+str(i+1)+".jpg"
						print(my_link)
						r = requests.head(my_link,verify= False)
						if r.status_code == 403:
							end_flag = True
						else:
							max_pages=i+1
							r = requests.head(my_link,verify=False)
							print(r.text)
							size_dictionary["page_"+str(i+1)+".jpg"]=r.headers["Content-Length"]
							# try:
							wget.download(my_link, out =file_folder)
							# print("here1")
							# except:
							# 	print("failed to wget")
							# 	r = requests.get(my_link, stream = True,verify=False)
							# 	with open("page_"+str(i+1)+".jpg","wb") as img:
							# 		for chunk in r.iter_content(chunk_size=1024):
							# 				if chunk:
							# 					img.write(chunk)
					except urllib.error.HTTPError as e:
						print("here3")
						print(str(e))
					except Exception as e:
						print(str(e))

			my_filenames = os.listdir(file_folder)
			print(my_filenames)
			print(len(my_filenames))
			print(max_pages)
			if len(my_filenames)<max_pages:
				quit()
			for image in my_filenames:
				fileinfo = filetype.guess(os.path.join(file_folder, image))# new
				extens = fileinfo.extension#new
				if os.path.getsize(os.path.join(file_folder, image)) == int(size_dictionary[image]):
					shutil.move(os.path.join(file_folder, image),os.path.join(file_folder, "page_" + image.split('.')[0].split("_")[1].zfill(3)+"."+extens))#".jpg" new
				else:
					quit()

			enum_a, enum_b, enum_c, chron_i, chron_j, chron_k=parse_final_dictionary({"issue":pub["issue"], "volume":pub["volume"], "number":pub["number"],"season":pub["season"],"day":pub["day"],"month_string": pub["month"],"year":pub["year"],"term":pub["term"]}) 
			my_design = description_maker.make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
			pub["design"] = my_design
			print(my_design)
			flname = os.path.join(file_folder, os.listdir(file_folder)[0])
			new_filename = flname.replace("","_")
			try:
				shutil.move(flname, new_filename)
			except Exception as e:
				print(str(e))
			my_sip = SIPMaker(issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design, file_sip_folder)
			if my_sip.flag:
				for el in os.listdir(file_folder):
					os.remove(os.path.join(file_folder,el))
				my_item = ItemMaker()
				my_item.item_routine( issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design)
				if  not pub["design"]:
						pub["design"] =my_design
				with open(os.path.join(report_folder_images,issuu+".txt"),"a") as f:
					f.write(pub["design"])
					f.write("\n")

				with open(os.path.join(report_folder_images, issuu+"_worked_out.txt"),"a") as f:
					f.write(pub["docname"])
					f.write("\n")
				with open("new_issues_viz_temp_{}.txt".format(dt.now().strftime("%Y_%m_%d")),"a") as f:
					f.write(issuu)
					f.write("||")				
					f.write(pub["docname"])
					f.write("||")
					f.write(pub["url"])
					f.write("||")
					f.write(pub["document_id"])
					f.write("||")
					f.write(pub["design"])
					f.write("||")
					f.write(os.path.join(rosetta_folder, my_sip.sip_name_folder))
					f.write("||")
					f.write(my_sip.sip_name_folder)
					f.write("\n")

		else:
			
		 	print("Payment detected")

	

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
	driver.close()
	covers_routine()




if __name__ == "__main__":			
	main()
