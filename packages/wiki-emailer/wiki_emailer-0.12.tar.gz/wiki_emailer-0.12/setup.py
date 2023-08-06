from setuptools import setup, find_packages

setup(
    name='wiki_emailer',
    version='0.12',
	py_modules=['Converter', 'Emailer'],
	install_requires=[
          'pypandoc',
		  'flask_mail',
		  'flask'
      ],
    packages=find_packages(exclude=['test*']),
    url='',
    license='',
    author='Steve Brownfield',
    author_email='brownfiels2@nku.edu',
    description='Convert a markdown file to pdf and send it via email'
)