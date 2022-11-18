from issuu_image_dict import issuu_image_dict
count =2
for el in issuu_image_dict:
	print("_")
	print(count)

	print(el, issuu_image_dict[el]["interval"])
	count+=1
	# print(issuu_image_dict[el]["interval"])
print(len(issuu_image_dict))