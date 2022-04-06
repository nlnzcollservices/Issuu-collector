from my_settings import to_send_email, email_address_line, report_folder, report_folder_images, logging
from issuu_image_dict import issuu_dict as issuu_image_dict
import sys
from issuu_dict import issuu_dict
import os
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools
import re
import requests
from time import sleep

def main():

	"""The script is a tool for issuu process. It extracted first page imge links from Issuu platform via APIs and the last preserved document name
	from report "worked out" files  for each title and also extractes titles of bibliographic records and combines them into html file.
	For it's work it uses.
		1. issuu_dict (dict) - file with the dicrionary of all the titles in the process
		2. ..worked_out.txt files from report report_folder
		3. AlmaTools method from alma_tools.py
		4. my_settings.py - main settings file from Issuu pipeline
		5. Issuu search APIs

	"""

	my_alma = AlmaTools("prod")
	html_template = """<html>
	    <head>
	        <title>Issuu Titles and Covers</title>
	    </head>
	    <body></body>
	</html>"""
	body = '<body><p>'
	search_url = r"http://search.issuu.com/api/2_0/document"
	page_url = r"https://image.isu.pub/"
	page_url_part2 = "/jpg/page_1"
	flag = False
	for issuu in issuu_dict.keys():
			flag = False
			mms_id = issuu_dict[issuu]["mms_id"]
			my_alma.get_bib(mms_id)
			title = re.findall(r"<title>(.*?)</title>", my_alma.xml_response_data)[0]
			print(title)
			body = body + "<H2>{}</H2>".format(title)

			file_path = os.path.join(report_folder,issuu+ "_worked_out.txt")
			with open(file_path,"r") as f:
				data= f.read()
			my_docname = data.split("\n")[-2]
			print(my_docname)
			username = issuu_dict[issuu]["username"]
			params = {"username":username,"pageSize":"100"}
			r = requests.get(search_url,params = params)
			print(r.text)
			my_json = r.json()
			num_found = my_json["response"]["numFound"]
			for ind in range(int(num_found)//100+2):
				if not flag:
					start_index = ((int(num_found)//100)-ind)*100
					params["startIndex"]=start_index
					r = requests.get(search_url, params)
					sleep(1)
					my_doc_json = r.json()["response"]["docs"]
					for doc in my_doc_json:
						if doc["docname"] == my_docname:
							document_id = doc["documentId"]
							my_link=page_url+document_id+page_url_part2+".jpg"
							print(my_link)
							body = body+ '<a href ={}><img src={} title="{}" alt="{}" width="500" height="720"></a>'.format(issuu_dict[issuu]["url"], my_link, title, title)
							body = body + '<br><HR>'
							flag = True
	body = body+'</p></body>'
	html_template = html_template.replace("<body></body>",body)
	print(html_template)
	with open("issuu_titles_covers.html","w",encoding="utf-8") as f:
		f.write(html_template)

if __name__ == '__main__':
	main()