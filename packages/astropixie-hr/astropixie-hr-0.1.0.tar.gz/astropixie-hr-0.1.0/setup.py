from setuptools import setup

setup(name='astropixie-hr',
      version='0.1.0',
      description='LSST EPO Hertzsprung-Russell (HR) Diagram library.',
      url='https://github.com/lsst-epo/vela/astropixie-hr',
      author='LSST EPO Team',
      author_email='epo-team@lists.lsst.org',
      license='MIT',
      packages=['astropixie_hr'],
      include_package_data=True,
      package_data={'astropixie': ['sample_data/*']},
      install_requires=[
          'astropixie',
          'astropy',
          'astroquery',
          'bokeh',
          # 'ipyaladin',
          'numpy',
          'pandas',
          'pytest',
          'scipy'
      ])
