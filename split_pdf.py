from PyPDF2 import PdfFileWriter, PdfFileReader

inputpdf = PdfFileReader(open("/Users/pratik/Desktop/test_ocr/pdf/p.pdf", "rb"))

for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(i))
    outputFiles = open("/Users/pratik/Desktop/test_ocr/pagepdf/%s.pdf" % i, "wb")
    output.write(outputFiles)
    outputFiles.close()

    # with open("document-page%s.pdf" % i, "wb") as outputStream:
    #     output.write(outputStream)
