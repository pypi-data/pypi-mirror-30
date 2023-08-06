from setuptools import setup

setup(name='bitcoinpaygate',
      version='0.3',
      description='The python client for Bitcoinpaygate API',
      url='https://github.com/bitcoinpaygate/python-api-client',
      author='Bitcoinpaygate',
      author_email='support@bitcoinpaygate.com',
      license='MIT',
      packages=['bitcoinpaygate'],
      install_requires=[
        'requests',
      ],
      test_suite='nose.collector',
      tests_require=[
      	'nose',
      	'pretenders'
      ])
