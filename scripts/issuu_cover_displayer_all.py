import sys
import os
import re
import requests
from my_settings import report_folder, report_folder_images,  seas_dict , file_name_sip
from issuu_image_dict import issuu_dict as issuu_image_dict
from issuu_dict import issuu_dict, innz_titles
from last_representation_getter import last_repres_getter
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
from alma_tools import AlmaTools
from time import sleep
from datetime import datetime as dt
import datetime

week_ago =dt.now() - datetime.timedelta(days=5)

def dict_reorder(my_dict):
	return {k: dict_reorder(v) if isinstance(v, dict) else v for k, v in sorted(my_dict.items())}

def count_lists_in_dict(my_dict):
    count = 0
    for value in my_dict.values():
        count += len(value)
    return str(count)

def dict_sort_by_last_el_of_list(my_dict):
	return {k: sorted(v, key=lambda x: x[-1]) for k, v in sorted(my_dict.items())}

def make_html(file_name, issue_dict, innz=False):
	sip_folder_name = None

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
	    	<meta charset="UTF-8">
	        <title>New issues collected from ISSUU</title>
			<style>	   
			    
			    div.header
			    {
			      font-size: 22px;
			      font-weight: 100;
			      font-family: Helvetica, Sans-Serif;
			      color: #87bdd8;
			      text-shadow: 2px 2px 10px #b7d7e8;
			      word-wrap: break-word;      
			      
			      }

			    div.hyperinstruct
			    {
			      font-size: 22px;
			      font-weight: 50;
			      font-family: Helvetica, Sans-Serif;
			      color: #696969;
			      word-wrap: break-word;    
			      
			      }


			      div.questions
			      {font-family: Helvetica, Sans-Serif;
			       color: #87bdd8;

			      }


			    div.instruct
			    {
			      font-size: 16px;
			      font-weight: 10;
			      font-family: Helvetica, Sans-Serif;
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
			      height: 300;
			    }

				div.desc {

				    padding: 4px;
				    font-family: Helvetica, Sans-Serif;
				    color: gray;S
				    text-align: center;
				    font-size: 18px;
				    height: 400;
				    text-align: left;
				    position:relative;
				    border: 2px solid #FFFFFF;
				    word-wrap: break-word; 
				    }
				div.ndesc {

				    padding: 4px;
				    color: black;
				    text-align: center;
				    font-size: 20px;
				    height: 400;
				    text-align: justify;
				    position:relative;
   				    border: 2px solid #045F5F;
   				    word-wrap: break-word; 


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
	      	 """.format(dt.now().strftime("%A, %d %B %Y"))

	else:
		body = r"""<body><div class="header"><H1>New issues collected from ISSUU Collector<br>run {}</H1></div>
			<div class="hyperinstruct">numberplaceholder - issues collected</div><br>
			<div class="instruct">The Issuu Collector is run each Thursday or Friday to collect new issues of titles we track on the Issuu platform published in the previous week. It creates Alma item records for the new issues at the same time.<br><br>New issues are saved into a staging folder so they can be checked by Collection Development staff in this tool before they are archived into Rosetta. Please check all issues and contact the Digital Collecting Specialist (DCS, currently Svetlana Koroteeva) if there are any problems. If the DCS is away, please contact the Legal Deposit Specialist (currently Rhonda Grantham).<br><br>To see the covers more clearly, scroll in using your mouse wheel or the <b>Ctrl+</b> keyboard shortcut. You can also click on each cover image to go directly to that publication on Issuu.<br><br>We provide you with this metadata to help check that new issues have been collected correctly:<br><br><b>&emsp;Alma title:</b> the title of the serial, as recorded in Alma.<br><b>&emsp;This issue:</b> the designation of the issue that you are now checking before it is added to NDHA (in the format of the new item added to Alma).<br><b>&emsp;Last issue in NDHA:</b> the designation of the most recent previous issue held in NDHA.<br><b>&emsp;Designation format:</b> what we expect the designation format of this serial to be, based on previous issues.<br><b>&emsp;Frequency (days):</b> how often we expect new issues of this serial to be published.<br><b>&emsp;MMS ID:</b> MMS ID of this serial.<br><b>&emsp;SIP folder:</b> link to the folder where the new issue is staged before archiving.</div>
			<ol><div class ="questions">Check these things for each new issue:</div>
			<li><div class ="questions">Is the designation for <b>This issue</b> the same as the <b>Latest issue in NDHA</b>?</div>
			<br><div class="instruct">If yes, double-check in Alma/Rosetta to confirm whether it is a duplicate of the latest issue we already hold. If it is, report the SIP folder to the DCS as a duplicate and withdraw the duplicate item from Alma. If it isn't a duplicate of an issue we already hold, report the SIP folder to the DCS to investigate.</div></li>
  			<br><li><div class ="questions">On the cover: does the title differ from the <b>Alma title</b>; or show that the publisher has changed?</div>
  			<br><div class="instruct">If there are changes, report the SIP folder to the DCS who will hold the issue from being processed while you investigate the possible title or publisher change. If there needs to be a new bib record and or POL, work with the DCS to update the Issuu Collector and make sure the new issue is associated with the correct bib record. Also make sure the new issue's Alma item is associated with the correct bib/POL.</div></li>
  			<br><li><div class ="questions">Does the new issue's designation match the expected <b>Designation Format</b>?</div>
  			<br><div class="instruct">If not, check the designation published on the item. If the expected <b>Designation format</b> is still correct and the Issuu Collector has just not correctly parsed the designation, report the SIP folder to the DCS who will update the SIP, while you update the Alma item.<br><br>If the publisher has changed the designation format, and it has been parsed correctly for the new issue, notify the DCS to update the <b>Designation format</b> in the Issuu collector.</div></li>
  			<br><li><div class ="questions">Is there a time gap between <b>This issue</b> and <b>Latest issue in NDHA</b> that doesn't match the <b>Frequency</b>?</div>
  			<br><div class="instruct">Investigate by opening the issue link and scrolling down to see recently published issues. If this is the first instance of a frequency change, make a note of it in the POL. If it is a continuing pattern, update the frequency interval in the POL and notify the DCS to update the Issuu Collector.<br><br>If an issue has been published between the latest issue and the current collected issue but was not collected, send the link for the skipped issue to the DCS. They will either collect the issue or generate a letter you can send to the publisher notifying them that the download link for the issue has not been enabled.</div></li>
  			<br><li><div class ="questions">Is there anything else that looks odd or raises questions?</div>
  			<br><div class="instruct">Talk to the DCS.</div></li>
  			</ol><br><div class="instruct"><b>Once you have checked all the new issues notify the DCS to move the new issue SIPs from the staging to the deposit folder.</b><br><br></div> 

	      	 """.format(dt.now().strftime("%A, %d %B %Y"))
	search_url = r"https://search.issuu.com/api/2_0/document"
	page_url = r"https://image.isu.pub/"
	page_url_part2 = "/jpg/page_1"
	base_url = r"https://issuu.com"
	flag = False
	txt_dict = {}
	#Testing folder here#
	with open("new_issues_viz_temp_{}.txt".format(dt.now().strftime("%Y_%m_%d")),"r") as f:
		data = f.read()
	for el in data.split("\n")[:-1]:
		el_list = el.split("||")
		if  not el_list[0] in txt_dict.keys():
			txt_dict[el_list[0]] = [el_list[1:]]
		else:
			txt_dict[el_list[0]] .append(el_list[1:])
	print(txt_dict)
	txt_dict = dict_sort_by_last_el_of_list(txt_dict)
	print(txt_dict)
	sip_number = count_lists_in_dict(txt_dict)
	for pub in txt_dict:
		print(pub)
		mms_id = issue_dict[pub]["mms_id"]
		days = issue_dict[pub]["days"]
		pattern = issue_dict[pub]["pattern"]

		try:
			my_alma.get_bib(mms_id)
		except Exception as e:
			print(str(e))
			my_alma.get_bib(mms_id)
		title = re.findall(r"<title>(.*?)</title>", my_alma.xml_response_data)[0].rstrip(".")
		print(title)
		for i in range(len(txt_dict[pub])):
			# print(i)
			# print(txt_dict[pub])
			# print(txt_dict[pub][i])

			div_class = "desc"
			design_file_time = None
			body = body+"""<div class="gallery">
						"""
			flag = False
			label = None
			design = None
			try:

				# file_path = os.path.join(report_folder,issuu+ "_worked_out.txt")
				# design_file_path = os.path.join(report_folder,issuu+ ".txt")
				# try:
				# 	print(design_file_path)
				# 	with open(design_file_path,"r") as f:
				# 		design_data= f.read()
				# 	design_file_time = os.path.getmtime(design_file_path)


				# except Exception as e:
				# 	print(str(e))
				# 	try:
						
				# 		design_file_path = os.path.join(report_folder_images,issuu+ ".txt")
				# 		with open(design_file_path,"r") as f:
				# 			design_data= f.read()
				# 		design_file_time = os.path.getmtime(design_file_path)
				# 	except Exception as e:
				# 		print(str(e))
				# 		quit()

				# if design_file_time>week_ago.timestamp():
				# 	div_class = "ndesc"
				# try:
				# 	with open(file_path,"r") as f:
				# 		data= f.read()
				# except:
				# 	try:
				# 		file_path = os.path.join(report_folder_images,issuu+ "_worked_out.txt")
				# 		with open(file_path,"r") as f:
				# 			data= f.read()
				# 	except:
				# 		pass

				# my_docname = data.split("\n")[-2]
				# design = design_data.split("\n")[-2]
				try:
					label = last_repres_getter(mms_id, pub, True,seas_dict )[2]["label"]
				except:
					pass
				# username = issue_dict[issuu]["username"]
				# params = {"username":username,"pageSize":"100"}
				# r = requests.get(search_url,params = params,verify=False)
				# print(r.text)
				# my_json = r.json()
				# num_found = my_json["response"]["numFound"]
				# for ind in range((int(num_found)//100)+2):
				# 	if not flag:
				# 		start_index = ((int(num_found)//100)-ind)*100
				# 		params["startIndex"]=start_index
				# 		try:
				# 			r = requests.get(search_url, params,verify=False)
				# 		except Exception as e:
				# 			print(str(e))
				# 			r = requests.get(search_url, params,verify=False)

				# 		my_doc_json = r.json()["response"]["docs"]
				# 		for doc in my_doc_json:
				# 			if doc["docname"] == my_docname:
				document_id = txt_dict[pub][i][2]
				my_link=page_url+document_id+page_url_part2+".jpg"
				pub_url =txt_dict[pub][i][1]
				design = txt_dict[pub][i][3]
				try:
					sip_folder = txt_dict[pub][i][4]
					sip_folder_name = txt_dict[pub][i][5]
				except:
					sip_folder = None
					sip_folder_name = None

				body = body+ """
								<a href ={}><img src={} title="{}" alt="{}"></a>
								""".format(pub_url, my_link, title, title)

				flag = True
				body = body + """
								<div class="{}"><b>Alma title:</b><br>{}<br><b>This issue:</b><br>{}<br><b>Last issue in NDHA:</b><br>{}<br><b>Designation format:<br></b>{}<br><b>Frequency (days):</b> {}<br><b>MMS ID:</b><br>{}<br><b>SIP folder:</b><br><a href={}>{}</a></div>
	     				</div>
	     			""".format(div_class,title,design,label,pattern, days,mms_id, sip_folder,  sip_folder_name)
				print(body+'</body>')

			except Exception as e:
				print(str(e))


	body = body+'</body>'
	body = body.replace("numberplaceholder",str(sip_number))
	html_template = html_template.replace("<body></body>",body)
	print(html_template)
	with open(file_name,"w",encoding="utf-8") as f:
		f.write(html_template)

def routine():
	#print(issuu_dict)
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
	make_html(file_name_sip, new_issuu_dict)
	#make_html(file_name_innz_sip, issuu_dict_innz, innz=True)

if __name__ == '__main__':

	routine() 
