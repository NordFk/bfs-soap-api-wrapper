from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='bfs',
      version='0.6',
      description='Bricknode Financial Systems SOAP API wrapper',
      long_description=readme(),
      url='http://bitbucket.org/nordfk/bfs-soap-api-wrapper',
      author='Joakim Platbarzdis',
      author_email='joakim.platbarzdis@nordfk.se',
      packages=[
          'bfs',
          'bfs/constants'
      ],
      install_requires=[
          'zeep',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
