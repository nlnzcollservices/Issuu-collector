import re
with open("my_item_file","r") as f:
	data = f.read()

my_items = re.findall(r'items/(.*?)">', data)
my_items = list(set(my_items))
for el in my_items:
	print(el)