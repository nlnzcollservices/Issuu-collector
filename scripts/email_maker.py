import os
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from textwrap import wrap
from decimal import Decimal
from datetime import datetime

                        

 

############################################Jay's old code###################################################################

class Gen_Emails(object):
    def __init__(self):
        pass

    def EmailGen(self, to_address, subject, message, f_name, folder):
        filename = os.path.join(folder,f_name+'.eml' )
        #inserting a current year to the subject line
        today = datetime.today()
        msg = MIMEMultipart('alternative')
        msg['X-Unsent'] = '1'
        msg['Subject'] = subject
        msg['To'] = to_address
        body = MIMEText(message.encode("utf-8", "replace"), 'html', _charset="UTF-8")
        msg.attach(body)
        self.SaveToFile(msg, filename)
        
    def SaveToFile(self, msg, filename ):
        with open(filename, 'w') as outfile:
            gen = generator.Generator(outfile)
            gen.flatten(msg)





            
if __name__ == '__main__':
    main()


