from distutils.core import setup
setup(
  name='mqtt_bundle',
  packages=['mqtt_bundle'],
  version='1.00',
  description='mqtt support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/applauncher-team/mqtt_bundle',
  download_url='https://github.com/applauncher-team/fluent_bundle',
  keywords=['mqtt', 'paho'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'paho-mqtt']
)
