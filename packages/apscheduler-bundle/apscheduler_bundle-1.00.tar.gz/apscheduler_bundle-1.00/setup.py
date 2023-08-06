from distutils.core import setup
setup(
  name='apscheduler_bundle',
  packages=['apscheduler_bundle'],
  version='1.00',
  description='APScheduler support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/applauncher-team/apscheduler_bundle',
  download_url='https://github.com/applauncher-team/apscheduler_bundle',
  keywords=['mqtt', 'paho'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'apscheduler']
)
