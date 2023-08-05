from setuptools import setup

setup(name='claims_helper',
      version='0.1.3',
      description='Decodes roles from custom claims',
      url='',
      author='Blaze devices',
      author_email='devices@blaze.cc',
      license='MIT',
      packages=['claims_helper'],
      install_requires=[
          'requests', 'flask'
      ],
      zip_safe=False)