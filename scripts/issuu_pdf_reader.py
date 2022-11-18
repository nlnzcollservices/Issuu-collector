#!python3

import os
from shutil import copyfile
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import PyPDF2
import re

class IssuuPdf:
    def __init__(self, path):
        self.path = path

    def parse_pdf(self):

        volume = None
        season = None
        year = None
        month = None
        issue = None
        if self.magazine_name in ['Business_central', 'Business_north', 'Business_south','Interclub_New_Zealand']:
                    volume = re.findall("Volume (\w+)", self.text)[0].rstrip(" ")
                    issue = re.findall("Issue (\w)", self.text)[0].rstrip(" ")
                    year= re.findall('\d{4}', self.text)[0].rstrip(" ")
                    if self.magazine_name in ['Business_central', 'Business_north', 'Business_south']:
                        pattern1 = issue+" \| "
                        pattern2 = year
                        month = re.findall( "{}(.*?){}".format(pattern1, pattern2),self.text)[0].rstrip(" ")
                # print(issue)
                # print(volume)
                # print(month)
                # print(year)
        if self.magazine_name in ['Business_rural','NZ_dairy','Business_rural_north','Go_travel_New_Zealand','Swings_and_roundabouts','RSA_review']:
            season= re.findall('Summer|Autumn|Winter|Spring|SUMMER|AUTUMN|WINTER|SPRING', self.text)[0].rstrip(" ")
            #print(season)
            year = re.findall("{} (\d+)".format(season),  self.text)[0].rstrip(" ")
            #print(season, year)
            if self.magazine_name in ['RSA_review']:
                issue = re.search('ISSUE (\d+)',self.text)[0].lstrip("ISSUE ").rstrip(" ")
                #print(issue)
        self.issue = issue
        self.volume = volume
        self.season = season
        self.month =  month
        self.year =  year
        self.pdf_dictionary = {"volume":self.volume, "issue":self.issue,"season":self.season, "month":self.month, "year":self.year}


    def read_pdf_cover(self):

        read_pdf = PyPDF2.PdfFileReader(self.path)
        number_of_pages = read_pdf.getNumPages()
        page = read_pdf.getPage(0)
        #print(dir(page))
        page_content = page.extractText()
        self.text = page_content

    def issuu_pdf_routine(self):

        self.magazine_name = self.path.split("\\")[-2]
        self.read_pdf_cover()
        #print(self.text)
        self.parse_pdf()

def main():

    links = [r"Y:\ndha\pre-deposit_prod\LD_working\issuu_main\test_file\test.pdf"]
    link = links[0]
    my_pdf = IssuuPdf(links[0])
    for link in links:
        my_pdf.read_pdf_cover()
        print(my_pdf.text)
        filename = link.split('\\')[-1].split(".pdf")[0]
        magazine_name = link.split("\\")[-2]
        # for el in self.text.split("\n"):
        #     print(el)
        print("#"*50)
        quit()
        print(self.magazine_name)
        issue, volume, season, month, year = parse_pdf(magazine_name)
        print(volume, issue, season, month, year)






if __name__ == '__main__':
    main()