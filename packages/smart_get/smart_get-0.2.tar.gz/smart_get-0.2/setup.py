from distutils.core import setup
setup(
  name='smart_get',
  packages=['smart_get'],
  version='0.2',
  description="Automatically assign user agent and check encoding for html.",
  author='Terry Hung',
  author_email='terryhung1228@gmail.com',
  url='https://github.com/Terryhung/Smart_Get',
  download_url='https://github.com/Terryhung/Smart_Get/archive/master.zip',
  keywords=['user_agent', 'requests', 'encoding', 'auto'],
  install_requires=['bs4', 'requests'],
  classifiers=[],
)
