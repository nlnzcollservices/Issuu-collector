import os
import sys
import configparser
from datetime import datetime as dt
import logging
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\alma_tools')
from alma_tools import AlmaTools
#Rhonda
#sys.path.insert(0,r'H:\project\Alma-tools')
#from alma_tools_v3 import AlmaTools

#********************SETTINGS FILE FOR ALL PODCAST SCRTIPTS****************#

#######################Setting path for all the parts#######################

script_folder = os.getcwd()
working_folder = "\\".join(script_folder.split("\\")[:-1])
file_folder = os.path.join(working_folder, "files")
temp_folder = os.path.join(working_folder,"temp_files")
file_sip_folder = os.path.join("files")
temp_sip_folder = os.path.join("temp_files")
not_processed_files = os.path.join(working_folder, "not_processed_files")
#logs_folder = os.path.join(working_folder, "log")
assets_folder = os.path.join(working_folder,"assets")
template_folder = os.path.join(assets_folder, "templates")
report_folder= os.path.join(working_folder, "reports")
report_folder_images = os.path.join(working_folder, "reports_images")
#log_folder = os.path.join(logs_folder, "log")
email_folder = os.path.join(working_folder,"emails")
email_log = os.path.join(email_folder, "issuu_email_log.txt")
to_send_email = os.path.join(email_folder, "to_send")
sent_emal = os.path.join(email_folder,"sent")

# database_fullname = os.path.join(database_folder, "podcasts.db")
sip_folder_images = os.path.join(working_folder, "SIP_images")
sip_folder = os.path.join(working_folder, "SIP")
#rosetta_folder = r"Y:\NDHA\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\periodic"
rosetta_folder = r"Y:\ndha\pre-deposit_prod\LD_working\issuu_main\rosetta_folder_staging"

#path for cover displayer html files
file_name=r"G:\Fileplan\Bib_Services\Non-Clio_formats\digital_collecting_projects\ISSUU\issuu_titles_covers.html"
file_name_innz = r"G:\Fileplan\Bib_Services\Non-Clio_formats\digital_collecting_projects\ISSUU\issuu_titles_innz.html"
file_name_sip = r"G:\Fileplan\Bib_Services\Non-Clio_formats\digital_collecting_projects\ISSUU\issuu_new_issues.html"
#file_name_innz_sip = r"G:\Fileplan\Bib_Services\Non-Clio_formats\digital_collecting_projects\ISSUU\issuu_sip_innz.html"


########################SETTING FOLDER FOR CREDENTIAL FILES#################

# *-used for proxies, google credentials, alma APIs and DNZ APIs
secrets_and_credentials_fold = r'H:\\secrets_and_credentials'#Svetlana's secrets
#secrets_and_credentials_fold = r'H:\\Secrets'#Rhonda's secrets
sys.path.insert(0, secrets_and_credentials_fold)
secret_file = os.path.join(secrets_and_credentials_fold, "secrets") #Svetlana's secrets
#secret_file = os.path.join(secrets_and_credentials_fold, "shopping") #Rhonda's secrets
config = configparser.ConfigParser()
config.read(secret_file)


####################Getting API keys from secret file##########################

pr_key = config.get( "configuration", "production") 
sb_key= config.get("configuration", "sandbox")	

#############################Logging#####################################################
	
#Logging levels:
# DEBUG: Detailed information, for diagnosing problems. Value=10.
# INFO: Confirm things are working as expected. Value=20.
# WARNING: Something unexpected happened, or indicative of some problem. But the software is still working as expected. Value=30.
# ERROR: More serious problem, the software is not able to perform some function. Value=40
# CRITICAL: A serious error, the program itself may be unable to continue running. Value=50


logging.basicConfig(level=logging.INFO,  datefmt='%Y-%m-%d %H:%M:%S', format = "%(name)15s (%(levelname)s) : %(message)s[%(asctime)s]")
	
months_dictionary = {"January":"01", "February":"02", "March":"03", "April":"04", "May":"05", "June":"06","July":"07", "August":"08","September":"09", "October":"10","November":"11", "December":"12"}
seas_dict = {"Summerer":"January","Spring":"October","Autumn":"April", "Winter":"July", "Summer":"January","Summers":"January","spring":"October","autumn":"April", "winter":"July", "summer":"January","Hōtoke":"July", "Kōanga":"October", "Raumati":"January", "Ngahuru":"April","Chtistmas":"December", "christmas":"December", "Here turi koa":"August"}
months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
reversed_season = {"10":"Spring", "11":"Spring", "09":"Spring","03":"Autumn", "04":"Autumn", "05":"Autumn","06":"Winter","07":"Winter", "08":"Winter","01":"Summer","02":"Summer","12":"Summer"}
term_dict = {"1":"January","2":"April", "3":"July", "4":"October"}
reversed_term =  {"10":"4", "11":"4", "09":"4","03":"2", "04":"2", "05":"2","06":"3","07":"3", "08":"Winter","01":"1","02":"1","12":"1"}
short_month_dict = {"JAN":"January","FEB":"February", "MAR":"March","APR":"April","MAY":"May","JUN":"June","JUL":"July","AUG":"August","SEP":"September","OCT":"October","NOV":"November","DEC":"December"}
issue_dict = {"one":"1","two":"2","tree":"3","four":"4"}
#############################################################Emails######################################################
email_address_line = "LDR@dia.govt.nz"


def main():
	for folder in [ script_folder, assets_folder, template_folder, sip_folder, temp_folder, report_folder, rosetta_folder ]:
		print(folder)
		if not os.path.exists(folder):
			os.mkdir(folder)

if __name__ == '__main__':
	main()