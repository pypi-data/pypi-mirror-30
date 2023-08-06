from setuptools import setup, find_packages

setup(
    name='wiki_emailer',
    version='2.0',
	py_modules=['Emailer'],
	install_requires=[
          'pypandoc',
      ],
    packages=find_packages(exclude=['test*']),
    url='',
    license='',
    author='Steve Brownfield',
    author_email='brownfiels2@nku.edu',
    description='Convert a markdown file to pdf and sends it via email'
)