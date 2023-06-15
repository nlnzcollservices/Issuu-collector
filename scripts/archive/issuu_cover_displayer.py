import sys
import os
import re
import requests
from my_settings import report_folder, report_folder_images,  seas_dict , file_name, file_name_innz
from issuu_image_dict import issuu_dict as issuu_image_dict
from issuu_dict import issuu_dict, innz_titles
from last_representation_getter import last_repres_getter
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools
from time import sleep
from datetime import datetime as dt
import datetime

week_ago =dt.now() - datetime.timedelta(days=5)

def dict_reorder(item):
	return {k: dict_reorder(v) if isinstance(v, dict) else v for k, v in sorted(item.items())}


def make_html(file_name, issue_dict, innz=False):

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
	        <title>ISSUU publication covers vs Titles from bib records</title>
			<style>	    
			    
			    div.header
			    {
			      font-size: 18 px;
			      font-weight: 100;
			      font-family: "Times New Roman", Times, serif;
			      color: #87bdd8;
			      text-shadow: 2px 2px 10px #b7d7e8;
			      word-wrap: break-word;      
			      
			      }

			    div.instruct
			    {
			      font-size: 9 px;
			      font-weight: 10;
			      font-family: "Times New Roman", Times, serif;
			      color: #696969;
			      word-wrap: break-word;      
			      
			      }

			    div.gallery {
			      margin: 5px;
			      border: 1px solid #ccc;
			      float: left;
			      width: 250px;
			    }

			    div.gallery:hover {
			      border: 1px solid #777;
			    }

			    div.gallery img {
			      width: 100%;
			      height: 350;
			    }

				div.desc {

				    padding: 4px;
				    color: gray;
				    text-align: center;
				    font-size: 20px;
				    height: 290;
				    text-align: justify;
				    position:relative;
				    border: 2px solid #FFFFFF;
				    }
				div.ndesc {

				    padding: 4px;
				    color: black;
				    text-align: center;
				    font-size: 20px;
				    height: 290;
				    text-align: justify;
				    position:relative;
   				    border: 2px solid #045F5F;


				    }

				div.desc span {
				  align-self: flex-end;
				  color: gray;
				  bottom: 0;
				  position:absolute;
				}
			</style>
	    </head>
	    <body></body>
	</html>"""
	if innz:
		body = r"""<body><div class="header"><H1>INNZ titles collected from ISSUU<br>{}</H1></div>
			<div class="instruct">The Issuu Collector is run every Thursday, the issues collected will be in the NDHA on the next Tuesday. To see details more clearly, you can scroll in using your mouse wheel or <b>Ctrl+</b> keyboard shortcut. Latest issues collected have a bold border and text. Clicking on the cover image takes you to the issue on Issuu.
			<b>If an issue you are expecting has not been collected notify <a href = "ldr@dia.govt.nz">ldr@dia.govt.nz</a>.</div>
	      	 """.format(dt.now().strftime("%A, %B %d %Y"))

	else:
		body = r"""<body><div class="header"><H1>Cover and designation checker for issues collected from ISSUU, {}</H1></div>
			<div class="instruct">Use this to check new issues collected by the Issuu automated collecting pipeline. The cover is a clickable link to the item on Issuu.
			 <b>This issue</b> is the issue that will be archived into the NDHA next, for comparison we also provide details about the <b>Latest issue in NDHA</b>. 
			 Check the Alma publication details matches the issue collected, if there are incorrect designations and gaps between <b>This issue</b> and <b>Latest issue in NDHA</b>. 
			 See <a href = "http://1840.dia.govt.nz/groups/information-and-knowledge-services-iks/national-library-new-zealand/library-groups/collecti-2#DigACHIssuu">1840</a> for more Issuu checking instructions.</div> 
	      	 """.format(dt.now().strftime("%A, %B %d %Y"))
	search_url = r"https://search.issuu.com/api/2_0/document"
	page_url = r"https://image.isu.pub/"
	page_url_part2 = "/jpg/page_1"
	base_url = r"https://issuu.com"
	flag = False
	
	for issuu in issue_dict.keys():
			div_class = "desc"
			design_file_time = None
			body = body+"""<div class="gallery">
						"""
			flag = False
			label = None
			design = None
			mms_id = issue_dict[issuu]["mms_id"]
			days = issue_dict[issuu]["days"]
			pattern = issue_dict[issuu]["pattern"]
			try:
				my_alma.get_bib(mms_id)
			except Exception as e:
				print(str(e))
				my_alma.get_bib(mms_id)
			title = re.findall(r"<title>(.*?)</title>", my_alma.xml_response_data)[0].rstrip(".")
			print(title)
			file_path = os.path.join(report_folder,issuu+ "_worked_out.txt")
			design_file_path = os.path.join(report_folder,issuu+ ".txt")
			try:
				print(design_file_path)
				with open(design_file_path,"r") as f:
					design_data= f.read()
				design_file_time = os.path.getmtime(design_file_path)


			except Exception as e:
				print(str(e))
				try:
					
					design_file_path = os.path.join(report_folder_images,issuu+ ".txt")
					with open(design_file_path,"r") as f:
						design_data= f.read()
					design_file_time = os.path.getmtime(design_file_path)
				except Exception as e:
					print(str(e))
					quit()

			if design_file_time>week_ago.timestamp():
				div_class = "ndesc"
			try:
				with open(file_path,"r") as f:
					data= f.read()
			except:
				try:
					file_path = os.path.join(report_folder_images,issuu+ "_worked_out.txt")
					with open(file_path,"r") as f:
						data= f.read()
				except:
					pass

			my_docname = data.split("\n")[-2]
			design = design_data.split("\n")[-2]
			try:
				label = last_repres_getter(mms_id, issuu, True,seas_dict )[2]["label"]
			except:
				pass
			username = issue_dict[issuu]["username"]
			params = {"username":username,"pageSize":"100"}
			r = requests.get(search_url,params = params,verify=False)
			print(r.text)
			my_json = r.json()
			num_found = my_json["response"]["numFound"]
			for ind in range((int(num_found)//100)+2):
				if not flag:
					start_index = ((int(num_found)//100)-ind)*100
					params["startIndex"]=start_index
					try:
						r = requests.get(search_url, params,verify=False)
					except Exception as e:
						print(str(e))
						r = requests.get(search_url, params,verify=False)

					my_doc_json = r.json()["response"]["docs"]
					for doc in my_doc_json:
						if doc["docname"] == my_docname:
							document_id = doc["documentId"]
							my_link=page_url+document_id+page_url_part2+".jpg"
							pub_url =os.path.join(base_url, username, "docs", doc["docname"])
							body = body+ """
							<a href ={}><img src={} title="{}" alt="{}"></a>
							""".format(pub_url, my_link, title, title)

							flag = True
			body = body + """
							<div class="{}">{}<br><b>This issue:</b><br>{}<br><b>Last issue in NDHA:</b><br>{}<br><b>MMS ID:</b><br>{}<br><b>Frequency (days):</b> {}<br><b>Designation format:<br></b>{}</div>
     				</div>
     			""".format(div_class,title,design,label,mms_id, days, pattern)
			print(body+'</body>')


	body = body+'</body>'
	html_template = html_template.replace("<body></body>",body)
	print(html_template)
	with open(file_name,"w",encoding="utf-8") as f:
		f.write(html_template)

def routine():
	print(issuu_dict)
	issuu_dict.update(issuu_image_dict)
	issuu_dict_innz = {}
	for el in issuu_dict.keys():
		if el in innz_titles:
			issuu_dict_innz[el]=issuu_dict[el]
	#print(issuu_dict_innz)
	new_issuu_dict = {}
	issuu_dict_innz = dict_reorder(issuu_dict_innz)
	for el in issuu_dict.keys():
		new_issuu_dict[el]=issuu_dict[el]
	new_issuu_dict = dict_reorder(new_issuu_dict)
	print("####################################")
	make_html(file_name, new_issuu_dict)
	make_html(file_name_innz, issuu_dict_innz, innz=True)

if __name__ == '__main__':
	print(issuu_dict)
	routine()
