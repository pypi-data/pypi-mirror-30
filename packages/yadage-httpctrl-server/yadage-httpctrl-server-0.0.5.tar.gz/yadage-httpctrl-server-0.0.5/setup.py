from setuptools import setup, find_packages

setup(
  name = 'yadage-httpctrl-server',
  version = '0.0.5',
  description = 'yadage http controller interfacint to persistent yadage controller',
  url = '',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  install_requires = [
    'click',
    'flask',
    'psutil',
    'requests[security]>2.9',
    'pyyaml',
    'jsonref',
    'yadage',
    'jsonschema',
    'pyyaml',
    'jq',
  ],
  entry_points = {
      'console_scripts': [
          'yadage-httpctrl-server=yadagehttpctrl.yadagehttpserver:serve',
      ],
  },
  dependency_links = [
  ]
)
