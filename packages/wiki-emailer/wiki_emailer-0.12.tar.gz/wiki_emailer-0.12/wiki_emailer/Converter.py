import pypandoc

class Converter:
    '''Class to convert markdown file to a pdf file for emailing'''

    def md_to_pdf(self, infile, outfile):
        try:
            pypandoc.convert(infile, 'pdf', outputfile=outfile, extra_args=['-V', 'geometry:margin=1.5cm'])
        except ImportError:
            print("warning: pypandoc module not found, could not convert Markdown to pdf")
			
			
			