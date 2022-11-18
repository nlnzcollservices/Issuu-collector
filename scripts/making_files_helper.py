from my_settings import report_folder_images
import os
from issuu_image_dict import issuu_dict
import requests
text = ""
search_url = r"http://search.issuu.com/api/2_0/document"
my_files = os.listdir(report_folder_images)

for  el in issuu_dict:
	username = issuu_dict[el]["username"]
	params = {"username":username,"pageSize":"100"}
	r = requests.get(search_url,params = params)
	my_json = r.json()
	num_found = my_json["response"]["numFound"]
	# print(issuu_dict[el]["url"])
	filename = el+"_worked_out.txt"
	print("#"*50)
	print(filename)
	full_filename = os.path.join(report_folder_images,filename)
	for ind in range(int(num_found)//100+2):
		start_index = ((int(num_found)//100)-ind)*100
		params["startIndex"]=start_index
		r = requests.get(search_url, params)
		my_doc_json = r.json()["response"]["docs"]
		for el in my_doc_json:
			with open(full_filename,"a") as f:
				f.write(el["docname"])
				f.write("\n")
	quit()