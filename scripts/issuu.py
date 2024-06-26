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
from issuu_cover_displayer_all import routine as covers_routine
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from time import mktime, sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from sys import platform
from selenium.common import exceptions
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from rosetta_sip_factory.sip_builder import build_sip
from selenium.webdriver.common.action_chains import ActionChains
from description_maker import make_description
import description_maker
from issuu_dict import issuu_dict
from my_settings import  to_send_email, temp_folder,temp_sip_folder, email_address_line, report_folder, template_folder,logging, rosetta_folder, seas_dict, term_dict, months, reversed_season, months_dictionary,short_month_dict, not_processed_files, email_log, reversed_term, issue_dict
from my_settings  import sip_folder
# os.environ['REQUESTS_CA_BUNDLE'] = os.path.join( r'C:\Users\Korotesv\AppData\Roaming\Python\Python310\site-packages\certifi', 'ZscalerRootCertificate-2048-SHA256.crt')
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\alma_tools')
from alma_tools import AlmaTools
from email_maker import Gen_Emails
import last_representation_getter
import send_email
import json 

# if dt.now().strftime("%m") in ["11","12","1"]:
# 		seas_dict ["Summer"]="December"
# 		seas_dict["summer"] = "December"
# 		seas_dict["Raumati"]="December"Z
# 		seas_dict["Raumati"]="December"


fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.helperApps.alwaysAsk.force", False)
fp.set_preference("browser.download.dir", temp_folder)
fp.set_preference("browser.download.useDownloadDir",True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
fp.set_preference("pdfjs.disabled",True)
fp.set_preference("browser.download.manager.showWhenStarting",False)

# options = Options()
# options.headless = True

driver = webdriver.Firefox(firefox_profile = fp)#, options=options)

prefs = {
  "download.default_directory": temp_folder,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "plugins.always_open_pdf_externally": True
}

# options = Options()
# options.add_experimental_option("prefs", prefs)
# options.add_argument("--start-maximized");
# # options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("disable-infobars")
# options.add_argument("--disable-extensions")
# options.add_argument("--disable-dev-shm-usage") #overcome limited resource problems
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)

#driver =webdriver.Chrome(chrome_options=options)


logger = logging.getLogger(__name__)
base_url = r"https://issuu.com/"
test_url = r"https://issuu.com/dressagenzbulletin"
search_url = r"https://search.issuu.com/api/2_0/document"
# page_url = r"https://image.isu.pub/"
# page_url_part2 = "/jpg/page_"
pdf_url_part2 =r"/docs/"
key = "prod"


year_now =dt.now().strftime('%Y')
last_year =str(int(dt.now().strftime('%Y'))-1)


try:
	driver.get(test_url)
except Exception as e:
	print(str(e))
driver.implicitly_wait(10)
try:				
	driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept").click()
except Exception as e:
	print(str(e))
	try:
		driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
	except Exception as e:
		print(str(e))




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
		print(key)
		my_alma.get_items(issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"])
		print(my_alma.xml_response_data)
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
			print(os.getcwd())
			self.sip_name_folder = self.pub_name.replace(" ","_") + "_"+self.description.replace(" ","").replace(".","_").replace("(","-").replace(")","-").replace(",","-").rstrip("-").rstrip("_")
			self.output_folder = os.path.join(sip_folder, self.sip_name_folder )			
			print(self.file_folder_place)
			print(self.output_folder)
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
									output_dir=self.output_folder, 
									exclude_file_char = ['fileOriginalPath','fileSizeBytes', 'fileModificationDate','fileCreationDate']
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
			os.chdir("scripts")
			print(os.getcwd())

def click_element(element):
    action = ActionChains(driver)
    action.move_to_element(element).click().perform()

def load_driver(url):
	print("called load driver")

	driver.get(url)
	driver.implicitly_wait(9)
	element_to_click = driver.find_element(By.ID, "app")
	click_element(element_to_click)
	driver.implicitly_wait(5)
	element_to_click = driver.find_element(By.TAG_NAME, "h1")
	click_element(element_to_click)
	driver.implicitly_wait(5)
	#change to [-2] when listing pages for backlogs as link will be ended with /2 ,/3,/4
	username = url.split("/")[-1]
	html = driver.page_source
	soup = bs(html, "html.parser")	
	links = soup.find_all("a", href=True)
	return (links, username)

def get_my_doc_json(url):

	links, username = load_driver(url)
	matched_links = []
	for link in links:
		#print(link)
		href = link.get("href")
		#print(href)
		if "{}/docs/".format(username) in href:
		    image_link = link.find("div").find("div").find("img").get("src")
	
		    image_id = image_link.split("/")[-3]
		    docname = href.split("/")[-1]
		    matched_links.append({"docname":docname, "documentId":image_id})
	# if matched_links == []:
	# 		links, username = load_driver(url)
	# 		matched_links = []
	# 		for link in links:
	# 			links = load_driver(url)
	# 			#print(link)
	# 			href = link.get("href")
	# 			#print(href)
	# 			if "{}/docs/".format(username) in href:
	# 			    image_link = link.find("div").find("div").find("img").get("src")
			
	# 			    image_id = image_link.split("/")[-3]
	# 			    docname = href.split("/")[-1]
	# 			    matched_links.append({"docname":docname, "documentId":image_id})
	print(matched_links)
	return matched_links


def scroll_down(driver):

    """
    A method for scrolling the page.
    Origin: #https://stackoverflow.com/questions/48850974/selenium-scroll-to-end-of-page-in-dynamically-loading-webpage
    """

    last_height = driver.execute_script("return document.body.scrollHeight")

    # while True:
    for i in range(3):

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(6)
        new_height = driver.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
        # #     break
        # last_height = new_height
from time import sleep

def scroll_slightly_down(driver, scroll_factor=0.25):
    """
    A method for scrolling the page slightly.
    Origin: #https://stackoverflow.com/questions/48850974/selenium-scroll-to-end-of-page-in-dynamically-loading-webpage
    
    Parameters:
    driver (WebDriver): The Selenium WebDriver instance.
    scroll_factor (float): The fraction of the screen height to scroll. Default is 0.25 (quarter of the screen).
    """
    current_height = driver.execute_script("return window.pageYOffset")
    window_height = driver.execute_script("return window.innerHeight")
    scroll_distance = window_height * scroll_factor
    target_height = current_height + scroll_distance

    driver.execute_script("window.scrollTo(0, {});".format(target_height))
    sleep(2)  # Adjust sleep time as needed



def sip_checker(sippath):

	"""Checks if met files are empty, or no_file
		Parameters:SS
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

	
def request_title(pdf_url):
	r=requests.get(pdf_url ,verify=False)
	my_soup = bs(r.text,"lxml")
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
	my_soup = bs(r.text,"html.parser")
	try:
		web_title = my_soup.find_all("h1")[0].text
	except:
		web_title = my_soup.find_all("h3")[0].text
	try:
		published_stamp = my_soup.find_all("time")[0].attrs["datetime"]
		published = my_soup.find_all("time")[0].text
	except:
		data = my_soup.find_all('script')[9]["data-json"]#, type='application/ld+json').text)
		json_object = json.loads(data)
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
            if fname.endswith('part') or fname.endswith('.crdownload'):
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
	sent_emails = []
	if issuu in ["Line of defence","Bunnings New Zealand",'Diabetes wellness','Better breathing',"Human resources","Forest and bird",'Franchise New Zealand','Air chats',"New Zealand cameratalk",'Summerset scene','Family care',"Explore Dunedin","Wide Sky"]:#'World of wine',
		seas_dict ["Summer"]="December"
		seas_dict["summer"] = "December"
		seas_dict["Raumati"]="December"
		seas_dict["Raumati"]="December"
		seas_dict["Summers"] = "December"

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
#	r = requests.get(search_url,params = params, verify=False)
	#logger.setLevel("DEBUG")
	#logger.debug(r.text)
	my_dates = []
	try:
		# print(issuu)
		# print(os.path.join(report_folder,issuu + ".txt"))
		# print("here")
		with open(os.path.join(report_folder,issuu + ".txt"),"r")as f:
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
		with open(os.path.join(report_folder,issuu + "_worked_out.txt"),"r")as f:
			data = f.read()
		for el in data.split("\n")[:-1]:
			my_docnames.append(el)
		with open(os.path.join(report_folder,issuu + "_worked_out2.txt"),"r")as f:
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

	with open(email_log,"r") as f:
		data = f.read()
		for el in data.split("\n")[:-1]:
			sent_emails.append(el)

	my_docs =  get_my_doc_json(pub_url)
	if my_docs == []:
		scroll_down(driver)
		driver.implicitly_wait(3)
		element = driver.find_element_by_xpath("//html/body")
		actions = ActionChains(driver)
		actions.move_to_element(element).click().perform()
		driver.implicitly_wait(10)
		my_docs = get_my_doc_json(pub_url)
		# if my_docs == []:
		# 	element= driver.find_element(By.XPATH, "//div[@class='if-container']")
		# 	actions = ActionChains(driver)
		# 	actions.move_to_element(element).click().perform()
		# 	driver.implicitly_wait(5)
		# 	my_docs = get_my_doc_json(pub_url)

	# my_json = r.json()
	# num_found = my_json["response"]["numFound"]
	my_dict_list = []
	# my_dict = {}
	# for ind in range(int(num_found)//100+2):
	# 	start_index = ((int(num_found)//100)-ind)*100
	# 	params["startIndex"]=start_index
	# 	r = requests.get(search_url, params, verify=False)
	# 	# print(r.url)
	# 	my_doc_json = r.json()["response"]["docs"]
	# 	logger.debug(my_doc_json)
		# my_doc_json.append({"docname":"ag_january_27_2022","documentId":0})
	print(my_docs)
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
				custom_design = None
				published_stamp = None
				others = []
				# print(doc["docname"])
				pdf_url =base_url+issuu_dict[issuu]["username"]+pdf_url_part2+doc["docname"]
				# print(doc["docname"])
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
					if issuu in ['Malvern news']:
						if "stone" in doc["docname"] or "issue" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.lstrip("Malvern News - ").rstrip(" - Christmas Issu").rstrip(" - Christmas Issue")
							print(web_title)
							issue = web_title.split(" ")[1]
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2].capitalize()
							day = web_title.lower().split(" ")[-3].strip("-thst")
							if "," in issue:
								issue = issue.replace(",","")
							elif not web_title.lower().startswith("issue"):
								issue = None
								my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})


							# print(issue)
							# print(issue.isdigit())
							# if not issue.isdigit():
							# 	issue = None
								#my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})	
							if issue and not issue.startswith("2"):
								my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

							else:
								others.append(doc["docname"])
						else:
							others.append(doc["docname"])




					if issuu in ['Rolleston news']:
						if "stone" in doc["docname"] or "issue" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.rstrip("Malvern News - ")
							print(web_title)
							issue = web_title.split(" ")[1]
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2].capitalize()
							day = web_title.lower().split(" ")[-3].strip("-thst")
							if not web_title.lower().startswith("issue"):
								issue = None
								my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							elif not "," in issue:
								if issue.startswith("2") or issue in ["193","194","195","196","197","198"]:
									my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								others.append(doc["docname"])
						else:
							others.append(doc["docname"])

					if issuu in ['Academic freedom survey']:

							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0]							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})

					
					if issuu in ["Purongo a Tau annual report"]:
						if "annual" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							year = re.findall(r'\d{4}', web_title)[0]							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Water']:
						if not "npr" in doc["docname"] and not "directory" in doc["docname"]  and  not "competency" in doc["docname"] and  not "naviga" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(web_title)
							title_words = web_title.split(" ")
							try:
								issue = re.findall(r'\s(\d{3})\s', web_title)[0]
							except:
								pass
							try:	
								year = re.findall(r'\d{4}', web_title)[0]
							except:
								pass
							for wrd in title_words:
								print(wrd)
								if "/" in wrd:
								    wrd = wrd.split("/")[0]
								if wrd in months_dictionary.keys():
									month = str(wrd)
							if not month or not year:
								print("here777")
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
								month = dateparser.parse(published_stamp).strftime("%B")	
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Water directory']:
						if "directory" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							if "/" in year:
								year = year.split("/")[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['National performance review']:
						if "npr" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							print(web_title)						
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])


					if issuu in ['Lizard News']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Cruise news']:
					 	if "cruise" in doc["docname"] and "news" in doc["docname"]:
					 		print(doc["docname"])
					 		web_title = request_title(pdf_url)
					 		print(web_title)
					 		year = web_title.split(" ")[-1]
					 		month = web_title.split(" ")[-2]
					 		my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					 	else:
					 		others.append(doc["docname"])
					if issuu in ['NZsecurity']:
					 	if "nzsm" in doc["docname"]:
					 		print(doc["docname"])
					 		web_title = request_title(pdf_url)
					 		print(web_title)
					 		year = web_title.split(" ")[-1]
					 		month = web_title.split(" ")[-2]
					 		print(year)
					 		print(month)
					 		if "-" in month:
					 			month = month.split("-")[0]
					 			if not month in months_dictionary.keys():
					 				month = web_title.split(" ")[-2].split("-")[-1]

					 		if month in short_month_dict.keys():
					 			month = short_month_dict[month]
					 		if year == "20201":
					 			year = "2021"
					 		


					 		if web_title.split(" ")[-3] in short_month_dict:
					 			month = web_title.split(" ")[-3].split("-")[-1]
					 		print(month)
					 		my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					 	else:
					 		others.append(doc["docname"])
					if issuu in ["Line of defence"]:
						if "lod" in doc["docname"] and not "media" in doc["docname"] and not "kit" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							if "(" in season:
								season =web_title.split(" ")[-3]
							print(season)
							if "/" in year:
								year="20"+year.split("/")[-1]

							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Fire NZ']:
					 	if "firenz" in doc["docname"] or  "fnzm" in doc["docname"]:
					 		print(doc["docname"])
					 		web_title = request_title(pdf_url)
					 		print(web_title)
					 		year = web_title.split(" ")[-1]
					 		month = web_title.split(" ")[-2]
							
					 		my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					 	else:
					 		others.append(doc["docname"])
					if issuu in ['Hauraki rail trail guide']:
						if "hauraki" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.rstrip("Gguide")
							print(web_title)
							year = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['Guardian property']:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							# year = web_title.split(" ")[-1]
							# month = web_title.split(" ")[-2]
							
							# my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})


					if issuu in ["The record"]:
						if doc["docname"].startswith("tr"):
							print(doc["docname"])
							year = doc["docname"].split("_")[-1]
							if len(year)==2:
								year =="20"+year
							month = short_month_dict[doc["docname"].split("_")[-3].upper()]
							day =doc["docname"].split("_")[-2]							
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Te Rā o Waitangi']:
						if "waitangi" in doc["docname"]:
							print(doc["docname"])
							year = re.findall(r'\d{4}', doc["docname"])[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:	
							others.append(doc["docname"])

					if issuu in ['Winepress the official magazine of Wine Marlborough']:
						if not "annual" in doc["docname"] and not doc["docname"].startswith("wp"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Irhace"]:
						if not "_kit_" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "-" in month:
								month = month.split("-")[0]
								if month.capitalize() in ["Dec","December"]:
									month = "Jan"
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Midwife Aotearoa New Zealand']:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							issue_list = re.findall(r'\d{3}', doc["docname"])[0]
							for el in issue_list:
								if len(el) >3 and len (el)<2:
									issue = str(el)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							print(issue, month, year)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Regulus']:
						if doc["docname"].startswith("reg"):
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
							except:
								web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							issue = web_title.split(" ")[-2].rstrip(",")
							for el in doc["docname"].split("_"):
								if el.capitalize() in months:
									month = str(el)
								elif el.capitalize() in short_month_dict.keys():
									month = short_month_dict[el.capitalize()]
							if not month:
								try:
									month = dateparser.parse(published_stamp).strftime("%m")
								except:
									pass
							if doc["docname"] in ["reg_2021_issue_3_lr"]:
								month = "November"
							if doc["docname"] in ["regulus_issue_2_lr"]:
								month = "August"
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Wide Sky']:
						if "wide" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							if "/" in year:
								year="20"+year.split("/")[-1]
							if doc["docname"] in ["widesky_online_issue"]:
								year = "2021"
								season = "Winter"
							
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Nelson weekly"]:
						if "nelwk" in doc["docname"] or "nelson_we" in doc["docname"] or "nw" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.rstrip("- Nelson wWeekly").lstrip("Nelson wWeekly-")
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
							my_date=dateparser.parse(day+ " " + month+" "+year, settings ={'DATE_ORDER': 'DMY'})
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
	
					if issuu in ['Annual report AFL']:
						if doc["docname"].startswith("aflnz") and "annual" in doc["docname"]:
							year = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Northland must do']:#!!!!WAS IN DIFFERENT GROUP
						if "northland" in doc["docname"]:
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							if "/" in year:
								year = year.split ("/")[-1]
							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
							others.append(doc["docname"])
					if issuu in ['Modern slavery statement']:
						if "" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Our place']:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							year = dateparser.parse(published_stamp).strftime("%Y")
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Summerset scene']:
						if "scene" in doc["docname"]:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
							except:
								web_title=request_title(pdf_url)
								published=None
								published_stamp=None
							web_title = web_title.rstrip(" ")
							print(web_title)
							if "," in web_title and "issue" in web_title.lower():
								issue = issue_dict[web_title.lower().split(" ")[-1]]
								web_title = web_title.split(",")[0].rstrip(" ")

							if len(web_title.split(" "))==4:
								year = web_title.split(" ")[-1]
								season = web_title.split(" ")[-2]
							if  len(web_title.split(" "))==3:
								print("!!!!!!!!!!!!!")
								season = web_title.split(" ")[-1]
								print(season)
								year = dateparser.parse(published_stamp).strftime("%Y")
								print(year)
							if  len(web_title.split(" "))==2:
								season = web_title.split(" ")[-1]
								year = dateparser.parse(published_stamp).strftime("%Y")
								month = dateparser.parse(published_stamp).strftime("%m")
								season = reversed_season[month]
							if season == "Summers":
								season = "Summer"
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['The specialist']:
						if "spec" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							title_words = web_title.split(" ")
							for el in title_words:
								if el in months_dictionary.keys():
									month = months_dictionary[el]
								elif el.isdigit():
									if len(el)==4:
										year = str(el)
									if len(el)<4:
										issue = str(el)
							if not month or not year:
								web_title, published, published_stamp = request_title_date(pdf_url)
								if not month:
									month = dateparser.parse(published_stamp).strftime("%m")
								if not year:
									year = dateparser.parse(published_stamp).strftime("%Y")

							print(issue,month, year)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Inspect - industrial and logistics']:
						if "inspect" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							title_list = web_title.split(" ")
							new_web_title=""
							for el in title_list:
								if not el in ["Inspect", "inspect"]:
									new_web_title+=el
									new_web_title+= " "
							web_title = new_web_title.rstrip(" ")
							print(web_title)
							year = web_title.split(" ")[-1]
							# issue = web_title.split(" ")[-1].strip("#")
							issue = web_title.split(" ")[-2]
							print(issue)
							print(year)
							my_date = 0
						else:
							others.append(doc["docname"])
		
					if issuu in ['Farmers weekly']:
						if (doc["docname"].startswith("fw_") or doc["docname"].endswith("issue")) and not ("ag_ed") in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							day = web_title.split(" ")[-2].strip(",").strip("th")
							month = web_title.split(" ")[-3]						
							my_date=dateparser.parse(day +" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["The lampstand"]:
						if "lamp" in doc["docname"] or doc["docname"].startswith("ls"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					
					if issuu in ['New Zealand cameratalk']:
						if "ct" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							if "-" in web_title:
								month = web_title.split("-")[-1].strip(" ").rstrip(year)
							else:
								month = web_title.split(" ")[-2]
								
							
							print(month)
							print(year)
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
							others.append(doc["docname"])
					if issuu in ['Prospectus']:
						if "pros" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split("-")[-1]
							if "/"	in year:
								year = year.split("/")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["The Learning Connexions graduation"]:
						if "grad" in doc["docname"] and "book" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year= re.findall(r'\d{4}', web_title)[0].rstrip(" ")
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Te Korowai"]:
						if "korowai" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							issue = web_title.split(" ")[-1]
							print(issue)
							
							# my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["The Hobson life and lifestyle"]:
						if "hobston" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in []:
						if "" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["The New Zealand mortgage mag"]:

						print(doc["docname"])

						web_title = request_title(pdf_url)
						print(web_title)
						if doc["docname"]=="tmm5_2022_digital":
							issue = "5"
							year = "2002"
							month = "December"

						elif doc["docname"] == "tmm2_march_2023_digital":
							issue = "2"
							year = "2023"	
							month = "march"	
							
						elif doc["docname"] == "tmm2_march_2023_digital":
							issue = "2"
							year = "2023"	
							month = "march"	

						else:
							if "TMM " in web_title:
								if not "/" in web_title:
								#year = web_title.split("_")[-1]
									issue = str(int(web_title.split(" ")[-1]))
									year = re.findall(r'\d{4}', doc["docname"])[0]
								else:

									month= web_title.split(" ")[-1].split("/")[0]
									year= web_title.split(" ")[-1].split("/")[-1]
								if not issue:
									issue = doc["docname"].split("_")[0].lstrip("tmm")
							# if "/" in web_title:
							# 	year = web_title.split("/")[-1]
							# 	issue = web_title.split("/")[-2]
							# else:	
							# 	year = web_title.split(" ")[-1]
							# 	issue = str(int(web_title.split(" ")[-2]))
							#month = term_dict[issue]				
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						print(my_date)

					if issuu in ["Te Hookioi e rere atu na"]:
						if "hookioi" in doc["docname"] or "issue" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							# my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Waterline the Bay of Plenty and Coromandel" ]:
						if doc["docname"].startswith("wl"):
								web_title = request_title(pdf_url)
								print(web_title)
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2]
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['New farm dairies']:
						if doc["docname"].startswith("nfd"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]						
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Coast and country news']:
						if doc["docname"].startswith("c") and not "field" in  doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Flavours of Christchurch"]:
						if "flavours" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%m")
							issue = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["What's hot Christchurch"]:
						if "whchc" in doc["docname"]:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							except:
								# web_title = request_title(pdf_url)
								#year = "2020"
								year = year_now
							issue = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Cityscape Christchurch here and now']:
						if "cityscape" in doc["docname"]:
							print(doc["docname"])
							print(pdf_url)
			
							year = doc["docname"].split("-")[-1]
							season = doc["docname"].split("-")[-2].capitalize()
							# if len(year)!=4:
							# 	web_title=request_title(pdf_url)
							if doc["docname"] =="cityscape-issue-109":
								year = "2022"
								month = "November"
								issue = "109"
								my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								if season in months_dictionary.keys():
									month = str(season)
									season = None
									my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

								else:

									my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

						else:
							others.append(doc["docname"])
					if issuu in ["Hort news"]:
						if doc["docname"].startswith("hn") or doc["docname"].startswith("hort"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							try:
								issue = re.findall(r'\d{2}', doc["docname"])[0]
							except:
								print("could not grab issue")
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Getting the basics right"]:
						if doc["docname"].startswith("gtbr"):
							try:
								issue = doc["docname"].split("_")[-1]
							except:
								pass
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]						
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Dairy news']:
						if doc["docname"].startswith("dn"):
							try:
								issue = re.findall(r'\d{3}', doc["docname"])[0]
							except:
								pass
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
							my_date=dateparser.parse(day+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['Rural news']:
						if doc["docname"].startswith("rn") and not "_sth" in doc["docname"]:
							print(doc["docname"])
							try:
								issue = re.findall(r'\d{3}', doc["docname"])[0]
							except:
								pass
							web_title = request_title(pdf_url)
							print(web_title)
							web_title = web_title.rstrip(" North Island")
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
							if doc["docname"] =="rn_780_july_18":
								year = "2023"
								month = "July"
								day ="18"
							my_date=dateparser.parse(day+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Navy today Royal New Zealand Navy']:
						if "navytoday" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							web_title = web_title.split("-")[-1].lstrip(" ")
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							issue = web_title.split(",")[0].split(" ")[1]
							if "/" in month:
								month = month.split("/")[0]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["RROGA news"]:
						if "rroga" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]				
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Air chats"]:
							# print(doc["docname"])
							web_title = request_title(pdf_url)
							# print(web_title)
							year = web_title.split(" ")[3]
							season = web_title.split(" ")[2]
							if "/" in year:
								year = year.split("/")[0]
							issue=re.findall(r'\d{2}', doc["docname"])[0]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ['Whenua Parininihi Ki Waitotara magazine']:
						if "whenua" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							issue = web_title.split(" ")[-1]
							year = dt.now().strftime("%Y")
							my_date = 0
						else:
							others.append(doc["docname"])
					if issuu in ['Annual report Parininihi']:
						if doc["docname"].startswith("pkw") and "annual" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year= re.findall(r'\d{4}', web_title)[0].rstrip(" ")
							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Annual report Te Korowai'] :
						if doc["docname"].startswith("te_ko") or doc["docname"].startswith("tk") and "annual" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year= re.findall(r'\d{4}', web_title)[0].rstrip(" ")
							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Hooked up']:
						if "hooked" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							issue  = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Off-site']:
						if "off" in doc["docname"] or "os" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.strip("()")
							year = web_title.split(" ")[-1]
							mnths = web_title.split(" ")[-2]
							if not year.isdigit():
								mnths = str(year)
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")							
							if "/" in mnths:
								month = mnths.split("/")[0]
								if month.isdigit():
									year = str(month)
									month = web_title.split(year)[0].split(" ")[1]
							if month.upper() in short_month_dict.keys():
								month = short_month_dict[month.upper()]

							if "issue" in  web_title.lower():
								issue = web_title.split(" ")[2]
							else:
								issue = web_title.split(" ")[1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Annual review taxpayers']:
						if "annual" in doc["docname"] and "review" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = re.findall(r'\d{4}', web_title)[0]
							
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in []:
						if "" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Annual report Mercury']:
						if "ar" in doc["docname"]:
							year = web_title.split(" ")[-1]				
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Interim report Mercury']:
						if ("interim" in doc["docname"] and "rep" in doc["docname"] or "ir" in doc["docname"]) and not "transc" in doc["docname"]:
							year = web_title.split(" ")[-1]				
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['New Zealand printer']:
						if "zealand" in doc["docname"]  and "printer" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							if "-" in web_title:
								year = web_title.split(" ")[4]
								month = web_title.split(" ")[3]
							else:
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Bunnings New Zealand']:
						print(doc["docname"])
						if "nz" in doc["docname"] and not "outdoor" in doc["docname"] and not "au_" in doc["docname"]:
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							season_month = web_title.split(" ")[-2]
							if season_month in seas_dict.keys():
								season = str(season_month)
								my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["Massive"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							issue  = web_title.split(" ")[-2]
							year = web_title.split(" ")[-1]
							# my_date=dateparser.parse("01 01" +year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Builders & contractors']:
						if "b_c" in doc["docname"] or "bc" in doc["docname"]  or "builder" in doc["docname"] or "constructor" in doc["docname"]:
							print(doc["docname"])
							web_title, published, published_stamp = request_title_date(pdf_url)
							print(web_title)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							issue  = web_title.split(" ")[-1].strip("#")
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

						else:
							others.append(doc["docname"])
					if issuu in ["Te korowai o Tangaroa"]:
						if "korowai" in  doc["docname"]:
							# print(pdf_url)
							web_title = request_title(pdf_url)

							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
							
					if issuu in ["Principals today"]:
						if doc["docname"][:2]=="pt":
							print(doc["docname"])
							web_title = request_title(pdf_url)
							year = str(year_now)
							month = dt.now().strftime("%B")
							month_number = dt.now().strftime("%m")
							term = reversed_term[month_number]



							# web_title, published, published_stamp = request_title_date(pdf_url)
							# year = dateparser.parse(published_stamp).strftime("%Y")
							# month = dateparser.parse(published_stamp).strftime("%B")
							# for el in term_dict.keys():
							# 	if el == month:
							# 		term = term_dictionary[el]
							if "#" in web_title:
								issue = web_title.split("#")[-1]
							else:
								issue = web_title.split(" ")[-1]
							# my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
							my_design = "iss."+issue +" ("+year+" term "+term+")"
							my_date = 0
						else:
							others.append(doc["docname"])
					if issuu in ["Canterbury today"]:
						if "ct" in doc["docname"]:
							web_title = request_title(pdf_url)
							year = dt.now().strftime("%Y")
							issue = web_title.split(" ")[-1]
							my_date = 0
						else:
							others.append(doc["docname"])							
					if issuu in ['Build & renovate today']:
						if "b_r" in doc["docname"] or doc["docname"][:2]=="br":
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = dt.now().strftime("%Y")
							if "#" in web_title:
								issue = web_title.split("#")[-1]
							else:
								issue = issue = web_title.split(" ")[-1]
							my_design = description_maker.make_description(None, number, None, year, None, None)
							my_date=0

						# else:
						# 	others.append(doc["docname"])
					if issuu in ['Hibiscus Matters']:
						print(doc["docname"])
						if "hibiscus" in doc["docname"] or "hm" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(web_title)
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
							print(day)
							if "_" in day:
								day_issue=str(day)
								day=day_issue.split("_")[-1]
								issue=day_issue.split("_")[0]
							else:
								issue = web_title.split(" ")[-4]
							year=web_title.split(" ")[-1]
							# 	year = web_title.split(" ")[-3].strip("_")
							# 	issue = web_title.split(" ")[-1]
							# if "_" in  web_title:
							# 	year = web_title.split(" ")[-3].strip("_")
							# 	issue = web_title.split(" ")[-1]
							# elif "-" in web_title:
							# 	year = web_title.split(" ")[5]
							# 	number = web_title.split(" ")[-1]
					# 		season = web_title.split(" ")[-2]
							print(day, month, year)
							my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Ram']:
							print(doc["docname"])
							try:
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							except:
								web_title = request_title(pdf_url)
								year = str(year_now)
							print(web_title)
							if "#" in web_title:
								issue = web_title.split("#")[1].split(" ")[0]
								my_monthes = web_title.split(" ")[-1]
								print(my_monthes)
								if "/" in my_monthes:
									monthes = my_monthes.strip("()").split("/")
								else:
									monthes = [my_monthes]
								print(monthes)
								for el in monthes:
									print(el)
									if el in months_dictionary:
										month = str(el)
								print(year)
								print(month)
								print(issue)
								my_design = description_maker.make_description(None, None, issue, year, month, None)
								print(my_design)
								if doc["docname"] == "ram_issue_6_fa_17a4381b0e837b":
									month = "August"

							# 	season = web_title.split(" ")[-2]
							else:
								issue = doc["docname"].split("_")[-1]
								year = dateparser.parse(published_stamp).strftime("%Y")
								month = dateparser.parse(published_stamp).strftime("%B")
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ['Junction handbook Puhoi - Waipu']:
						if "handbook" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							if "/" in year:
								year = year.split("/")[-1]
							if len(year) == 2:
								year= "20"+year
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
						 	others.append(doc["docname"])
					if issuu in ['Junction Puhoi to Waipu']:
						if not "handbook" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					
					if issuu in ['Pacific romance']:
						if "pacific_romance_" in doc["docname"] and not "cook_is" in doc["docname"] and not "niue" in doc["docname"]and not "vanuatu" in doc["docname"]and not "tahiti" in doc["docname"]and not "fiji" in doc["docname"] and not "samoa" in doc["docname"]and not "newcaledonia" in doc["docname"]and not "hawaii" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							# season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Islandtime']:
						if ("it_" in doc["docname"] or "islandtime") in doc["docname"] and not "special" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]							
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})

						else:
							others.append(doc["docname"])
						# 	month = web_title.split(" ")[-2]
						# else:
						# 	others.append(doc["docname"])

					if issuu in ['World of wine']:
						if "wine" in doc["docname"] and "world" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							print(year)
							if "-" in year:
								year = year.split("-")[0]
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
							
						else:
							others.append(doc["docname"])
					if issuu in ['The Shout New Zealand']:
						if "shout" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
							
					if issuu in ['FMCG business']:
						if "fmcg" in doc["docname"] and not "leaders" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(doc["docname"])
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "-" in month:
								month = month.split("-")[0]
							my_date=dateparser.parse("01 "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['FMCG business leaders forum special report']:
						if "fmcg" in doc["docname"] and  "leader" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(doc["docname"])
							print(web_title)
							year = web_title.split(" ")[-1]
							
							my_date=dateparser.parse("01 01 " + year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Hospitality business']:
						if "hospitality_business" in doc["docname"]:
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "-" in  month:
								print("here")
								month = month.split("-")[0]
							if month.upper() in  short_month_dict.keys():
								print("here")
								month = short_month_dict[month.upper()]
							my_date=dateparser.parse("01 "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])



					if issuu in ['Dairy farmer']:
						if "df_" in doc["docname"]:
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in  ['The G.B. weekly']:
						web_title = request_title(pdf_url)
						if len(web_title.split(" "))>4:
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[-3]
						else:
							year = doc["docname"][:4]
							left_part = doc["docname"].replace(year,"")
							day = re.findall(r'\d{2}', left_part)[0]
							month = left_part.replace(day," ").strip("_-").split(" ")[0]
						my_date=dateparser.parse(day+" "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
						print(my_date)
					if issuu in ['Diabetes wellness']:
						web_title = request_title(pdf_url)
						year = web_title.split(" ")[-1]
						season = web_title.split(" ")[-2]
						my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ['Destination Devonport']:
						if "destin" in doc["docname"] or "dd" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							year = web_title[-4:]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Construction excellence awards Connexis']:
						if "" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if  issuu in ["The Devonport Flagstaff"]:
						if "flag" in doc["docname"] or ("rang" in doc["docname"] and "5nov" in doc["docname"]):
							print(doc["docname"])

							web_title = request_title(pdf_url)
							print(web_title)
							web_title=web_title.lstrip("Devonport Flagstaff")
							day = web_title.split(" ")[0]
							month = web_title.split(" ")[1]
							year = web_title.split(" ")[2]
							my_date=dateparser.parse(day+" "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ["The Rangitoto Observer"]:
						if "rangi" in doc["docname"] or doc["docname"] == "issu_observer_20jan2023" or doc["docname"].startswith("ro")  or doc["docname"].startswith("issuu_observer") :
							print(doc["docname"])
							web_title = request_title(pdf_url)
							web_title = web_title.lstrip("Rangitoto Observer")
							day = web_title.split(" ")[0]
							month = web_title.split(" ")[1]
							year = web_title.split(" ")[2]
							my_date=dateparser.parse(day+" "+month+ " " + year, settings ={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
							others.append(doc["docname"])
					if issuu in ["Concrete"]:
						web_title, published, published_stamp = request_title_date(pdf_url)
						year = dateparser.parse(published_stamp).strftime("%Y")
						issue = doc["docname"].split("_")[-1]
						volume =doc["docname"].split("_")[-2]
						my_date=0
						my_design = description_maker.make_description(volume, None, issue, year, None, None)

					if issuu in ["Focus"]:
						web_title = request_title(pdf_url)
						year = web_title.split(" ")[-1]
						month = web_title.split(" ")[-2]
						number = re.findall(r"number (.*?),", web_title)[0]
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
	
					if issuu in ['Love your workspace']:
						print(doc["docname"])
						if "auckland" in doc["docname"] or "workspace_6" in doc["docname"]:
							web_title, published,published_stamp = request_title_date(pdf_url)
							# print(web_title, published, published_stamp)
							issue = web_title.split("#")[-1].split(" ")[0]
							my_date=dateparser.parse(published_stamp, settings ={'DATE_ORDER': 'YMD'})
						else:
							others.append(doc["docname"])

					if issuu in ['Love your workspace Christchurch']:
						print(doc["docname"])
						if "christ" in doc["docname"] and "workspace" in doc["docname"] and  not "auck" in doc["docname"]:
							web_title = request_title(pdf_url)
							if "issue" in doc["docname"]:
								issue = doc["docname"].split("_")[-2].lstrip("issue")
							year = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["Update Canterbury Employers"]:
						web_title, published,published_stamp = request_title_date(pdf_url)
						try:
							year = re.findall(r'\d{4}', web_title_cut)[0]
						except:
							year = published.split(" ")[-1]
						my_date=dateparser.parse(published_stamp, settings ={'DATE_ORDER': 'YMD'})

					if issuu in ["The sun Blenheim Marlborough"]:
						web_title = request_title(pdf_url)
						web_title = web_title.replace("The Blenheim Sun","").lstrip(" ").rstrip(" ")
						print(web_title, doc["docname"])
						print(web_title.split(" "))
						# docdate = re.findall(r'\d{6}', doc["docname"])[0]
						# year = "20"+docdate[:2]
						# month = docdate[2:4]
						# day =docdate[4:]
						# if year == "2021":
						# 	year="2022"
						try:
							month = web_title.split(" ")[1]
							year =web_title.split(" ")[-1]
							day = web_title.split(" ")[0]
							if not year.isdigit():
								web_title, published, published_stamp = request_title_date(pdf_url)
								year = dateparser.parse(published_stamp).strftime("%Y")
							else:
								if len(year)>4:
									year="20"+year[:2]
							print(year,month,day)
						except:
							web_title, published, published_stamp = request_title_date(pdf_url)
							year = dateparser.parse(published_stamp).strftime("%Y")
							month = dateparser.parse(published_stamp).strftime("%B")
							day =  dateparser.parse(published_stamp).strftime("%d")
						my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ['The bay waka']:
						if not "elections" in doc["docname"]:
							web_title = request_title(pdf_url)
							web_title_cut = web_title.split(",")[1].lstrip(" ")
							year = re.findall(r'\d{4}', web_title_cut)[0]
							issue = re.findall(r'\d{2}',web_title_cut)[0]
							season = web_title_cut.split(" ")[0]
							month_short = re.findall(r'[A-Z]{3}',web_title_cut)[0]
							month = short_month_dict[month_short]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['FYI']:
						if "fyi" in doc["docname"]:
							web_title = request_title(pdf_url)
							month = web_title.split(" ")[1]
							year =web_title.split(" ")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Drinksbiz']:
						if doc["docname"].startswith("db"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							month = web_title.split(" ")[-3]
							year =web_title.split(" ")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ['Better breathing']:
						print(doc["docname"])
						if not "report" in doc["docname"]:
							web_title = request_title(pdf_url)
							season = web_title.split(" ")[-2]
							year = web_title.split(" ")[-1]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ['ATC']:
						if "atc" in doc["docname"]:
							web_title = request_title(pdf_url)
							print(web_title)          
							year = re.findall(r'\d{4}', doc["docname"])[0]
							my_date=dateparser.parse("01 01 "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Annual report']:
						if "awhi" in doc["docname"]:
							if "report" in doc["docname"]:
								year = doc["docname"].split("_")[-1]
								month = dt.now().strftime("%B")
								my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["Awhi"]:
						print(doc["docname"])
						if "awhi" in doc["docname"]:
							if not "report" in doc["docname"] and not  "book" in doc["docname"]:
								web_title = request_title(pdf_url)
								print(web_title)
								issue = web_title.split(" ")[-1]
								my_date=0
								year = dt.now().strftime("%Y")
								my_design = description_maker.make_description(None, None, issue, None, None, None)
							else:
								others.append(doc["docname"])
						else:
							others.append(doc["docname"])
							
					if issuu in ["Schoolnews"]:
						if "snnz" in doc["docname"] and not "eotc" in doc["docname"] and not "media" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							web_title = web_title.replace(" - "," ").replace("-"," ").replace(","," ").replace("  "," ").lower()
							year = web_title.split(' ')[-1]
							term = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+ term_dict[term] + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
	
					if issuu in ["Food New Zealand"]:
						fnz_flag = False
						print(doc["docname"])
						if doc["docname"].startswith("fnz") or doc["docname"].startswith("food"):
							web_title = request_title(pdf_url)
							print(web_title)
							web_title_list = web_title.split(" ")
							if not "Media"  in web_title  in web_title:
								if doc["docname"] == "foodnzdec22jan23web":
									month = "December"
									year ="2022"
								if doc["docname"] == "foodnzfebmarch2023web":
									month = "February"
									year = "2023"
								if doc["docname"] == "foodnzaprilmay2023web":
									month = "April"
									year  = "2023"
								else:
									my_dt=doc["docname"].replace("foodnz","").replace("web","")
									try:
										year = re.findall(r'\d{4}', doc["docname"])[0]
									except:
										year = "20"+ re.findall(r'\d{2}', doc["docname"])[0]
									for el in short_month_dict.keys():
										if not fnz_flag:
											if el.lower() in doc["docname"]:
												month = str(el)
												fnz_flag =True
									if not month:
										for el in months_dictionary.keys():
											if not fnz_flag:
												if el.lower() in months_dictionary :
													month = str(el)
													fnz_flag = True
										# # if "." in web_title:
								# # 	year = re.findall(r" (.*?)\.",web_title)[0].split(" ")[-1]
								# else:
								# 	print(web_title_list)
								# 	for el in web_title_list:
								# 		if "/" in el:
								# 			month = str(el)
								# 	if "/" in month:
								# 		month = month.split("/")[0]
								# 	try:
								# 		year = re.findall(r'\d{4}', web_title)[0]
								# 	except:
								# 		try:
								# 			web_title, published, published_stamp = request_title_date(pdf_url)
								# 			year = dateparser.parse(published_stamp).strftime("%Y")
								# 		except:
								# 			year = dt.now().strftime("%Y")



								# 	month = web_title.split(year)[0].split(" ")[-1]
								print(month)
								print(year)

								my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
					if issuu in ["Te karaka"]:
						if "karaka" in doc["docname"]:
							# print(doc["docname"])
							web_title = request_title(pdf_url)
							# year = dt.now().strftime("%Y")
							# season = reversed_season[dt.now().strftime("%m")]
							number= web_title.split("|")[-1].lstrip(" ")
							year= web_title.split('|')[0].rstrip(" ").split(" ")[-1]
							season = web_title.split("/")[-1].split(" ")[0]
							# print(year)
							# print(season)
							my_date=dateparser.parse("01 "+ seas_dict[season] + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
							# quit()
					if issuu in ["Human resources"]:
						# print(doc["docname"])
						web_title = request_title(pdf_url)
						print(web_title)
						seas_year_vol_num = web_title.split(" - ")[1].split(" H")[0]
						print(seas_year_vol_num)
						if "Summer" in seas_year_vol_num or "Spring" in seas_year_vol_num or "Winter" in seas_year_vol_num or "Autumn" in seas_year_vol_num:
							season = seas_year_vol_num.split(" ")[0]			
							year = seas_year_vol_num.split(" ")[1]
						else:

							season = web_title.split(" - ")[0].split(" ")[-1]
							year = dt.now().strftime("%Y")
						volume = re.findall(r"Vol (.*?) ",seas_year_vol_num)[0].rstrip(".,: ")
						number = seas_year_vol_num.split("No")[-1].split(")")[0].lstrip(".").lstrip(" ")
						my_date=dateparser.parse("01 "+ seas_dict[season] + " "+year, settings ={'DATE_ORDER': 'DMY'})
					
					if issuu in ["Asset"]:
						web_title = request_title(pdf_url)
						# print(pdf_url)
						# print(web_title)
						year_month_issuu_number = " ".join(web_title.split(" ")[1:])
						year = year_month_issuu_number.split(" ")[-1]
						# print(year)
						issue_number_month = year_month_issuu_number.rstrip(year).rstrip(" ")
						print(issue_number_month)
						if len((issue_number_month).split(" ")) == 1:
							month = issue_number_month.capitalize()
						elif len((issue_number_month).split(" "))==2:
							if issue_number_month.split(" ")[0].capitalize() in months:
								month = issue_number_month.split(" ")[0].capitalize()
							elif issue_number_month.split(" ")[0].isdigit():
								issue_number = issue_number_month.split(" ")[0]
								if int(issue_number) > 4:
									issue = issue_number
								else:
									number = issue_number
						print(month, year, issue,number)
						if month:
							if month in seas_dict:
								my_date=dateparser.parse("01 "+ seas_dict[month] + " "+year, settings ={'DATE_ORDER': 'DMY'})
							else:
								my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							print("here2")
							my_date = 0
	
							



					if issuu in ["Forest and bird"]:
						if "f_b_" in doc["docname"]: 
							web_title = request_title(pdf_url)
							if not " kit " in web_title:
								year = web_title.split(" ")[-1]
								season= web_title.split(" ")[-2]
								issue = web_title.split(" ")[-3]
								# print(web_title)
								my_date=dateparser.parse("01 "+ seas_dict[season] + " "+year, settings ={'DATE_ORDER': 'DMY'})
								flag_ses = True
							else:
								others.append(doc["docname"])
						else:
							others.append(doc["docname"])								

					if issuu  in ["New Zealand winegrower official journal"]:
						print(doc["docname"])
						if "winegrower" in doc["docname"] or "wg" in doc["docname"]:
							web_title = request_title(pdf_url) 
							print(web_title)
							year = web_title.split(" ")[-1]
							monthes = web_title.split(" ")[-2]
							if "/" in monthes:
								month = monthes.split("/")[0]
							elif "-" in monthes:
								month = monthes.split("-")[0]
							else:
								month = str(monthes)
							my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["Army news"]:

						if "an" in doc["docname"] or "armynews" in doc["docname"]:
							
							web_title = request_title(pdf_url)
							print(web_title)
							print(doc["docname"])
							print("here!!!")
							try:
								issue = re.findall('\d{3}', doc["docname"])[0]
							except:
								print("no issue found")
							if "army news" in web_title.lower():
								print(web_title, doc["docname"])
								year = web_title.split(" ")[-1]
								month = web_title.split(" ")[-2]
								issue = web_title.split(" ")[-3].rstrip(",")
								if "/" in month:
									month = month.split("/")[0]
								my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["Air force news"]:
						if "airforcenews" in doc["docname"] or "afn" in doc['docname'] or ("air" and doc["docname"] and "force" in doc["docname"]):
							print(doc["docname"])
							if doc["docname"] in ["royal_new_zealand_air_force_air_for_d7b79f6bbd7be3"]:
								issue = "254"
							else:
								issue = re.findall('\d{3}', doc["docname"])[0]
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							if "/" in month:
								month = month.split("/")[0]
							print(year)
							print(month)
							my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])



					if issuu in  ["Franchise New Zealand"]:
						# if doc["docname"].startswith("fnz"):
							issue = re.findall('\d{4}', doc["docname"])[0][-2:]
							volume = re.findall('\d{4}', doc["docname"])[0][:2]
							print(pdf_url)
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							try:
								season = web_title.split(" ")[-2]
								my_date=dateparser.parse("01 "+ seas_dict[season] + " "+year, settings ={'DATE_ORDER': 'DMY'})
							except:

								season = web_title.split(" – ")[-1].split(" ")[0]
								print(web_title.split(" – "))
								print(season)
								print(seas_dict)
								print(seas_dict[season])
								my_date=dateparser.parse("01 "+ seas_dict[season] + " "+year, settings ={'DATE_ORDER': 'DMY'})


						
					if issuu in ["Family care"]:
						print(doc["docname"])
						print(web_title)
						web_title, published, published_stamp = request_title_date(pdf_url)
						year = dateparser.parse(published_stamp).strftime("%Y")
						month = dateparser.parse(published_stamp).strftime("%B")
						season = reversed_season[month]
						if "Issue" in web_title:
							if ":" in web_title:
								issue = web_title.split(":")[0].split(" ")[-1]
							else:
								issue = web_title.split(" ")[-1] 
						my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ["Better breathing"]:
						if not "annual" in doc["docname"]:
							web_title = request_title(pdf_url)
							year = web_title.split(" ")[-1]
							season = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+seas_dict[season]+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])
					if issuu in ['Active retirees']:
						#if "active" in doc["docname"] and "retirees" in doc["docname"] and not doc["docname"] in my_docnames:
							print(doc["docname"])
							# print(printdf_url)
							web_title = request_title(pdf_url)
							print(web_title)
							if "New Zealand" in web_title:
								#print(web_title)
								#print(doc["docname"])
								#Active Retires New Zealand - Winter 2023
								title = web_title.replace("Active Retirees New Zealand Magazine","").replace("Active Retires New Zealand - ","").replace("Active Retirees Magazine - New Zealand","").replace("Active Retirees ","").replace(" - New Zealand","").rstrip(" ")
								#year= re.findall('\d{4}', title)[0].rstrip(" ")
								# print(title)
								year = title.split(" ")[-1]
								if not year.isdigit():
									web_title,published,published_stamp = request_title_date(pdf_url)
									year = dateparser.parse(published_stamp).strftime("%Y")
								season = title.split(" ")[0]
								month_string = seas_dict[season]
								month = months_dictionary[month_string]
								flag_ses = True

								my_date=dateparser.parse("01 "+ month + " "+year, settings ={'DATE_ORDER': 'DMY'})
								# print(my_date)
					if issuu in ["Explore Dunedin"]:# {'publisher': 'Allied Press Ltd', 'web_title': 'Explore Dunedin \xa0', 'mms_id': '9919061063502836', 'holding_id': '22366692760002836', 'po_line': 'POL-167410', 'pattern': '', 'days': '', 'url': 'https://issuu.com/alliedpress/docs/exploredunedin2020', 'username': 'exploredunedin2020'},"]
						if "dunedin" in doc["docname"]:
							print(doc["docname"])
							web_title,published,published_stamp = request_title_date(pdf_url)
							print(web_title)
							if len(web_title.split(" "))==4:
								year = web_title.split(" ")[-1]
								season = web_title.split(" ")[-2]
							if len(web_title.split(" "))==2 or len(web_title.split(" "))==3:
								year = web_title.split(" ")[-1]
								month = dateparser.parse(published_stamp).strftime("%m")
								season = reversed_season[month]


							if "-" in year:
								year = year.split("-")[0]

							my_date=dateparser.parse("01 "+ seas_dict[season] + " "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["Ponsonby news"]:
						if "ponsonby_news_" in doc["docname"] and not doc["docname"] in my_docnames:
							web_title=request_title(pdf_url)
							print(doc["docname"])
							print(web_title)
							if doc["docname"] == "ponsonby_news_august_fri_29_july_final":
								my_date = dateparser.parse("01 August 2022", settings={'DATE_ORDER': 'DMY'})
							elif doc["docname"] == "ponsonby_news_april_23_website_updated":
								my_date = dateparser.parse("23 April 2023", settings={'DATE_ORDER': 'DMY'})	
							elif doc["docname"] == "ponsonby_news_august_2023_website":
								my_date = dateparser.parse("01 August 2023",settings={'DATE_ORDER': 'DMY'})
							elif doc["docname"] == "ponsonby_news_september_2023_website":
								my_date = dateparser.parse("01 September 2023",settings={'DATE_ORDER': 'DMY'})

							else:
								year  = doc["docname"].split("_")[-1]
								if len(year)==2:
									year = "20"+year
								month = doc["docname"].split("_")[-2].capitalize()
								if month in short_month_dict.keys():
									month = short_month_dict[month]
								my_date = dateparser.parse("01 "+month + " " +year, settings={'DATE_ORDER': 'DMY'})
							print(my_date)
						else:
							others.append(doc["docname"])
		
					if issuu in ["Taranaki farming lifestyles"]:
						if "tfl" in doc["docname"]:
							my_date = dateparser.parse(doc["docname"].replace("tfl_","01"),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Taranaki farming lifestyles, ",""))
						else:
							others.append(doc["docname"])
			
					if issuu in ["Hawke's Bay farming lifestyles"]:
						if "hbfl" in doc["docname"]:
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["Northern farming lifestyles"]:
						if "nfl" in doc["docname"]:
							my_date = dateparser.parse(doc["docname"].replace("nfl_","01"),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Northern Farming Lifestyles, ",""))
						else:
							others.append(doc["docname"])


					if issuu in ["Waikato farming lifestyles"]:
						if "wfl" in doc["docname"]:
							my_date = dateparser.parse(doc["docname"].replace("wfl_","01"),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Waikato farming lifestyles ",""))
						else:
							others.append(doc["docname"])
			
					if issuu in ["Hawke's Bay farming lifestyles"]:
						if "hbfl" in doc["docname"]:
							my_date = dateparser.parse(doc["docname"].replace("hbfl_","01"),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Hawke's Bay farming lifestyles ",""))
						else:
							others.append(doc["docname"])
					if issuu in ["Northern farming lifestyles"]:
						if "nfl" in doc["docname"]:
							my_date = dateparser.parse(doc["docname"].replace("nfl_","01"),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Northern Farming Lifestyles, ",""))

					if issuu in ["The weekend lifestyler"]:
						if "wl" in doc["docname"] or "weekend_lifestyler" in doc["docname"]:
							print(doc["docname"])

							my_date = dateparser.parse(doc["docname"].replace("wl_",""),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								print(web_title)
								my_date=dateparser.parse(web_title.replace(",","").replace("The Weekend Lifestyler ","").replace("th",""))
						else:
							others.append(doc["docname"])								
					if issuu in ["Manawatu farming lifestyles"]:
						if "mfl" in doc["docname"]:
							my_date = dateparser.parse(doc["docname"].replace("mfl_","01"),settings={'DATE_ORDER': 'DMY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Manawatu Farming Lifestyles, ",""))
						else:
							others.append(doc["docname"])
					if issuu in ["Education Gazette"]:
						#print(doc["docname"])
						web_title, published, published_stamp = request_title_date(pdf_url)
						year = dateparser.parse(published_stamp).strftime("%Y")
						r = requests.get(pdf_url, verify=False)
						my_vol_num = re.sub("[A-Za-z]", "", web_title).rstrip(" ").lstrip(' ')
						try:

							volume = my_vol_num.split(".")[0]
							number = my_vol_num.split('.')[1]
							if not number.isdigit() and " " in number:
								number = number.split(" ")[0]
							print(volume)
							print(number)
							my_design = description_maker.make_description(volume, number, None, year, None, None)
							my_date =0
							#my_date=dateparser.parse("01 "+ "01" + " "+year, settings ={'DATE_ORDER': 'DMY'})
						except:
							with open('to_process_manually.txt',"a") as f:
								f.write(issuu+"|"+web_title+pdf_url)
								f.write("\n")

							my_date=None
						#print(my_date)	
					if issuu in ["Waimea Weekly"]:
						if "ww" in doc["docname"] and not "rural" in doc["docname"]and not "0219" in doc["docname"]:
								web_title = request_title(pdf_url)
								try:
									my_date=dateparser.parse(web_title)
								except:
									quit()
								# if not my_date:
								# 	print(web_title)
								# 	quit()
						else:
							others.append(doc["docname"])
					if issuu in ["DressageNZ bulletin"]:
						print(doc["docname"])
						web_title = request_title(pdf_url)
						web_title = web_title.rstrip(" ")
						print(web_title)
						year = web_title.split(" ")[-1]
						month = web_title.split(" ")[-2]
						issue = web_title.split(" ")[-3]
						if issue in months_dictionary.keys():
							month=str(issue)
							issue=web_title.split(" ")[-4]
						
						if "/" in month:
							month =month.split("/")[-1]	
						if "issue_59_april_may_2022" in doc["docname"]:
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-3]
							issue = web_title.split(" ")[-4]
						my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						#print(web_title)
								# print(my_pub)
							# print(my_date)
							# print(issue)
					if issuu in ["Weekend Sun"]:
						#print('Please wait, "Weekend sun" takes more time....')
						if doc["docname"].startswith("ws") and (year_now[2:] in doc["docname"] or last_year[2:] in doc["docname"]):
								web_title = request_title(pdf_url)
								print(doc["docname"])
								print(web_title)

								if "the weekend sun" in web_title.lower() and (year_now in web_title or last_year in web_title):
									web_title = web_title.lower().replace("the weekend sun","").lstrip('- ')
									year = web_title.split(" ")[-1]
									month = web_title.split(" ")[-2]
									day = web_title.split(" ")[-3]
									if  month == "septemnber":
										month = "September"
									if month == "apri":
										month = "April"
									print(year, month, day)
									my_date = dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
								# if "ws" in web_title.lower():
								# 	print(pdf_url)
						else:
							others.append(doc["docname"])
							
					if issuu in ["Kaipara lifestyler"]:
						if "kl" in doc["docname"] or doc["docname"].startswith("sl"):
							my_date = dateparser.parse(doc["docname"].replace("kl_","").replace("sl_",""),settings={'DATE_ORDER': 'MDY'})
							if not my_date:
								web_title = request_title(pdf_url)
								my_date=dateparser.parse(web_title.replace("Kaipara Lifestyler, ","").replace("Summer Lifestyler ",""))
						else:
							others.append(doc["docname"])

					if issuu in ['SALT']:
						if doc["docname"].startswith("salt"):
							print(doc["docname"])
							web_title = request_title(pdf_url)
							print(web_title)

							web_title = web_title.replace(", NZFTS","")
							#month_year = web_title.split(",")[1].rstrip(" ").lstrip()
							#month = month_year.split(" ")[0]
							# year = month_year.split(" ")[1]
							month = web_title.split(" ")[-2]
							year =web_title.split(" ")[-1]
							my_date=dateparser.parse("01 "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						else:
							others.append(doc["docname"])

					if issuu in ["The Guardian Motueka, Tasman and Golden Bay"]:
						#print("here")
						my_date = dateparser.parse(doc["docname"],settings={'DATE_ORDER': 'DMY'})
						if not my_date:
							print(doc["docname"])

							web_title = request_title(pdf_url)
							print(web_title)
							year = web_title.split(" ")[-1]
							month = web_title.split(" ")[-2]
							day = web_title.split(" ")[0]
							try:
								my_date =dateparser.parse(web_title,settings={'DATE_ORDER': 'DMY'})
							except:
								my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})

					if issuu in ["The Geraldine news"]:
						print(doc["docname"])
						web_title = request_title(pdf_url)
						print(web_title)
						if "-" in web_title:
							web_title = web_title.split("-")[0].rstrip(" ")
						year = web_title.split(".")[-1]
						month = web_title.split(".")[-2]
						day = web_title.split(" ")[-1].split(".")[0]				
						my_date=dateparser.parse(day+" "+month+" "+year, settings ={'DATE_ORDER': 'DMY'})
						print(my_date)
						
				if month:
					if "-" in month:
						month = month.split("-")[0]
					if "/" in month:
						month = month.split("/")[0]
				if not my_date and my_date!=0:
					print("Check date parsing")
					quit()
				elif my_date != "None" or my_date==0:
					#print(my_date)
					if my_date!=0:
						logger.debug(my_date.strftime("%d %B %Y"))
						try:
							my_date_stamp = mktime(my_date.timetuple())


						except OverflowError:
							print("here!!!!!!!")
							quit()
							overflow_flag = True
					#	print(alma_last_representation_list[0])
					#	print(my_date_stamp)
						#print(my_dates)
						if overflow_flag or (my_date_stamp > alma_last_representation_list[0] and my_date.strftime("%d %B %Y") not in my_dates) or issuu in ["The Geraldine news", "Franchise New Zealand"]:
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
								if issuu in ["Active retirees","Taranaki farming lifestyles","Waikato Farming Lifestyle","Hawke's Bay farming lifestyles","Northern farming lifestyles", "DressageNZ Bulletin","Manawatu farming lifestyles","Ponsonby news","Explore Dunedin","Down in Edin magazine","Family care","Franchise New Zealand","Air force news","New Zealand winegrower official journal","Forest and bird","Food New Zealand","Asset","Human resources","Schoolnews","Annual report",'ATC','Better breathing',"FYI","The bay waka","Update Canterbury Employers",'Love your workspace',"Focus",'Destination Devonport','Diabetes wellness','Dairy farmer','Hospitality business','FMCG business', 'FMCG business leaders forum special report','The Shout New Zealand','World of wine','Pacific romance','Junction handbook Puhoi - Waipu','Junction Puhoi to Waipu','Ram',"Canterbury today","Te korowai o Tangaroa","Principals today",'Builders & contractors',"Massive",'Bunnings New Zealand','Bunnings New Zealand','New Zealand printer','Annual report Mercury','Interim report Mercury','Annual review taxpayers',"Off-site",'Hooked up',"Air chats","RROGA news",'Navy today Royal New Zealand Navy','Cityscape Christchurch here and now',"What's hot Christchurch",'Coast and country news','Waterline the Bay of Plenty and Coromandel',"The Hobson life and lifestyle",'Prospectus',"The Learning Connexions graduation",'New Zealand cameratalk',"The lampstand","Waikato farming lifestyles","The specialist",'Summerset scene','Our place','Modern slavery statement',"Getting the basics right","Cityscape Christchurch here and now","What's hot Christchurch","New farm dairies",'Annual report AFL',"Northland must do","The New Zealand mortgage mag","Education Gazette","Army news","Love your workspace Christchurch","Nelson magazine","Wide Sky",'Regulus',"Irhace","Winepress the official magazine of Wine Marlborough","Drinksbiz",'Te Rā o Waitangi',"Annual report Parininihi","Annual report Te Korowai","Hort news",'Cruise news','NZsecurity',"Line of defence",'Fire NZ',"Hauraki rail trail guide","SALT","Lizard News","Water","Water directory", "National performance review","Purongo a Tau annual report", 'Academic freedom survey'] and my_dict["day"]=="01":
									my_dict["day"]=None
								if issuu in ["Explore Dunedin","Family care","Franchise New Zealand","Forest and bird","Human resources","Schoolnews","Annual report",'ATC','Better breathing',"Update Canterbury Employers",'Love your workspace','Destination Devonport','Diabetes wellness','World of wine','Pacific romance','Junction handbook Puhoi - Waipu','Annual report Mercury','Interim report Mercury','Annual review taxpayers','Hooked up',"Air chats","RROGA news",'Cityscape Christchurch here and now',"What's hot Christchurch",'Prospectus',"The Learning Connexions graduation","The lampstand",'Summerset scene','Our place','Modern slavery statement',"Principals today","Getting the basics right", 'FMCG business leaders forum special report', "What's hot Christchurch","New farm dairies",'Annual report AFL','Northland must do',"The New Zealand mortgage mag","DressageNZ bulletin","Massive","Education Gazette","Love your workspace Christchurch",'Te Rā o Waitangi',"Annual report Parininihi","Annual report Te Korowai","Hauraki rail trail guide" ,"Water directory", "National performance review","Purongo a Tau annual report",'Academic freedom survey']:
									my_dict["month"] = None
								if issuu in ["Asset"]:
									if not month or number:
										my_dict["month"] = None
								if issuu in ["Active retirees"]:
									if flag_ses:
										my_dict["month"] = None
										my_dict["season"] = reversed_season[month]

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
										if not (year > alma_last_representation_list[2]["year"] or (year==alma_last_representation_list[2]["year"] and issue> alma_last_representation_list[2]["issue"]))and issue in ['Build & renovate today',"Awhi",'Inspect - industrial and logistics',"Concrete","Principals today"]:
											my_dict={}
									elif  number:
										if not (year > alma_last_representation_list[2]["year"] or (year==alma_last_representation_list[2]["year"] and number> alma_last_representation_list[2]["number"]))and issue in ['Asset',"Education Gazette"]:
											my_dict={}

								#else:
									# if not issuu in ["Education Gazette"]:
									# 	my_dict={}
								if issue in ['Build & renovate today',"Awhi","Inspect - industrial and logistics"]:
									print(my_dict)

					if not my_dict in my_dict_list and my_dict !={}:
							my_dict_list.append(my_dict)




	for el in others:
		if el not in my_docnames:
			with open(os.path.join(report_folder, issuu+"_worked_out2.txt"),"a") as f:
				f.write(el)
				f.write("\n")
	for i,pub in enumerate(my_dict_list):
		email_fname = issuu+ ' ' +pub["web_title"].replace(" ","_")
		flag_to_do = False
		r=requests.get(pub["url"], verify=False)
		if len(re.findall("The publisher chose",r.text)) == 0:
			if len(os.listdir(temp_folder))!=0:
				print("files detected")

				for el in os.listdir(temp_folder):
					try:
						shutil.move(os.path.join(temp_folder,el), not_processed_files)
					except:
						os.remove(os.path.join(temp_folder,el))
			if pub["web_title"]=="":
				my_soup = bs(r.text, "lxml")
				web_title = my_soup.find_all("h1")[0].text
				my_dict_list[i]["web_title"] = web_title

			try:
				driver.get(pub["url"])
			except Exception as e:
				print(str(e))
			# driver.implicitly_wait(10)
			# try:
			# 	# print("here00")
			# 	# <a id="CybotCookiebotDialogBodyButtonAccept" class="CybotCookiebotDialogBodyButton" href="#" tabindex="0" style="padding-left: 12px; padding-right: 12px;" lang="en">Allow all cookies</a>
			# 	print("here000")
			# except Exception as e:
			# 	print(str(e))
			# 	try:				
			# 		driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept").click()
			# 	except Exception as e:
			# 		print(str(e))
			# 		try:
			# 			driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
			# 		except Exception as e:
			# 			print(str(e))

			sleep(20)
			# try:	
			# 	driver.find_element(By.XPATH,"//button[contains(@aria-label, 'Download')]").click()
			# except Exception as e:
			# 	print("here11")
			try:
				#scroll_slightly_down(driver)
				sleep(20)
				driver.find_element(By.XPATH,"//button[contains(@aria-describedby, 'download_tooltip')]").click()
				# <button aria-describedby="download_tooltip" class="sc-1an4lpe-1 jPjQNo" style=""><div aria-hidden="true" class="sc-1an4lpe-0 bQChXH"><svg fill="currentColor" height="24" viewBox="0 0 24 24" width="24" role="img"><path d="M11.8484 15.3864C11.8664 15.4081 11.8894 15.4257 11.9157 15.4378C11.9419 15.4498 11.9708 15.4561 12 15.4561C12.0292 15.4561 12.0581 15.4498 12.0843 15.4378C12.1106 15.4257 12.1336 15.4081 12.1516 15.3864L14.8468 12.1659C14.9455 12.0477 14.8564 11.8727 14.6952 11.8727H12.912V4.18182C12.912 4.08182 12.8254 4 12.7195 4H11.2757C11.1698 4 11.0832 4.08182 11.0832 4.18182V11.8705H9.30481C9.14358 11.8705 9.05455 12.0455 9.15321 12.1636L11.8484 15.3864ZM19.8075 14.5909H18.3636C18.2578 14.5909 18.1711 14.6727 18.1711 14.7727V18.2727H5.82888V14.7727C5.82888 14.6727 5.74225 14.5909 5.63636 14.5909H4.19251C4.08663 14.5909 4 14.6727 4 14.7727V19.2727C4 19.675 4.34412 20 4.77005 20H19.2299C19.6559 20 20 19.675 20 19.2727V14.7727C20 14.6727 19.9134 14.5909 19.8075 14.5909Z"></path></svg></div>Download</button>

				sleep(40)
				# pyautogui.moveTo(720,670)
				# #pyautogui.moveTo(725,572)#Rhonda's big screen
				# # pyautogui.moveTo(1725,1000)#big screen save location
				# # pyautogui.moveTo(800,500)
				# # pyautogui.moveTo()
				# # pyautogui.move(1,1)
				# pyautogui.click()
				# # sleep(10)
				# # pyautogui.click()
				# #pyautogui.hotkey('enter')https://issuu.com/deputy_editorhttps://issuu.com/deputy_editor
				if len(os.listdir(temp_folder))!=1:
					sleep(20)
				if len(os.listdir(temp_folder))!=1:
					sleep(20)
					# try:
					# 	pyautogui.hotkey('tab')
					# 	pyautogui.hotkey('tab')
					# 	pyautogui.hotkey('tab')
					# 	pyautogui.hotkey('tab')
					# 	pyautogui.hoftkey('enter')
					# except:
					# 	pass

				seconds =download_wait(temp_folder)
				print("Downloading process took",seconds, "seconds")
				if len(os.listdir(temp_folder))==0:
					html = driver.page_source
					if "The specified key does not exist" in html:

						with open(os.path.join(report_folder,"was_not_downloaded.txt"),"a") as f:
							f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
							f.write("\n")
						with open(os.path.join(report_folder,"wrong_key_error.txt"),"a") as f:
							f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
							f.write("\n")
						with open(os.path.join(report_folder,"wrong_key_error.txt"),"a") as f:
								f.write(pub["docname"])
								f.write("\n")
						print(sent_emails)
						if not email_fname in sent_emails:
							try:
								print("here22")
								email_subject = "[ISSUU] No PDF link found for {} - {}".format(issuu, pub["web_title"])
								print(email_subject)
								email_message = '<body style="font-family:Calibri"><br><p>During the automated Issuu downloading process, we expected to find a link for downloading the following issue as a PDF, but it was not enabled:</p><br><p><ul><li><b>Title:</b> {}</li><li><b>Web designation:</b> {}</li><li><b>MMSID:</b> {}</li><li><b>URL for publication:</b> {}</li></ul></p></body>'.format(issuu, pub["web_title"], issuu_dict[issuu]["mms_id"], pub["url"])
								print(email_message)
								email_maker = Gen_Emails()
								email_maker.EmailGen(email_address_line, email_subject, email_message,  email_fname, to_send_email)
								with open (email_log,"a") as f:
									f.write(email_fname)
									f.write("\n")
							except Exception as e:
								print(str(e))





			except exceptions.NoSuchElementException:
				with open(os.path.join(report_folder,"was_not_downloaded.txt"),"a") as f:
					f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
					f.write("\n")
				with open(os.path.join(report_folder,"was_not_downloaded_docnames.txt"),"a") as f:
					f.write(pub["docname"])			
					f.write("\n")
			except Exception as e:
				print(str(e))
			for fname in os.listdir(temp_folder):
				if not fname.endswith('part'):
					flag_to_do = True
			if len(os.listdir(temp_folder))==1 and flag_to_do:
				enum_a, enum_b, enum_c, chron_i, chron_j, chron_k=parse_final_dictionary({"issue":pub["issue"], "volume":pub["volume"], "number":pub["number"],"season":pub["season"],"day":pub["day"],"month_string": pub["month"],"year":pub["year"],"term":pub["term"]}) 
				my_design = description_maker.make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
				pub["design"] = my_design
				# print(my_design)
				# print(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
				if len(os.listdir(temp_folder)) >1:
					quit()
				flname = os.path.join(temp_folder, os.listdir(temp_folder)[0])
				new_filename = flname.replace("","_")
				try:
					shutil.move(flname, new_filename)
				except Exception as e:
					print(str(e))
				my_sip = SIPMaker(issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design, temp_sip_folder)
				if my_sip.flag:
					for el in os.listdir(temp_folder):
								os.remove(os.path.join(temp_folder,el))
					my_item = ItemMaker()
					#education_gazette_101.5_issuu2
					my_item.item_routine( issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design)
					if  not pub["design"]:
						pub["design"] =my_design
					with open(os.path.join(report_folder,issuu+".txt"),"a") as f:
						f.write(pub["design"])
						f.write("\n")

					with open(os.path.join(report_folder, issuu+"_worked_out.txt"),"a") as f:
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
			with open(os.path.join(report_folder,"download_not_enabled_by_publisher.txt"),"a") as f:
					f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
					f.write("\n")
			with open(os.path.join(report_folder,"docnames_not_enabled_by_publisher.txt"),"a") as f:
					f.write(pub["docname"])
					f.write("\n")
			
			print(sent_emails)
			if not email_fname in sent_emails:
				try:
					print("here44")
					email_subject = "[ISSUU] No PDF link found for {} - {}".format(issuu,pub["web_title"])
					print(email_subject)
					email_message = '<body style="font-family:Calibri"><br><p>During the automated Issuu downloading process, we expected to find a link for downloading the following issue as a PDF, but it was not enabled:</p><br><p><ul><li><b>Title:</b> {}</li><li><b>Web designation:</b> {}</li><li><b>MMSID:</b> {}</li><li><b>URL for publication:</b> {}</li></ul></p></body>'.format(issuu, pub["web_title"], issuu_dict[issuu]["mms_id"], pub["url"])
					print(email_message)
					email_maker = Gen_Emails()
					email_maker.EmailGen(email_address_line, email_subject, email_message, email_fname, to_send_email)
					with open (email_log,"a") as f:
						f.write(email_fname)
						f.write("\n")
				except Exception as e:
					print(str(e))

def main():

	go_to_flag = False
	if len(os.listdir(temp_folder))!=0:
		for el in os.listdir(temp_folder):
			os.remove(os.path.join(temp_folder, el))
	for issuu in issuu_dict:
		print("#"*50)
		print(issuu)
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
	with open(os.path.join(report_folder,"download_not_enabled_by_publisher.txt"),"r") as f:
		data = f.read()

	#send_email.send_email(data)
	driver.close()
	covers_routine()
if __name__ == "__main__":			
	main()
