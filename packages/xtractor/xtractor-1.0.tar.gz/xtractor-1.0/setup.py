from distutils.core import setup
setup(
  name = 'xtractor',
  packages = ['xtractor'], # this must be the same as the name above
  version = '1.0',
  description = 'Topic extractor with the idea of generating labels using genism.n_similarity',
  author = 'Peter Nagy',
  author_email = 'nagypeterjob@gmail.com',
  url = 'https://github.com/nagypeterjob/xtractor', # use the URL to the github repo
  download_url = 'https://github.com/nagypeterjob/xtractor/archive/1.0.tar.gz', # I'll explain this in a second
  keywords = ['topic-extraction', 'machine-learning', 'genism', 'python', 'pandas', 'labels'], # arbitrary keywords
  classifiers = [],
)
