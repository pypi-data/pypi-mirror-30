from distutils.core import setup
setup(
  name = 'matialvarezs_handlers_easy',
  packages = ['matialvarezs_handlers_easy'], # this must be the same as the name above
  version = '0.1.9',
  install_requires = [
    'simplejson==3.13.2',
  ],
  include_package_data = True,
  description = 'Easy handler',
  author = 'Matias Alvarez Sabate',
  author_email = 'matialvarezs@gmail.com',
  classifiers = [
    'Programming Language :: Python :: 3.5',
  ],
)