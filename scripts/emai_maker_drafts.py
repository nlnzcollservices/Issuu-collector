mport os
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from textwrap import wrap
from decimal import Decimal
from datetime import datetime


input_text_file = r'G:\wgn\Fileplan\Bib_Services\Non-Clio_formats\PLR\2020\2020 Confirmation of registration email.txt'
subject = '{} Confirmation of Registration - Public Lending Right for New Zealand Authors'.format(datetime.today().year)
email_folder =  'email_march'
test_folder = 'test_march'
test_email = 'Faye.Rodgers@dia.govt.nz'
send_by_date = "1 April"

if not os.path.exists(email_folder):
    os.mkdir(email_folder)

if not os.path.exists(test_folder):
    os.mkdir(test_folder)                               


############################################Jay's old code###################################################################

class Gen_Emails(object):
    def __init__(self):
        pass

    def EmailGen(self, to_address, html, f_name, folder):

        filename = os.path.join(folder,f_name+'.eml' )
        #inserting a current year to the subject line
        today = datetime.today()
        msg = MIMEMultipart('alternative')
        msg['X-Unsent'] = '1'
        msg['Subject'] = subject
        msg['To'] = to_address
        part = MIMEText(html.encode("utf-8", "replace"), 'html', _charset="UTF-8")

        msg.attach(part)

        self.SaveToFile(msg, filename)
    def SaveToFile(self, msg, filename ):
        with open(filename, 'w') as outfile:
            gen = generator.Generator(outfile)
            gen.flatten(msg)



maker = Gen_Emails()





##########################################GLOBAL VARIABLES#########################################################################
#email_count - counts emails
#line_count - counts lines in xml document and helps to escape the first delimiter
#small_list - stemporary container for one record based on delimiter
#xml_data - restored from small_list individual record for each author
#result_list - contains list of titles and results for each author
#list_of_books - small list with two records - title and result for each row
#author_list - big list which contains all the list_of_bookds for each author
#full_titles - contains html rows for each author
#body - contains html body for every letter
#x_titles - header strings in list
#x_border - creates border
#x_titles_header - combine header data to html header



####################################Creates list  of each in comfortable format######################################################
#This function returns author id, email, salutation and title/table_list from individual email data
#['a','b',['c','d']]
#table_flag - indicates a start of title-result table rows
#table_list - contains all the title-result data 

def Create_data(xml_data):


    part_of_titles = ""
    part_of_status = ""
    contact = "Contact: "

    table_flag = False
    body_flag = False
    table_list = []
    body_string = ""
    for line in xml_data:   

           
        if '<AuthorDetails>' in line:
            author_details = re.sub(r'<AuthorDetails>|<\/AuthorDetails>', "", line)               
        if '<AuthorID>' in line:
            authorid = re.sub(r'<AuthorID>|<\/AuthorID>', "", line)
            
        if '<AuthorName>' in line:
            author_name =  re.sub(r'<AuthorName>|<\/AuthorName>', "", line)
        if '<Contact>' in line:
            contact =  re.sub(r'<Contact>|<\/Contact>', "", line)
        if '<Email>' in line:
            emails = re.sub(r'<Email>|<\/Email>',"", line)
            emails = emails.replace("Email: ", "")
        if '<Address>' in line:
            address =  re.sub(r'<Address>|<\/Address>', "", line)
        if '<GST>' in line:
            GST = re.sub(r'<GST>|<\/GST>', "", line)
        if '<Bank>' in line:
            bank = re.sub(r'<Bank>|<\/Bank>', "", line)
        if '<Residency>' in line:
            residency = re.sub(r'<Residency>|<\/Residency>', "", line)
        if '<ConsentName>' in line:
            consent_name = re.sub(r'<ConsentName>|<\/ConsentName>', "", line)
        if '<ConsentAmount>' in line:
            consent_amount = re.sub(r'<ConsentAmount>|<\/ConsentAmount>', "", line)

        if '<Salutation>' in line:
            salutation = re.sub(r'<Salutation>|<\/Salutation>',"", line)
        if '<Title>' in line:
            table_flag = True
        if '<BodyText>' in line:
            body_flag = True
        if body_flag:
            body_string +=" " + line
        if '</BodyText>' in line:
            body_flag = False
            body_string = re.sub(r'<BodyText>|<\/BodyText>',"", body_string)
            body_string = body_string.lstrip(" ")

       

        if table_flag:
            if '<Title>'in line and '</Title>' in line:
                
                stripped_data = re.sub(r'<Title>|<\/Title>',"", line)
                table_list.append(stripped_data)
            if '<Title>' in line and '</Title>' not in line:
                part_of_titles =  re.sub(r'<Title>',"", line)
            if '</Title>' in line and not '<Title>' in line:
                stripped_data = re.sub(r'<\/Title>',"", line)
                table_list.append(part_of_titles + " " +stripped_data)
            if '<Royalties>' in line:
                stripped_data = re.sub(r'<Royalties>|<\/Royalties>',"", line)
                table_list.append(stripped_data)
            if '<TitleStatus>' in line and '</TitleStatus>' in line:
                stripped_data = re.sub(r'<TitleStatus>|<\/TitleStatus>',"", line)
                stripped_data = stripped_data.split(")")
                #print(len(stripped_data))
                if len(stripped_data) == 3:
                  piece_of_data = "{}){}".format(stripped_data[0], stripped_data[1])
                  stripped_data = piece_of_data +")" + ":" +stripped_data[2]
                if len(stripped_data) ==2:
                  stripped_data = stripped_data [0] + ")"+":" + stripped_data[1]
                if len(stripped_data) == 1:
                  stripped_data = stripped_data[0]

                table_list.append(stripped_data)


    try:
        return [author_details, authorid, author_name, contact, emails,  address, GST, bank, residency, consent_name, consent_amount, salutation, body_string, table_list]
    except UnboundLocalError as e:
        print("error", str(e))




def separator(text, param):
    string = '<br />' + '&nbsp;'*3
    new_text = string.join(wrap(text, param))
    return new_text



def main():

    body_add = []
    small_list = []
    line_count = 0
    email_count = 0
    xmlfile = open(input_text_file,'r')

    for line in xmlfile:
    # loops every file line
        if line != "\n":
            line = line.lstrip(" ")
        #splits the last one
            line_count +=1
            # find delimiter 
            if line.startswith("<RecordDelimiter>################"):
                    email_count+=1
                #starts processing data for each author
                #if if txt starts with delimeter.
                #if line_count != 1: #uncomment if text file starts with <RecordDelimiter>
                    xml_data = "".join(small_list)
                    splited_xml = xml_data[:-1].split("\n")
                    small_list = []
                    list_of_books= []
                    # calling function Create_data to get a list of individual information
##########################Calling Create_data parser function###################################
                    #to get a list of individual information
                    input_values= Create_data(splited_xml)                                      #
################################################################################################
                    
                    result_list = input_values[13]
                    author_list = []
                    author_details = input_values[0]
                    authorid = input_values[1].strip("Author ID: ")
                    salutation = input_values[11]
                    to_address = input_values[4]
                    title = result_list[0]
                    author_name = input_values[2]
                    contact = input_values[3]
                    address = input_values[5]
                    GST = input_values[6]
                    bank = input_values[7]
                    residency = input_values[8]
                    consent_name = input_values[9]
                    consent_amount = input_values[10]
                    body_string = input_values[12]

                    for ind in range(len(result_list)):

                        if len(list_of_books)<3:
                            list_of_books.append(result_list[ind])
                        if len(list_of_books)==3:
                            author_list.append(list_of_books)
                            list_of_books = []

                    full_titles = ""
                    one_title = ""
#########################################################################################Start building html#############################################################################################
                    today = datetime.today()
                    body_string = "Thank you for submitting a registration for the {} Public Lending Right for New Zealand Authors scheme. Please carefully check all of the information below that we have recorded about your registration. Note that any missing titles will not be surveyed. If there are any errors please advise us before the {} {}. There is no need to contact us if everything is correct.".format(today.year, send_by_date, today.year)
                    body = '<body style="font-family:Calibri"><p>{}</p><p>{}</p>'.format(salutation, body_string)
                    body += '</br>'
                    body += '<p>'
                    for ind in range(11):
                        if input_values[ind] == "Author Details:":
                            body+='<b>{}</b>'.format(input_values[ind])
                        else:
                            if ":" in input_values[ind]:
                                body +='<p><b>{}</b><i>{}</i></p>'.format( input_values[ind].split(":")[0] + ": ", input_values[ind].split(":")[1] )
                            else:
                                body_add.append('<p><i>{}</i></b></p>'.format( input_values[ind]))
                    for ind in range(len(body_add)):
                        body+= body_add[ind]
                    body_add = []
                    x_titles= ["Title","Royalties", "Eligibility"]
                    x_border = "-"* 110+'<br />'  
                    x_titles_header = "&nbsp;"*3+x_titles[0]+","+"&nbsp;" + x_titles[1]+ "&nbsp;"+"and" + "&nbsp;"+ x_titles[2] + "&nbsp;"*15 +'<br />'  
                    #this for loop creates table inside of email body
                    for lst in author_list:
                        new_title = separator(lst[0], 75)
                        new_royalties = lst[1]
                        new_eligibility = separator(lst[2].lstrip(" "), 100)
                        new_royalties = new_royalties.lstrip(" ").split(" ")[1].strip("%")
                        new_royalties = '{0:g}'.format(float(new_royalties))# to get rid of zeros
                        new_royalties = new_royalties + "%"


                        one_title = '&nbsp;'*3 + new_title+"<br />" + '&nbsp;'*3 + "Royalties: " + new_royalties + '<br />' +  '&nbsp;'*3 + new_eligibility+"<br />" + x_border +'<br />'
                        full_titles += one_title 
                    body +=  '<p>' + x_border + x_titles_header+x_border + full_titles+ '</p>' + '<p>Yours sincerely,</p><p><b>Faye Rodgers</b></p><p>Public Lending Right for New Zealand Authors</p><p><b>National Library of New Zealand | Te Puna M&#257tauranga o Aotearoa</b></p><p>Direct Dial: +64 4 470 4528</p><span><img alt="NLNZ-logo" width = "300" src = "http://www.dia.govt.nz/diawebsite.nsf/Files/NationalLibrarylogo/$file/NationalLibrarylogo.png"></img></body>'
                    body = body.replace("’","'")
#################################################################################################HTML is ready############################################################################################################
######################################################################################Using Gen_Emails class EmailGen method##############################################################################################
###############################################################################################Making test folder#######################################################################################################
                    if email_count%500 == 0:
                      try:
                        maker.EmailGen(test_email, body, authorid, test_folder)
                      except UnicodeDecodeError as e:
                        print("Error ", str(e), " can not process test emails ", to_address)
                    try:
                      maker.EmailGen(to_address, body, authorid, email_folder)
                    except UnicodeDecodeError as e:
                      print("Error ", str(e), " can not process ", to_address)
########################################################################################Gather data between record delimiters#############################################################################################
            else:

                small_list.append(line)

    xmlfile.close()
            
if __name__ == '__main__':
    main()


