from setuptools import setup

setup(name='ctkapi',
      version='1.0',
      description='Centra SDK for third party integration',
      url='https://github.com/CentraTech/Centra',
      author='centra',
      author_email='support@centra.tech',
      license='MIT',
      packages=['ctkapi'],
      install_requires=[
          'requests',
           "pyyaml",
           
      ],
      zip_safe=False)