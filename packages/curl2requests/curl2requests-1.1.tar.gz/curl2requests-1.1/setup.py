from distutils.core import setup
setup(
  name = 'curl2requests',
  packages = ['curl2requests'], # this must be the same as the name above
  version = '1.1',
  description = 'This module gets informations from cURL command and returns them in JSON format.',
  author = 'mark0smith',
  author_email = 'm11711237@gmail.com',
  url = 'https://github.com/a4m/curl2requests', # use the URL to the github repo
  download_url = 'https://github.com/a4m/curl2requests/archive/1.1.tar.gz', # I'll explain this in a second
  keywords = ['cURL', 'requests'], # arbitrary keywords
  classifiers = [
      'Programming Language :: Python',
      'Development Status :: 3 - Alpha',
  ],
)
