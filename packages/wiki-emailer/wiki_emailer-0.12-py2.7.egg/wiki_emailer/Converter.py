'''
Converter class
Author: Steve Brownfield
Created: 4/15/2018
'''
import pypandoc

class Converter:
    '''Class to convert markdown file to a pdf file for emailing'''

    def md_to_pdf(self, infile_name, outfile_name):
        '''This function will convert an md file to a pdf


        :param infile_name: name of the markdown file to convert
        :param outfile_name: name for the pdf file output
        '''
        try:
            pypandoc.convert(infile_name, 'pdf', outputfile=outfile_name, extra_args=['-V', 'geometry:margin=1.5cm'])
        except ImportError:
            print("warning: pypandoc module not found, could not convert Markdown to pdf")
			
			
			