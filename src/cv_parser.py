
# importing required modules
import PyPDF2
# import re


def cvAnalizer(CV):
    # creating a pdf file object
    skills = ['Java', 'C++', 'Matlab', 'Lua', 'Objective C', 'Python', 'Swift', 'SQL',
              'React', 'Flask', 'Django', 'HTML', 'CSS', 'Ruby', 'Git', 'Javascript', 'Julia']
    existing = []
    pdfFileObj = open(CV, 'rb')

    # initializing punctuations string
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    # printing number of pages in pdf file
    page_num = pdfReader.numPages
    for i in range(page_num):
        # creating a page object
        pageObj = pdfReader.getPage(i)
        # extracting text from page
        text = pageObj.extractText()
        text_fixed = text
        # text_fixed = re.sub(r'[^\w\s]', '', text)
        # Removing punctuations in string
        # Using loop + punctuation string
        for ele in text_fixed.split():
            if ele in punc:
                text_fixed = text_fixed.replace(ele, "")
        for s in skills:
            if s.lower() in text_fixed.lower():
                existing.append(s)
    # print(existing)
    # closing the pdf file object
    pdfFileObj.close()
    return (existing)
