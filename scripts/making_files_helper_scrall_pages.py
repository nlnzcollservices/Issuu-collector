import os
import re
from time import mktime, sleep
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from sys import platform
from selenium.common import exceptions
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
import shutil
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#####Uncomment depending on workflow

from my_settings import report_folder
from issuu_dict import issuu_dict
#from my_settings import report_folder_images as report_folder
#from issuu_image_dict import issuu_dict
my_files = os.listdir(report_folder)

fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.helperApps.alwaysAsk.force", False)
# fp.set_preference("browser.download.dir", temp_folder)
fp.set_preference("browser.download.useDownloadDir",True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
fp.set_preference("pdfjs.disabled",True)
fp.set_preference("browser.download.manager.showWhenStarting",False)

# options = Options()
# options.headless = True

driver = webdriver.Firefox(firefox_profile = fp)#, options=options)



# logger = logging.getLogger(__name__)
# base_url = r"https://issuu.com/"
# test_url = r"https://issuu.com/dressagenzbulletin"
# search_url = r"https://search.issuu.com/api/2_0/document"
# # page_url = r"https://image.isu.pub/"
# # page_url_part2 = "/jpg/page_"
# pdf_url_part2 =r"/docs/"
# key = "prod"

test_url = r"https://issuu.com/dressagenzbulletin"
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




def click_element(element):
    action = ActionChains(driver)
    action.move_to_element(element).click().perform()

def load_driver(url):
	print("called load driver")

	try:
		driver.get(url)
	except Exception as e:
		print(str(e))
	driver.implicitly_wait(7)
	try:				
		driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept").click()
	except Exception as e:
		print(str(e))
		try:
			driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
		except Exception as e:
			print(str(e))
	# driver.implicitly_wait(7)
	# element_to_click = driver.find_element(By.ID, "app")
	# click_element(element_to_click)
	# driver.implicitly_wait(5)
	# element_to_click = driver.find_element(By.TAG_NAME, "h1")
	# click_element(element_to_click)
	# driver.implicitly_wait(5)
	# scroll_down(driver)

	username = url.split("/")[-1]
	print(username)
	if username.isdigit():
		print("here1")
		username = url.split("/")[-2]
	print("here2")
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
		print("{}/docs/".format(username))
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
    for i in range(25):

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(6)
        new_height = driver.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
        # #     break
        # last_height = new_height




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



# ######################################################
# ##################################

# 	for i,pub in enumerate(my_dict_list):
# 		email_fname = issuu+ ' ' +pub["web_title"].replace(" ","_")
# 		flag_to_do = False
# 		r=requests.get(pub["url"], verify=False)
# 		if len(re.findall("The publisher chose",r.text)) == 0:
# 			if len(os.listdir(temp_folder))!=0:
# 				print("files detected")

# 				for el in os.listdir(temp_folder):
# 					try:
# 						shutil.move(os.path.join(temp_folder,el), not_processed_files)
# 					except:
# 						os.remove(os.path.join(temp_folder,el))
# 			if pub["web_title"]=="":
# 				my_soup = bs(r.text, "lxml")
# 				web_title = my_soup.find_all("h1")[0].text
# 				my_dict_list[i]["web_title"] = web_title

# 			try:
# 				driver.get(pub["url"])
# 			except Exception as e:
# 				print(str(e))
# 			# driver.implicitly_wait(10)
# 			# try:
# 			# 	# print("here00")
# 			# 	# <a id="CybotCookiebotDialogBodyButtonAccept" class="CybotCookiebotDialogBodyButton" href="#" tabindex="0" style="padding-left: 12px; padding-right: 12px;" lang="en">Allow all cookies</a>
# 			# 	print("here000")
# 			# except Exception as e:
# 			# 	print(str(e))
# 			# 	try:				
# 			# 		driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonAccept").click()
# 			# 	except Exception as e:
# 			# 		print(str(e))
# 			# 		try:
# 			# 			driver.find_element(By.ID,"CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
# 			# 		except Exception as e:
# 			# 			print(str(e))

# 			sleep(30)
# 			# try:	
# 			# 	driver.find_element(By.XPATH,"//button[contains(@aria-label, 'Download')]").click()
# 			# except Exception as e:
# 			# 	print("here11")
# 			try:
# 				driver.find_element(By.XPATH,"//button[contains(@aria-describedby, 'download_tooltip')]").click()
# 				# <button aria-describedby="download_tooltip" class="sc-1an4lpe-1 jPjQNo" style=""><div aria-hidden="true" class="sc-1an4lpe-0 bQChXH"><svg fill="currentColor" height="24" viewBox="0 0 24 24" width="24" role="img"><path d="M11.8484 15.3864C11.8664 15.4081 11.8894 15.4257 11.9157 15.4378C11.9419 15.4498 11.9708 15.4561 12 15.4561C12.0292 15.4561 12.0581 15.4498 12.0843 15.4378C12.1106 15.4257 12.1336 15.4081 12.1516 15.3864L14.8468 12.1659C14.9455 12.0477 14.8564 11.8727 14.6952 11.8727H12.912V4.18182C12.912 4.08182 12.8254 4 12.7195 4H11.2757C11.1698 4 11.0832 4.08182 11.0832 4.18182V11.8705H9.30481C9.14358 11.8705 9.05455 12.0455 9.15321 12.1636L11.8484 15.3864ZM19.8075 14.5909H18.3636C18.2578 14.5909 18.1711 14.6727 18.1711 14.7727V18.2727H5.82888V14.7727C5.82888 14.6727 5.74225 14.5909 5.63636 14.5909H4.19251C4.08663 14.5909 4 14.6727 4 14.7727V19.2727C4 19.675 4.34412 20 4.77005 20H19.2299C19.6559 20 20 19.675 20 19.2727V14.7727C20 14.6727 19.9134 14.5909 19.8075 14.5909Z"></path></svg></div>Download</button>

# 				sleep(40)
# 				# pyautogui.moveTo(720,670)
# 				# #pyautogui.moveTo(725,572)#Rhonda's big screen
# 				# # pyautogui.moveTo(1725,1000)#big screen save location
# 				# # pyautogui.moveTo(800,500)
# 				# # pyautogui.moveTo()
# 				# # pyautogui.move(1,1)
# 				# pyautogui.click()
# 				# # sleep(10)
# 				# # pyautogui.click()
# 				# #pyautogui.hotkey('enter')https://issuu.com/deputy_editorhttps://issuu.com/deputy_editor
# 				if len(os.listdir(temp_folder))!=1:
# 					sleep(20)
# 				if len(os.listdir(temp_folder))!=1:
# 					sleep(20)
# 					# try:
# 					# 	pyautogui.hotkey('tab')
# 					# 	pyautogui.hotkey('tab')
# 					# 	pyautogui.hotkey('tab')
# 					# 	pyautogui.hotkey('tab')
# 					# 	pyautogui.hoftkey('enter')
# 					# except:
# 					# 	pass

# 				seconds =download_wait(temp_folder)
# 				print("Downloading process took",seconds, "seconds")
# 				if len(os.listdir(temp_folder))==0:
# 					html = driver.page_source
# 					if "The specified key does not exist" in html:

# 						with open(os.path.join(report_folder,"was_not_downloaded.txt"),"a") as f:
# 							f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
# 							f.write("\n")
# 						with open(os.path.join(report_folder,"wrong_key_error.txt"),"a") as f:
# 							f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
# 							f.write("\n")
# 						with open(os.path.join(report_folder,"wrong_key_error.txt"),"a") as f:
# 								f.write(pub["docname"])
# 								f.write("\n")
# 						print(sent_emails)
# 						if not email_fname in sent_emails:
# 							try:
# 								print("here22")
# 								email_subject = "[ISSUU] No PDF link found for {} - {}".format(issuu, pub["web_title"])
# 								print(email_subject)
# 								email_message = '<body style="font-family:Calibri"><br><p>During the automated Issuu downloading process, we expected to find a link for downloading the following issue as a PDF, but it was not enabled:</p><br><p><ul><li><b>Title:</b> {}</li><li><b>Web designation:</b> {}</li><li><b>MMSID:</b> {}</li><li><b>URL for publication:</b> {}</li></ul></p></body>'.format(issuu, pub["web_title"], issuu_dict[issuu]["mms_id"], pub["url"])
# 								print(email_message)
# 								email_maker = Gen_Emails()
# 								email_maker.EmailGen(email_address_line, email_subject, email_message,  email_fname, to_send_email)
# 								with open (email_log,"a") as f:
# 									f.write(email_fname)
# 									f.write("\n")
# 							except Exception as e:
# 								print(str(e))





# 			except exceptions.NoSuchElementException:
# 				with open(os.path.join(report_folder,"was_not_downloaded.txt"),"a") as f:
# 					f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
# 					f.write("\n")
# 				with open(os.path.join(report_folder,"was_not_downloaded_docnames.txt"),"a") as f:
# 					f.write(pub["docname"])			
# 					f.write("\n")
# 			except Exception as e:
# 				print(str(e))
# 			for fname in os.listdir(temp_folder):
# 				if not fname.endswith('part'):
# 					flag_to_do = True
# 			if len(os.listdir(temp_folder))==1 and flag_to_do:
# 				enum_a, enum_b, enum_c, chron_i, chron_j, chron_k=parse_final_dictionary({"issue":pub["issue"], "volume":pub["volume"], "number":pub["number"],"season":pub["season"],"day":pub["day"],"month_string": pub["month"],"year":pub["year"],"term":pub["term"]}) 
# 				my_design = description_maker.make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
# 				pub["design"] = my_design
# 				# print(my_design)
# 				# print(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
# 				if len(os.listdir(temp_folder)) >1:
# 					quit()
# 				flname = os.path.join(temp_folder, os.listdir(temp_folder)[0])
# 				new_filename = flname.replace("","_")
# 				try:
# 					shutil.move(flname, new_filename)
# 				except Exception as e:
# 					print(str(e))
# 				my_sip = SIPMaker(issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design, temp_sip_folder)
# 				if my_sip.flag:
# 					for el in os.listdir(temp_folder):
# 								os.remove(os.path.join(temp_folder,el))
# 					my_item = ItemMaker()
# 					#education_gazette_101.5_issuu2
# 					my_item.item_routine( issuu, enum_a, enum_b, enum_c, chron_i, chron_j, chron_k, my_design)
# 					if  not pub["design"]:
# 						pub["design"] =my_design
# 					with open(os.path.join(report_folder,issuu+".txt"),"a") as f:
# 						f.write(pub["design"])
# 						f.write("\n")

# 					with open(os.path.join(report_folder, issuu+"_worked_out.txt"),"a") as f:
# 						f.write(pub["docname"])
# 						f.write("\n")

# 					with open("new_issues_viz_temp_{}.txt".format(dt.now().strftime("%Y_%m_%d")),"a") as f:
# 						f.write(issuu)
# 						f.write("||")				
# 						f.write(pub["docname"])
# 						f.write("||")
# 						f.write(pub["url"])
# 						f.write("||")
# 						f.write(pub["document_id"])
# 						f.write("||")
# 						f.write(pub["design"])
# 						f.write("||")
# 						f.write(os.path.join(rosetta_folder, my_sip.sip_name_folder))
# 						f.write("||")
# 						f.write(my_sip.sip_name_folder)
# 						f.write("\n")
# 		else:
# 			with open(os.path.join(report_folder,"download_not_enabled_by_publisher.txt"),"a") as f:
# 					f.write(issuu+"|"+my_dict_list[i]["url"]+"|"+web_title)
# 					f.write("\n")
# 			with open(os.path.join(report_folder,"docnames_not_enabled_by_publisher.txt"),"a") as f:
# 					f.write(pub["docname"])
# 					f.write("\n")
			
# 			print(sent_emails)
# 			if not email_fname in sent_emails:
# 				try:
# 					print("here44")
# 					email_subject = "[ISSUU] No PDF link found for {} - {}".format(issuu,pub["web_title"])
# 					print(email_subject)
# 					email_message = '<body style="font-family:Calibri"><br><p>During the automated Issuu downloading process, we expected to find a link for downloading the following issue as a PDF, but it was not enabled:</p><br><p><ul><li><b>Title:</b> {}</li><li><b>Web designation:</b> {}</li><li><b>MMSID:</b> {}</li><li><b>URL for publication:</b> {}</li></ul></p></body>'.format(issuu, pub["web_title"], issuu_dict[issuu]["mms_id"], pub["url"])
# 					print(email_message)
# 					email_maker = Gen_Emails()
# 					email_maker.EmailGen(email_address_line, email_subject, email_message, email_fname, to_send_email)
# 					with open (email_log,"a") as f:
# 						f.write(email_fname)
# 						f.write("\n")
# 				except Exception as e:
# 					print(str(e))
def make_second_files():

	for el in os.listdir(report_folder):
		if "_worked_out.txt" in el:
			shutil.copyfile(os.path.join(report_folder,el),os.path.join(report_folder_folder,el.replace("_worked_out.txt","worked_out2.txt")))
			#os.rename(os.path.join(report_folder,el),os.path.join(report_folder,el.replace("_worked_out.txt","_worked_out2.txt")))

def main():
	for  el in issuu_dict:
		my_final_list = []
		username = issuu_dict[el]["username"]
		pub_url = issuu_dict[el]["url"]
		params = {"username":username,"pageSize":"100"}
		# my_doc_json =  get_my_doc_json(pub_url)
		filename = el+"_worked_out.txt"
		full_filename = os.path.join(report_folder,filename)
		status = ""
		# if my_doc_json == []:
		#scroll_down(driver)
		my_json_list = []
		i = 1
		my_doc_json =""
		while not my_doc_json == []:
				print(i)
				my_url = str(pub_url)
				if i > 1:
					my_url= pub_url+"/"+str(i)
				# driver.get(my_url)
				# driver.implicitly_wait(3)

				my_doc_json == []
				# element = driver.find_element_by_xpath("//html/body")
				# actions = ActionChains(driver)
				# actions.move_to_element(element).click().perform()
				# driver.implicitly_wait(3)
				my_doc_json = get_my_doc_json(my_url)
				my_json_list = my_json_list + my_doc_json
				i+=1
		#my_doc_json = r.json( )["response"]["docs"]
		for el in my_json_list:
			my_final_list.append(el["docname"])

		my_final_list = list(set(my_final_list))
		my_final_list = sorted(my_final_list)
		for dcnm in my_final_list:
			with open(full_filename,"a") as f:
					f.write(dcnm)
					f.write("\n")
			with open(full_filename.replace("_worked_out.txt","_worked_out2.txt"),"a") as f:
					f.write(dcnm)
					f.write("\n")

if __name__ == '__main__':
	main()

