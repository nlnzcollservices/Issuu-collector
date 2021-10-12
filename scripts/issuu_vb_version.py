import os
import re
import time
import sys
from time import mktime
from PIL import Image
import dateparser
# sys.path.insert(0, r'H:\GIT\file-downloader')
# from downloader_light_modified import DownloadResource as Downloader
# from urllib.request import urlopen
#import urlparse
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
import pyautogui
import keyboard, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from fpdf import FPDF
import wget
import ssl
import pickle
import shutil
ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup as bs
from rosetta_sip_factory.sip_builder import build_sip
from alma_tools import AlmaTools
from description_maker import make_description


# from time import time, sleep, mktime
# from datetime import datetime as dt
# #from database_handler import DbHandler
# from nltk.corpus import words
# import nltk
# #nltk.download('words')
# import logging 
# import json
# import requests
from time import sleep
import time
from selenium import webdriver

from sys import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


from issuu_dict import issuu_dict, download_image_list
from settings import logging, file_folder, temp_folder, sip_folder, report_folder
# sys.path.insert(0, r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools
# sys.path.insert(0, r'H:\GIT\file-downloader')
# from downloader_light_modified import DownloadResource as Downloader
# sys.path.insert(0,r"G:\Fileplan\Bib_Services\Non-Clio_formats\Asscquisitions Team\bulk item ingest\bulk_upload_script\tools")
# from description_maker import make_description
import last_representation_getter
import feedparser
import requests
from selenium.webdriver.common.keys import Keys 


pdf = FPDF(unit="pt")#, format=[WIDTH_PDF, HEIGHT_PDF])


logger = logging.getLogger(__name__)
profile = "./main_profile"
if not os.path.isdir("./main_profile"):
	os.makedirs("./main_profile")
print("*** Using profile: {}".format(profile))
opts = Options()
opts.add_argument("-profile")
opts.add_argument(profile)
#opts.binary=r"C:\Program Files\Firefox Developer Edition\firefox.exe"
#driver = webdriver.Firefox(options=opts, service_args=["--marionette-port", "2828"])

# my code
profileFolder=profile
browserProfile=webdriver.FirefoxProfile(profileFolder)
options=webdriver.FirefoxOptions()
options.set_headless(False)




base_url = r"https://issuu.com/"
#######################################Creating google spreadsheet object#################################################


# c = gspread.authorize(creds)
# gs = c.open_by_key(podcast_sprsh)
# #change if the name or id of the worksheet is different
# ws = gs.get_worksheet(0)

class ItemMaker():

	"""This Class is making items for Waterford press"""
	def __init__(self):
		self.item_check = None
	
	def check_item_in_the_system(self, pub_name,description):
		my_alma = AlmaTools("prod")
		my_alma.get_items(issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"])
		total_count = int(re.findall(r'<items total_record_count="(.*?)">', my_alma.xml_response_data)[0]) 
		for ind in range(0, round(total_count+49,-2),100):
			my_alma.get_items(issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"],{"limit":100, "offset":ind})
			descriptions = re.findall(r"<description>(.*?)</description>", my_alma.xml_response_data)
			print(descriptions)
			print(description)
			# v. 27, 1 (2021)
			# v. 27, iss. 1 (2021)
			print(description  in descriptions)
			if description in descriptions:
				self.item_check = True
				return True
			elif description.replace(",",", iss.") in descriptions:
				self.item_check = True
				return True
		return False


	def item_routine(self, pub_name, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, description ):
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
			my_alma = AlmaTools("prod")
			my_alma.create_item_by_po_line(issuu_dict[pub_name]["po_line"], item_data)
			logger.info(my_alma.xml_response_data)
			logger.debug(my_alma.status_code)
			item_grab = bs(my_alma.xml_response_data, "lxml-xml")
			item_pid  = item_grab.find('item').find( 'item_data' ).find( 'pid' ).string 
			logger.info(item_pid + " - item created")		
			
			report_name = "report_items"+str(dt.now().strftime("_%d%m%Y"))+".txt"

			with open(os.path.join(report_folder, report_name),"a") as f:
				f.write("{}|{}|{}|{}".format(pub_name, issuu_dict[pub_name]["mms_id"], issuu_dict[pub_name]["holding_id"], item_pid))
				f.write("\n")		


class SIPMaker():


# Volume = dcterms:bibliographicCitation
# Issue = dcterms:issued
# Number = dcterms:accrualPeriodicity
# Year = dc:date
# Month = dcterms:available
# Day = dc:coverage


	def __init__(self, pub_name, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k,description, file_folder_place ):
		
		self.flag = False
		self.pub_name = pub_name
		self.enum_a = enum_a
		self.enum_c = enum_c
		self.chron_i = chron_i
		self.chron_j = chron_j
		self.chron_k = chron_k
		self.description = description
		self.file_folder_place = file_folder_place
		self.make_SIP()


	def make_SIP(self):
			print("making sips")
			
			self.output_folder = os.path.join(sip_folder, self.pub_name.replace(" ","_") + "_"+self.description.replace(" ","").replace(".","_").replace("(","-").replace(")","-").replace(",","-").rstrip("-").rstrip("_"))
			print(self.output_folder)
			#try:
			print([{"dc:date":self.chron_i, "dcterms:available":self.chron_j, "dc:coverage":self.chron_k, "dcterms:issued":self.enum_c, "dcterms:bibliographicCitation":self.enum_a,  "dc:title":self.pub_name}])
			print(self.file_folder_place)
			print([{"IEEntityType":"PeriodicIE"}])
			print([{"objectIdentifierType":"ALMAMMS", "objectIdentifierValue":issuu_dict[self.pub_name]["mms_id"]}])
			print([{"policyId":"100"}])
			print(self.file_folder_place)
			print(self.pub_name+"_"+self.description)
			print(self.output_folder)
			try:
				build_sip(
									
									ie_dmd_dict=[{"dc:date":self.chron_i, "dcterms:available":self.chron_j, "dcterms:issued":self.enum_c, "dc:coverage":self.chron_k,"dcterms:bibliographicCitation":self.enum_a,  "dc:title":self.pub_name}],
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
			# 	self.flag = False
class IssuuHarvester():

	"""
		This class manages harvesting podcast episodes via rss feed.

		Attributes
		----------

	    podcast_name(str) - name of podcast from podcasts_dict. Should be the same as in serial_record
	    podcast_data(dict) - dictionary which contains information about particular podcast
	    podcast_id(int) - id of podcast in db


	 	Methods
		-------
		__init__(self, podcast_id, podcast_name, podcast_data, last_issue)
		reload_spreadsheet(self, function, parameters)
		episode_sprsh_check(self)
		jhove_check(self, filepath)
		find_description_with_podcastparser(self)
		parsing_with_feedparser(self)
		check_for_meaning(self, my_filename)
	"""

	def __init__(self):
		pass
	def convert_tuple(self, tup):
	    str = ''.join(tup)
	    return str
	def image_pdf_maker(self):
		print("image_pdf_maker")

	def convert_images(self,input_folder, output_folder):
		my_list=os.path.listdir(input_folder)
		for el in os.listdir:
			image1 = Image.open(r'path where the image is stored\file name.png')
			im1 = image1.convert('RGB')
			im1.save(r'path where the pdf will be stored\new file name.pdf')

	def parse_final_dictionary(self,final_dict):
		print(final_dict)
		months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]

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
		if not chron_j and "month_string" in final_dict.keys():
			chron_j=str(months.index(final_dict["month_string"])+1).zfill(2)
		if "year" in final_dict.keys():
			chron_i  = final_dict["year"]
		if "volume" in final_dict.keys():
			enum_a = final_dict["volume"]
		if "issue" in final_dict.keys():
			enum_c = final_dict["issue"]
		if "number" in final_dict.keys():
			enum_c = final_dict["number"]
		if "day" in final_dict.keys():
			chron_k = final_dict["day"]

		return enum_a, enum_b, enum_c, chron_i, chron_j, chron_k


	# def parse_designation(self):

	# 	my_title = None
	# 	volume = None
	# 	issue  = None
	# 	season = None
	# 	month_string = None
	# 	month_number = None
	# 	year = self.web_title.split(" ")[-1]
	# 	if year == "201":
	# 		year  = "2021"
	# 	months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
	# 	my_titles = ["Business Rural North","Business North","Business Rural","RSA Review","Go Travel New Zealand", "Go Travel","NZ dairy","NZ Dairy", "Swings and roundabouts","Swings + Roundabouts", "Business Central","Business North","Business South","Interclub New Zealand", "Interclub"]
	# 	seasons = ["Spring","Autumn", "Winter", "Summer"]
	# 	self.seas_dict = {"Spring":"October","Autumn":"April", "Winter":"July", "Summer":"January","spring":"October","autumn":"April", "winter":"July", "summer":"January"}
	
	# 	for mag_title in my_titles:
	# 		# print(mag_title)
	# 		# print(self.web_title)
	# 		# print("item_title")
	# 		if mag_title.lower() in self.web_title.lower():
	# 			try:
	# 				my_title = self.web_title.split(mag_title)[1].lstrip(" ")
	# 			except:
	# 				if mag_title == "Business Rural North":
	# 					if "rural" not in self.web_title.lower():
	# 		 				my_title = self.web_title.split("Business North")[1].lstrip(" ")

	# 	my_months = []
	# 	for mnth in months:
	# 		if mnth in my_title:
	# 			my_months += [str(mnth)]
	# 	for ses in seasons:
	# 		#print(ses)
	# 		if ses in my_title:
	# 			season = str(ses)
	# 			break
	# 	if self.pub_name in ["Interclub New Zealand","Interclub New Zealand"]:
	# 		volume = my_title.split(" ")[1]
	# 		issue  = my_title.split(" ")[3]
		
	# 	self.web_dictionary= {"volume":volume, "issue":issue, "season":season, "month_string": my_months, "month_number":month_number, "year":year, "title":my_title} 


	def combine_pdfs(self,filepath):
		pass

	def parse_pdf():
		pass

	def parse_pdf():
		pass

	def make_sip():
		pass

	def copy_sip():
		pass

	def make_item():
		pass

	def delete_file():
		pass

	def title_parser(self,title):
		month = None
		day=None
		issue=None
		year = None
		my_date= None
		season=None
		months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
		my_title_list = title.split(" ")
		print(my_title_list)

		for i,el in enumerate(my_title_list):
			print(el)
			if el == "Issue":
				issue = my_title_list[i+1]
		for i,el in enumerate(my_title_list):
			if "." in el:
				try:
					my_date = dateparser.parse(el)
					print(my_date)
				except:
					pass
			if my_date:
				print("here")
				month = my_date.strftime("%B")
				year = my_date.strftime("%Y")
				day = my_date.strftime("%d")
		for i,el in enumerate(my_title_list):
			if el in months:
				month = str(el)
		for i,el in enumerate(my_title_list):
			try:
				year_list = re.findall(r"\d\d\d\d", el)
				if len(year_list) == 1:
					year = year_list[0].lstrip(" ").rstrip(" ")
			except Exception as e:
				print(str(e))
		for i,el in enumerate(my_title_list):
			if "th" in el or "nd" in el or "rd" in el:
				day = el.rstrip("th").rstrip("nd").rstrip("rd")
		for i,el in enumerate(my_title_list):
			day_re= re.findall(r"\d{1,2}",el.split(year)[-1])
			if len(day_re) == 1:
				day=day_re[0]
				if day == issue:
					day = None



		return{"issue":issue,  "season":season, "day":day,"month_string": month,"year":year}
						






	def harvester(self,issuu, url, driver, alma_last_issue_list, filefolderpath):#,offset = 0, my_dict = {}):
		
		""" 
		    Collects files and metadata for all the issues after the last issue  of podcasts listed in dictionary. 	    

	    Args:
			url (str): link to scrape
			issuu (str): name of publication
	    Returns:
	    	None

		"""
		count = 0
		date = None
		logger.info("*"*50)
		logger.info(url)
		logger.info("*"*50)

		driver.get(url)
		for i in range(5):
			driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
			time.sleep(2)

		sleep(2)
		#print(driver.page_source)
		#my_div = 

		my_divs =  driver.find_elements_by_xpath("//div[contains(@class, issuu_dict[issuu]['class_name'])]")
		#my_divs =  driver.find_elements_by_xpath("//div[contains(@class, w7u1sd-4)])

		my_div_indexes = []
		my_dates=[]
		print(issuu)
		count = 0
		print(issuu_dict[issuu]["class_name"])
		for i,my_div in enumerate(my_divs):


#['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_execute', '_id', '_parent', '_upload', '_w3c', 'anonymous_children', 'clear', 'click', 'find_anonymous_element_by_attribute', 'find_element', 'find_element_by_class_name', 'find_element_by_css_selector', 'find_element_by_id', 'find_element_by_link_text', 'find_element_by_name', 'find_element_by_partial_link_text', 'find_element_by_tag_name', 'find_element_by_xpath', 'find_elements', 'find_elements_by_class_name', 'find_elements_by_css_selector', 'find_elements_by_id', 'find_elements_by_link_text', 'find_elements_by_name', 'find_elements_by_partial_link_text', 'find_elements_by_tag_name', 'find_elements_by_xpath', 'get_attribute', 'get_property', 'id', 'is_displayed', 'is_enabled', 'is_selected', 'location', 'location_once_scrolled_into_view', 'parent', 'rect', 'screenshot', 'screenshot_as_base64', 'screenshot_as_png', 'send_keys', 'size', 'submit', 'tag_name', 'text', 'value_of_css_property']
				
			if "7-3" in my_div.get_attribute("class"):# or "7-4"in my_div.get_attribute("class"):
					# print(dir(my_div))
					# print(my_div.tag_name)
					# print(my_div.text)
					# #print(my_div.get_property())
					# #print(my_div.get_attribute())
					# print(my_div.id)
					# #['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_execute', '_id', '_parent', '_upload', '_w3c', 'anonymous_children', 'clear', 'click', 'find_anonymous_element_by_attribute', 'find_element', 'find_element_by_class_name', 'find_element_by_css_selector', 'find_element_by_id', 'find_element_by_link_text', 'find_element_by_name', 'find_element_by_partial_link_text', 'find_element_by_tag_name', 'find_element_by_xpath', 'find_elements', 'find_elements_by_class_name', 'find_elements_by_css_selector', 'find_elements_by_id', 'find_elements_by_link_text', 'find_elements_by_name', 'find_elements_by_partial_link_text', 'find_elements_by_tag_name', 'find_elements_by_xpath', 'get_attribute', 'get_property', 'id', 'is_displayed', 'is_enabled', 'is_selected', 'location', 'location_once_scrolled_into_view', 'parent', 'rect', 'screenshot', 'screenshot_as_base64', 'screenshot_as_png', 'send_keys', 'size', 'submit', 'tag_name', 'text', 'value_of_css_property']
					
					if issuu in ["Dressage NZ Bulletin","Guardian – Motueka","Malvern News","Waimea Weekly"]:
						image = my_div.find_elements_by_tag_name("img")[0].get_attribute("alt")
						image1= my_div.find_element_by_xpath("..")
						image2= image1.find_elements_by_tag_name("time")
						image2 = image2[0].get_attribute("title")
						date = time.mktime(dateparser.parse(image2).timetuple())
					else:
						image = my_div.find_elements_by_tag_name("img")[0].get_attribute("alt")
						print(image)
						print("here")

						image = image.strip('"')
						try:
							
							date = time.mktime(dateparser.parse(" ".join(image.split(" ")[-3:])).timetuple())
						except:
							try:
								date = time.mktime(dateparser.parse(" ".join(image.split(" ")[-2:])).timetuple())
							except:
								try:
									date = time.mktime(dateparser.parse(image.split(" ")[-1]).timetuple())
								except Exception as e:
									try:
										date = time.mktime(dateparser.parse(image.lstrip("Echo"))).timetuple()
									except Exception as e:
										print(str(e))


					if date:
						if date> alma_last_issue_list[0] and (issuu_dict[issuu]["web_title"] in image or issuu == "Guardian – Motueka" and "Cover" in image or issuu_dict[issuu]["web_title2"] in image) or (issuu == "Waimea Weekly" and (not  issuu_dict[issuu]["web_title2"] in image and not "Rural" in image  and not "Grey" in image and not "Civil" in image)) :
							print("here1")
				

							my_div_indexes.append(i)
							my_dates.append(date)
		print(my_div_indexes)
		limit_flag =False
		for ind, el in enumerate(my_div_indexes):
			flag = False
			print("here0")
			driver.get(url)
			for i in range(5):
				driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
				sleep(2)
			sleep(10)
			print("getting indexes again")
			my_divs =  driver.find_elements_by_xpath("//div[contains(@class, issuu_dict[issuu]['class_name'])]")
			for i,my_div in enumerate(my_divs):
				if not flag :
					if not limit_flag:
						print(i)
						if i in my_div_indexes:
								my_class = my_div.get_attribute("class")
								my_div.click()
								sleep(10)
								#print(driver.page_source)
								my_soup = bs(driver.page_source, "lxml")
								#print(my_soup)
								print(type(my_soup))
								title = my_soup.find_all("title")[0].text
								print(title)
								print("title")
								web_dict = self.title_parser(title)
								print("web dict")
								print(web_dict)
								if not issuu in download_image_list:
								
									try:
										my_len=len(os.listdir(filefolderpath))
										print("trying to download")
										driver.find_element_by_xpath("//button[contains(@aria-label, 'Download')]").click()
										sleep(15)
										# for el in os.listdir(filefolderpath):
										# 	my_time = os.path.getctime(os.path.join(el, filefolderpath))
										# 	print(my_time)

										my_len2=len(os.listdir(filefolderpath))
										if my_len==my_len2:
											self.image_pdf_maker()
											my_data = [issuu, my_div_indexes]
											with open('temp.pickle', 'wb') as handle:
												pickle.dump(my_data, handle)
												limit_flag = True
										# else:

										# 	shutil.move(os.path.join(filefolderpath,os.listdir(filefolderpath)[0]), temp_folder )



										

									

								#except NoSuchElementException: 
									except Exception as e:
										print('image list')
										print(str(e))
										print(issuu)
										print(download_image_list)

								if issuu in download_image_list:
									page_source=driver.page_source
									soup = bs(page_source,"lxml")
									title = soup.find('meta', attrs={'property': 'og:title'})['content']
									link = soup.find('meta', attrs={'property': 'og:image'})['content'].split("_")[0]
									number_of_pages= soup.find('meta',attrs={'name':"description"})['content']
									num_page=int(re.findall(r"Length: (.*?) pages",number_of_pages )[0])
									print(num_page)
									my_list =[]
									for page in range(num_page):
										my_link=link+"_"+str(page+1)+".jpg"
										#filepath=os.path.join(filefolderpath,"image")
										#print("here4")
										#if not os.path.exists(filepath):
										#	os.makedirs(filepath)
										#pdfpath = os.path.join(filefolderpath,"pdfs")
										#pdffilepath=os.path.join(pdfpath,title+".pdf")
										#print(pdfpath)
										#if not os.path.exists(pdfpath):
										#	os.makedirs(pdfpath)
										#print("here5")
										wget.download(my_link, out =temp_folder)
										#print("here6")
									my_filenames = os.listdir(temp_folder)
									for image in my_filenames:
										print(image)
										print(image.split('.')[0].split("_")[1])
										print(image.split('.')[0].split("_")[1].zfill(2))
										#print(str(int(image.split('.')[0].split("_")[1]).zfill(2))+".jpg")
										shutil.move(os.path.join(temp_folder, image),os.path.join(temp_folder, "page_" + image.split('.')[0].split("_")[1].zfill(2)+".jpg"))
								if not limit_flag:
									enum_a, enum_b, enum_c, chron_i, chron_j, chron_k=self.parse_final_dictionary(web_dict)
									print(enum_a, enum_b, chron_i, chron_j, chron_k)
									my_designation =make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
									print(my_designation)
									my_sip = SIPMaker(issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k,my_designation, temp_folder)
									if my_sip:
										for el in os.listdir(temp_folder):
											os.remove(os.path.join(temp_folder,el))





										#my_list.append(my_link.split("/")[-1])

									# for el in my_list:
									#     print(os.path.join(filepath, el))
									#     path_to_file = os.path.join(filepath,el)
									#     pdf.add_page()
									#     pdf.image(path_to_file)

									# pdf.output(pdffilepath, "F")

									



								flag = True
								my_div_indexes= my_div_indexes[1:]



					# sleep(25)
					# print(dir(button))
					# elem = driver.switch_to_window(driver.window_handles[-1])
					# print(dir(elem))
					# # print(driver.current_url)
					# print("here3")
					# actions = webdriver.ActionChains(driver).move_to_element(driver.find_element_by_xpath("//button[contains(@aria-label, 'Download')]"))
					# actions.click(driver.find_element_by_xpath("//button[contains(@aria-label, 'Download')]")).perform()
					# # actions.perform()
					# # print(driver.page_source)
					# # print(dir(actions))
					# sleep(25)
					# quit()
					#actions.send_keys(Keys.ENTER)

				# except:


				# 	# .key_down(Keys.CONTROL).send_keys('enter')#.key_up(Keys.CONTROL).perform()
				# 	# sleep(25)
				# 	#pyautogui.press('tab')
				# 	pyautogui.press('enter')
				# 	driver.close()
				# 	#keyboard.press('enter')




				

		# for el in driver.find_elements_by_xpath(f"//div[contains(@class,{my_class})]"):
		# 	el.click()
		# 	print(el.text)
		# 	sleep(10)



			# my_div2 = my_div.find_element_by_tag_name("div")
			# print(my_div2.get_attribute("class"))

			# try:
			# 	el.find
			# 		print(el.get_attribute("class"))
			# 		if "sc-4uqco7-7" in el.get_attribute("class"):
			# 			print("here")
			# 			print(el.tag_name)
			# 			my_tag = el.find_element_by_xpath("//div[contains(@class, sc-4uqco7-7)]")
			# 			print(my_tag.text)
			# 			print("_____________")

			# except Exception as e:
			# 	print(str(e))




# 		#print(driver.page_source)
# 		els = driver.find_elements_by_xpath("//div[contains(@class, sc-4uqco7-7)]")
# 		print(dir(els))

# 		for e in els:
# 			print("here3")
# 			print(e.text)
# 			print("here4")
# 			try:
# 				#if not "FEATURES" in e.text:
# 					print(dir(e))
# 					#print(e.get_attribute())
# 					# print(e.get_property())
# 					print(e.tag_name)
# 					print(e.text)
# 					print(e.id)
# 					print(e.location)
# 					e.click()
# 					sleep(5)

# 			except Exception as e:
# 					print(str(e))


# #'get_attribute', 'get_property', 'id', 'is_displayed', 'is_enabled', 'is_selected', 'location', 'location_once_scrolled_into_view', 'parent', 'rect', 'screenshot', 'screenshot_as_base64', 'screenshot_as_png', 'send_keys', 'size', 'submit', 'tag_name', 'text', 'value_of_css_property']
# #Message: The element reference of <div class="ih-Search-overlay ih-js-search-overlay"> is stale; either the element is no longer attached to the DOM, it is not in the current frame context, or the document has been refreshed

# #['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__g

def harvest():
	"""
	Runs harvester
	"""

	fp = webdriver.FirefoxProfile()
	opt= webdriver.ChromeOptions()
	fp.set_preference("browser.download.folderList", 2)
	fp.set_preference("browser.helperApps.alwaysAsk.force", False)
	#firefox.preferences("browser.helperApps.alwaysAsk.force", false)

	# filefolderpath= os.path.join(os.getcwd(),file_folder,issuu_dict[issuu]["web_title"])
	# print(filefolderpath)
	# print("here0")
	# if not os.path.isdir(filefolderpath):
	# 	os.makedirs(filefolderpath)
	filefolderpath = str(temp_folder)
	print(filefolderpath)
	fp.set_preference("browser.download.dir", filefolderpath)
	#fp.set_preference("browser.download.downloadDir",filefolderpath)
	# fp.set_preference("browser.download.defaultFolder",filefolderpath)
	fp.set_preference("browser.download.useDownloadDir",True)
	fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
	# fp.set_preference("browser.helperApps.neverAsk.openFile", "multipart/x-zip,application/zip,application/x-zip-compressed,application/x-compressed,application/msword,application/csv,text/csv,image/png ,image/jpeg, application/pdf, text/html,text/plain,  application/excel, application/vnd.ms-excel, application/x-excel, application/x-msexcel, application/octet-stream")
	fp.set_preference("pdfjs.disabled",True)
	#fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "multipart/x-zip, application/zip, application/x-zip-compressed, application/x-compressed, application/msword, application/csv, text/csv, image/png , image/jpeg, application/pdf, text/html, text/plain, application/excel, application/vnd.ms-excel, application/x-excel, application/x-msexcel, application/octet-stream
	fp.set_preference("browser.download.manager.showWhenStarting",False)
	#driver=webdriver.Firefox(options=options, firefox_profile=browserProfile, firefox_binary=opts.binary)
	driver = webdriver.Firefox(firefox_profile=fp)
	

	my_harvester = IssuuHarvester()
	for issuu in issuu_dict:


		# opt.add_argument("browser.download.dir", filefolderpath)
		# opt.add_argument("browser.download.useDownloadDir",True)
		# opt.add_argument("browser.helperApps.neverAsk.saveToDisk","application/pdf")
		# opt.add_argument("pdfjs.disabled",True)
		# opt.add_argument("browser.download.manager.showWhenStarting",False)
		# prefs = {}
		# prefs["download.default_directory"]=filefolderpath

		#opt.add_experimental_option("prefs", {"download.default_directory": filefolderpath, "download.prompt_for_download": False, "download.directory_upgrade": True, "safebrowsing.enabled": True })
		#opt.add_experimental_option("prefs", prefs)


		#driver = webdriver.Chrome(r"/home/svetlana/Documents/issuu/chromedriver", chrome_options = opt)
		#driver = webdriver.Chrome("/usr/bin/chromedriver")
		driver.get(r"https://issuu.com")
		time.sleep(3)



		try:
			driver.find_element_by_id("CybotCookiebotDialogBodyButtonAccept").click()
		except Exception as e:
			print(str(e))
		driver.get(r"https://issuu.com/signin?onLogin=%2F&issuu_product=header&issuu_subproduct=anon_home&issuu_context=signin&issuu_cta=log_up")
		sleep(2)
		driver.find_element_by_name("email").send_keys("svetlana.koroteeva@gmail.com")
		driver.find_element_by_name("password").send_keys("HotLunch99")
		driver.find_element_by_name("email").send_keys("rhonda.grantham@dia.govt.nz")
		driver.find_element_by_name("password").send_keys("B18bby111")
		buttons = driver.find_elements_by_tag_name("button")
		for button in buttons:
			if "ixu-button ixu-button--pronounced" in button.get_attribute("class"):
				print(button.get_attribute("class"))
				button.click()
		sleep(1)
		alma_last_issue_list = last_representation_getter.last_repres_getter(issuu_dict[issuu]["mms_id"],issuu, True)

		#alma_last_issue_list = [1617854400.0, '2021 April 08', {'volume': None, 'issue': None, 'season': None, 'number': None, 'month_string': None, 'month_number': '04', 'year': '2021', 'label': '2021 04 08 '}, False, True]

		print(issuu)
		print(alma_last_issue_list)
		url = issuu_dict[issuu]["url"]
		print(url)
		my_harvester.harvester(issuu, url, driver, alma_last_issue_list,filefolderpath)
		




def main():
	harvest()

if __name__ == "__main__":
	main()
