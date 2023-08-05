from distutils.core import setup
setup(
  name='fluent_bundle',
  packages=['fluent_bundle'],
  version='1.00',
  description='fluentd support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/applauncher-team/fluent_bundle',
  download_url='https://github.com/applauncher-team/fluent_bundle',
  keywords=['fluentd'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'fluent-logger']
)
