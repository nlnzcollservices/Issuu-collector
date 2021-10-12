import os
import sys
import configparser
from datetime import datetime as dt
import logging



#********************SETTINGS FILE FOR ALL PODCAST SCRTIPTS****************#

#######################Setting path for all the parts#######################

script_folder = os.getcwd()
working_folder = "\\".join(script_folder.split("\\")[:-1])
#file_folder = os.path.join(working_folder, "files")
temp_folder = os.path.join(working_folder,"temp_files")
#logs_folder = os.path.join(working_folder, "log")
assets_folder = os.path.join(working_folder,"assets")
template_folder = os.path.join(assets_folder, "templates")
report_folder= os.path.join(working_folder, "reports")
#log_folder = os.path.join(logs_folder, "log")

# database_fullname = os.path.join(database_folder, "podcasts.db")
sip_folder = os.path.join(working_folder, "SIP")
rosetta_folder = r"Y:\NDHA\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\periodic"


########################SETTING FOLDER FOR CREDENTIAL FILES#################

# *-used for proxies, google credentials, alma APIs and DNZ APIs
secrets_and_credentials_fold = r'H:\\secrets_and_credentials'
sys.path.insert(0, secrets_and_credentials_fold)
secret_file = os.path.join(secrets_and_credentials_fold, "secrets") 
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
seas_dict = {"Spring":"October","Autumn":"April", "Winter":"July", "Summer":"January","spring":"October","autumn":"April", "winter":"July", "summer":"January"}
months = ["January", "February", "March", "April", "May", "June", "July", "August","September", "October","November", "December"]
reversed_season = {"10":"Spring", "04":"Autumn","07":"Winter","01":"Summer"}





def main():
	for folder in [ script_folder, assets_folder, template_folder, sip_folder, temp_folder, report_folder, rosetta_folder ]:
		print(folder)
		if not os.path.exists(folder):
			os.mkdir(folder)

if __name__ == '__main__':
	main()