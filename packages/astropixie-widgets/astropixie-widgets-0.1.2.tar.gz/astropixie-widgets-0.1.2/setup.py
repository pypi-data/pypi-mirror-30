from setuptools import setup

setup(name='astropixie-widgets',
      version='0.1.2',
      description='LSST EPO ',
      url='https://github.com/lsst-epo/vela/astropixie-hr',
      author='LSST EPO Team',
      author_email='epo-team@lists.lsst.org',
      license='MIT',
      packages=['astropixie_widgets'],
      include_package_data=True,
      package_data={'astropixie': ['sample_data/*']},
      install_requires=[
          'astropixie',
          'astropy==3.0',
          'astroquery',
          'bokeh>=0.12.15',
          # 'ipyaladin',
          'numpy==1.14.1',
          'pandas',
          'pytest',
          'scipy'
      ])
