from setuptools import setup

setup(name='astropixie',
      version='0.1.0',
      description='LSST EPO python library.',
      url='https://github.com/lsst-epo/vela/astropixie',
      author='LSST EPO Team',
      author_email='epo-team@lists.lsst.org',
      license='MIT',
      packages=['astropixie'],
      include_package_data=True,
      package_data={'astropixie': ['sample_data/*']},
      install_requires=[
          'astropy',
          'numpy',
          'pandas',
          'pytest'
      ])
