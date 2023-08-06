from setuptools import setup

setup(name='requests_throttled',
      version='0.3',
      description='Throttling requests.Session.',
      url='http://github.com/zaquest/requests_throttled',
      author='zaquest',
      author_email='web.elektro.net@gmail.com',
      license='MIT',
      install_requires=['requests'],
      py_modules=['requests_throttled'],
      zip_safe=True)
