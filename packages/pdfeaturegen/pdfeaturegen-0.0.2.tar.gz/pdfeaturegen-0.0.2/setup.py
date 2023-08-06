from setuptools import setup
setup(name='pdfeaturegen',
      version='0.0.2',
      description='Supporting functions to generate features in Pandas Dataframe for Machine Learning',
      url='https://github.com/ivanfoong/pdfeaturegen',
      author='Ivan Foong',
      author_email='vonze21@gmail.com',
      license='MIT',
      packages=['pdfeaturegen'],
      install_requires=[
          'pandas',
      ],
      zip_safe=False)

