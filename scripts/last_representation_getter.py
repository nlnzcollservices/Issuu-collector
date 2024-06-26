import sys
 #I use my git folder for podcasts where alma_tools.py is located
import dateparser
from time import mktime
from datetime import datetime as dt
# from issuu_images import issuu_dict
import re
sys.path.insert(0,r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts") 
from alma_tools import AlmaTools
import re
from my_settings import seas_dict,term_dict
import urllib3
urllib3.disable_warnings()


def parse_the_labels(label):

		my_date = None
		day = None
		year = None
		month = None
		issue = None
		volume = None
		season = None
		term = None
		number = None
		month_string = None
		month_number = None
		day = "01"
		flag_season = False
		flag_month = True
		flag_term = False

		try:
			year_list = re.findall(r"\d\d\d\d", label)
			if len(year_list) == 1:
				year = year_list[0].lstrip(" ").rstrip(" ")
			else:
				year = year_list[-1].lstrip(" ").rstrip(" ")
		except Exception as e:
			print(str(e))
			#quit()
		try:
			month_day= re.findall(r"\d{1,2}",label.split(year)[-1])
			if not "term" in label.lower() and not ("iss." in label and "v."  in label):
				if len(month_day) == 2:
					month_number = month_day[-2]
					day = month_day[-1]
				elif len(month_day) == 1:
					month_number = month_day[-1]
			# print(month_number)
			# print(int(month))
			# print(month)
			r = range(1,13)
			l = [*r]
			if month_number == '12' and len(year_list)>1:
				year = year_list[0].lstrip(" ").rstrip(" ")

			if not int(month_number) in l:
				# print(month)
				# print(l)
				# print("no manth here")
				month_number = None
				day = None
			#print(month)


		except Exception as e:
			#print(str(e))
			pass

		try:
			# print("finding issue")
			issue = re.findall(r"iss[.](\d{1,3})", label)[0].lstrip(" ").rstrip(" ")
			# print(issue)
		except:
			pass
		try:
			# print("finding number")
			number = re.findall(r"no[.](\d{1,3})", label)[0].lstrip(" ").rstrip(" ")
			# print(number)
		except:
			pass


		try:
			# print('fining volume')
			volume = re.findall(r"v[.](\d{1,2})", label)[0].lstrip(" ").rstrip(" ")
			# print(volume)
		except:
			pass
		try:
			if "term" in label.lower():
				term = re.findall(r"term(.*?)$", label.lower())[0].lstrip(" ").rstrip(" ")
		except Exception as e:
			print(str(e))
		try:
			month_string = re.findall(r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)", label)[0].lstrip(" ").rstrip(" ")
			try: 
				day = my_label.split(month_string)[-1]
			except:
				pass
		except:
			pass
		try:
			#print("here")
			season = re.findall(r"Spring|spring|Summer|summer|Autumn|autumn|Winter|winter", label)[0].lstrip(" ").rstrip(" ")
			#print(season)
		except Exception as e:

			#print(str(e))
			pass


		if year and month_number:
			#print("yera and moth")
			my_date = "{} {} {}".format(year, month_number, day)
		elif year and month_string:
			my_date = "{} {} {}".format(year, month_string, day)
		elif season:
			month_string = seas_dict[season]
			my_date = "{} {} {}".format(year, month_string, day)
			flag_season = True
		elif term:
			month_string = term_dict[term]
			my_date = "{} {} {}".format(year, month_string, day)
			flag_term = True
		else:
			month_number = "01"
			my_date = "{} {} {}".format(year, month_number, day)
			flag_month = True
		# print(my_date, volume, issue,  number,season, month_string, month_number, year, term, flag_season, flag_month, flag_term)
		return (my_date, volume, issue,  number,season, month_string, month_number, year, term, flag_season, flag_month, flag_term)


def last_repres_getter(mms,pub_name, two_years_ago, seas_dict):

	my_lables = {}
	iss = None
	my_date= 0
	year = 0
	my_alma = AlmaTools("prod") 
	my_alma.get_representations(mms)
	# print(my_alma.xml_response_data)
	total_count = int(re.findall(r'<representations total_record_count="(.*?)"', my_alma.xml_response_data)[0]) 
	lables = re.findall(r"<label>(.*?)</label>", my_alma.xml_response_data)
	if total_count !=0:
		if two_years_ago == True:
			current_year= str(dt.now().strftime("%Y"))
			previous_year = str(int(current_year)-1)
		else:
			current_year = "20"
			previous_year = "20"
		# if total_count == 1:
		# 	print("Only one record found")
		# 	print(lables[0])
		for ind in range(0, round(total_count+50,-2),100):
			my_alma.get_representations(mms,{"limit":100, "offset":ind})
			lables = re.findall(r"<label>(.*?)</label>", my_alma.xml_response_data)
			deliv_urls = re.findall(r"<delivery_url>(.*?)</delivery_url>", my_alma.xml_response_data)
			for i,label in enumerate(lables):
						# print(label)

				# if "2021" in label:# or "2020" in label:
						# print(label)
						# print(deliv_urls[i])
				#if not label in ["2021 07 ","2021 06 ","2021 05 ","2021 04 "]:
				# if "2021" in label or "2020" in label:
				# # 	print(my_alma.xml_response_data)
				# # 	quit()

				# # label = label.rstrip(" ")
					# print(label)
					# print(deliv_urls[i])
					# if current_year in label or previous_year in label:
						# if current_year in label and previous_year in label:
						try:
							# if dt.now().strftime("%m") in ["11","12"]:#,"01"]:
							# 		seas_dict ["Summer"]="December"
							# 		seas_dict["summer"] = "December"
							# 		seas_dict["Raumati"]="December"
							# 		seas_dict["Raumati"]="December"
							my_date, volume, issue, number,season, month_string, month_number, year, term, flag_season, flag_month,flag_term= parse_the_labels(label )
							# print(my_date, volume, issue, number,season, month_string, month_number, year, term, flag_season, flag_month,flag_term)
							parsed = dateparser.parse(my_date, settings ={'DATE_ORDER': 'YMD'})
							
							if parsed:
								stamp = mktime(parsed.timetuple())
								if stamp not in my_lables.keys():
									my_lables[stamp]={"volume":volume, "issue":issue, "season":season, "number":number,"month_string":month_string,"month_number":month_number,"year":year, "label":label}
								else:
									if number:
										iss = str(number)
									if issue:
										iss = str(issue)
									if not iss:
										iss="0"
									if volume:
										if my_lables[stamp]["issue"]:
											if int(my_lables[stamp]["volume"])<int(volume)  or (int(my_lables[stamp]["volume"])==int(volume) and int(my_lables[stamp]["issue"])<int(iss)):
												my_lables[stamp]={"volume":volume, "issue":issue, "season":season, "number":number,"month_string":month_string, "month_number":month_number, "year":year, "label":label}
										elif my_lables[stamp]["number"]:
											if int(my_lables[stamp]["volume"])<int(volume)  or (int(my_lables[stamp]["volume"])==int(volume) and int(my_lables[stamp]["number"])<int(iss)):
												my_lables[stamp]={"volume":volume, "issue":issue, "season":season, "number":number,"month_string":month_string, "month_number":month_number, "year":year, "label":label}
									elif issue or number:
										if my_lables[stamp]["issue"]:
											if int(my_lables[stamp]["issue"])<int(iss):
												my_lables[stamp]={"volume":volume, "issue":issue, "season":season, "number":number,"month_string":month_string, "month_number":month_number, "year":year, "label":label}
										elif my_lables[stamp]["number"]:
											if int(my_lables[stamp]["number"])<int(iss):
												my_lables[stamp]={"volume":volume, "issue":issue, "season":season, "number":number,"month_string":month_string, "month_number":month_number, "year":year, "label":label}


						except Exception as e:

							print(str(e))
							
		return [max(my_lables.keys()),dt.fromtimestamp(max(my_lables.keys())).strftime("%Y %B %d"),my_lables[max(my_lables.keys())],flag_season, flag_month, flag_term]
	else:

		return None

def main():
	results = parse_the_labels("2013 Summer")
	print(results)
	two_years_ago = True

	# # for el in ["2014 09 11","2013 Summer","no.700 2014 05 16","iss.803 2016 05 13","2018 09","2021 July 01"]:
	# # 	print(parse_the_labels(el))

	for issuu in issuu_dict.keys():
		print("#"*50)
		print(issuu)
		mms = issuu_dict[issuu]["mms_id"]
		pub_name = str(issuu)
		print(pub_name)
		my_dict=last_repres_getter(mms, pub_name, two_years_ago,seas_dict)
		print(my_dict[1])
if __name__ == '__main__':

	main()
