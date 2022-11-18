from issuu_image_dict import issuu_dict
import sys
import re
from my_settings import sip_folder, to_send_email, temp_folder, email_address_line, report_folder, template_folder,logging, rosetta_folder, seas_dict, term_dict, months, reversed_season, months_dictionary,short_month_dict, not_processed_files, email_log, reversed_term
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools

for el in issuu_dict:
	print(el)
	po_line = issuu_dict[el]["po_line"]
	my_api = AlmaTools("prod")
	my_api.get_po_line(po_line)
	try:
		days = re.findall(r'<subscription_interval>(.*?)</subscription_interval',my_api.xml_response_data )[0]
		print(days)
		issuu_dict[el]["days"] = days
	except Exception as e:
		print(str(e))
for el in issuu_dict:
	print('"'+el+'":',issuu_dict[el],',')