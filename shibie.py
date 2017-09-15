#-*-encoding:utf-8-*-
import pytesseract
from PIL import Image

class GetImageDate(object):
    def m(self):
        image = Image.open(u"C:\\4.jpg")
        text = pytesseract.image_to_string(image)
        return text

    def SaveResultToDocument(self):
        text = self.m()
        f = open(u"D:\\Verification.txt","w")
        print(text)
        f.write(str(text))
        f.close()

if __name__=="__main__":
    g = GetImageDate()
    g.SaveResultToDocument()