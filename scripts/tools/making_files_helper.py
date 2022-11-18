import os
import requests
import shutil
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#####Uncomment depending on workflow

from my_settings import report_folder
from issuu_dict import issuu_dict
# from my_settings import report_folder_images as report_folder
# from issuu_image_dict import issuu_dict

"Change issuu_dict variable from image dictionary or not, and in line 34 report_folder or report_folder_images"
"The same for second files maker"

text = ""

search_url = r"http://search.issuu.com/api/2_0/document"
my_files = os.listdir(report_folder)

def make_second_files():

	for el in os.listdir(report_folder):
		if "_worked_out.txt" in el:
			shutil.copyfile(os.path.join(report_folder,el),os.path.join(report_folder_folder,el.replace("_worked_out.txt","worked_out2.txt")))
			#os.rename(os.path.join(report_folder,el),os.path.join(report_folder,el.replace("_worked_out.txt","_worked_out2.txt")))
def main():
	for  el in issuu_dict:
		my_final_list = []
		username = issuu_dict[el]["username"]
		params = {"username":username,"pageSize":"100"}
		r = requests.get(search_url,params = params, verify =False)
		my_json = r.json()
		num_found = my_json["response"]["numFound"]
		# print(issuu_dict[el]["url"])
		filename = el+"_worked_out.txt"
		print("#"*50)
		print(filename)
		full_filename = os.path.join(report_folder,filename)
		for ind in range(int(num_found)//100+2):
			start_index = ((int(num_found)//100)-ind)*100
			params["startIndex"]=start_index
			r = requests.get(search_url, params, verify = False)
			my_doc_json = r.json()["response"]["docs"]
			for el in my_doc_json:
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
	# make_second_files()
	