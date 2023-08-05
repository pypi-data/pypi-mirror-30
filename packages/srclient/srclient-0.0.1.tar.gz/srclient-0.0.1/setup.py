from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='srclient',
      version='0.0.1',
      description='A small client for short-report.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications',
        'Topic :: Internet :: WWW/HTTP',
      ],
      keywords='REST client coreapi short report',
      url='https://github.com/axju/short-report-client',
      author='Axel Juraske',
      author_email='axel.juraske@short-report.de',
      license='MIT',
      packages=['srclient'],
      scripts=['bin/short-report-client'],
      install_requires=[
          'coreapi', 'bs4', 'requests', 'argparse'
      ],
      zip_safe=False)
