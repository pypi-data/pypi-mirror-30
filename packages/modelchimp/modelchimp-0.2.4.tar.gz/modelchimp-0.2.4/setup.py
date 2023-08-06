from setuptools import setup

setup(
  name = 'modelchimp',
  packages = ['modelchimp'], # this must be the same as the name above
  version = '0.2.4',
  description = 'Python client to upload the machine learning models data to the model chimp cloud',
  author = 'Samir Madhavan',
  author_email = 'samir.madhavan@gmail.com',
  url = 'https://github.com/samzer/modelchimp-client-python', # use the URL to the github repo
  download_url = 'https://github.com/samzer/modelchimp-client-python/archive/0.1.2.tar.gz', # I'll explain this in a second
  keywords = ['modelchimp', 'ai', 'datascience'], # arbitrary keywords
  install_requires=[
          'requests',
          'future',
          'six',
      ],
  classifiers = [],
)
