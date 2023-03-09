import sys
import os
import re
import requests
from my_settings import  seas_dict , working_folder
from issuu_image_dict import issuu_dict as issuu_image_dict
from issuu_dict import issuu_dict
from last_representation_getter import last_repres_getter
sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\Alma_tools')
from alma_tools import AlmaTools
from time import sleep
from datetime import datetime as dt
import datetime

week_ago =dt.now() - datetime.timedelta(days=5)

server_side_folder = r"Y:\ndha\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\periodic"
filename = os.path.join(working_folder,"sip_checker_test.html")

def make_html():

	"""The script is a tool for issuu process. It extracted first page image links from server_side_deposite folder and also extractes titles of bibliographic records and combines them into html file.
	For it's work it uses.
		1. issuu_dict (dict) - file with the dicrionary of all the titles in the process
		2. AlmaTools method from alma_tools.py
		3. my_settings.py - main settings file from Issuu pipeline
		4. Issuu search APIs

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


	body = r"""<body><div class="header"><H1>Cover and designation checker for issues collected from ISSUU, {}</H1></div>
			<div class="instruct">Use this to check newly built SIPs before ingesting.</div> 
	      	 """.format(dt.now().strftime("%A, %B %d %Y"))
	search_url = r"http://search.issuu.com/api/2_0/document"
	page_url = r"https://image.isu.pub/"
	page_url_part2 = "/jpg/page_1"
	base_url = r"http://issuu.com"
	
	for fld in os.listdir(server_side_folder):
		year = None
		month = None
		day = None
		iss_tit = None
		issue = None           
		volume = None
		number = None
		proj = None
		done = "No"
		sip_path = os.path.join(server_side_folder,fld)
		mets_path = os.path.join(sip_path, "content", "mets.xml")
		image_path = os.path.join(sip_path, "content","streams", "page_001.jpg")
		done_path = os.path.join(server_side_folder,fld,"done")
		if os.path.exists(done_path):
			done = "Yes"
		if os.path.exists(image_path):
			with open(mets_path,"r") as f:
				data= f.read()
			mms_id = re.findall(r'<key id="objectIdentifierValue">(.*?)</key>',data)[0]
			print(mms_id)
			try:
				proj = re.findall(r'<key id="UserDefinedA">(.*?)</key>',data)[0]
			except:
				pass
			if proj == "issuu":
				try:
				    year = re.findall(r"<dc:date>(.*?)</dc:date>",data)[0]
				except:
				 	pass
				try:
				    month = re.findall(r"<dcterms:available>(.*?)</dcterms:available>",data)[0]
				except:
				 	pass
				try:
				    day = re.findall(r"<dc:coverage>(.*?)</dc:coverage>",data)[0]
				except:
				 	pass
				try:
				    iss_tit = re.findall(r"<dc:title>(.*?)</dc:title>",data)[0]
				except:
				 	pass
				try:
				    issue= re.findall(r"<dcterms:issued>(.*?)</dcterms:issued>",data)[0]
				except:
				 	pass
				try:
				    volume = re.findall(r"<dcterms:bibliographicCitation>(.*?)</dcterms:bibliographicCitation>",data)[0]
				except:
				 	pass
				try:
				    day = re.findall(r"<dcterms:accrualPeriodicity>(.*?)</dcterms:accrualPeriodicity>",data)[0]
				except:
				 	pass
				print(year)
				print(month)
				print(day)
				print(issue)
				print(volume)
				print(number)
				print(iss_tit)
				ymd = str(year)
				if month:
					ymd= ymd +" " +month
				if day:
					ymd = ymd + " " +day
				ivn = ""
				if issue:
					ivn = ivn+"iss. "+issue
				if volume:
					ivn = ivn+" v. "+volume
				if number:
					ivn = ivn+" n. "+number

				ivn = ivn.lstrip(" ")

         
				div_class = "desc"
				design_file_time = None
				body = body+"""<div class="gallery">
							"""
				flag = False
				label = None
				design = None
				try:
					publisher_url = issuu_dict[iss_tit]["url"]
					print(publisher_url)
				except:
					pass

				try:
					my_alma.get_bib(mms_id)
				except Exception as e:
					print(str(e))
					my_alma.get_bib(mms_id)
				title = re.findall(r"<title>(.*?)</title>", my_alma.xml_response_data)[0].rstrip(".")
				print(title)
		
				try:
					print("here")
					label = last_repres_getter(mms_id, iss_tit, True,seas_dict )[2]["label"]
				except Exception as e:
					print(str(e))
				body = body+ """
				<a href ={}><img src={} title="{}" alt="{}"></a>
				""".format(publisher_url, image_path, title, title)

				flag = True
				body = body + """
								<div class="{}">{}<br><b>This ymd:</b><br>{}<br><b>This iss,vol,num:</b><br>{}<br><b>Last issue in NDHA:</b><br>{}<br><b>MMS ID:</b><br>{}<br><b>Done: </b>{}</div>
	     				</div>
	     			""".format(div_class,title,ymd,ivn,label,mms_id, done)
				print(body+'</body>')


	body = body+'</body>'
	html_template = html_template.replace("<body></body>",body)
	print(html_template)
	with open(filename,"w",encoding="utf-8") as f:
	 	f.write(html_template)

def routine():
	print(issuu_dict)
	issuu_dict.update(issuu_image_dict)
	make_html()


if __name__ == '__main__':
	routine()
