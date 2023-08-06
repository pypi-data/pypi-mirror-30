from setuptools import setup

setup(name='cenpy',
      version='0.9.8',
      description='Explore and download data from Census APIs',
      url='https://github.com/ljwolf/cenpy',
      author='Levi John Wolf',
      author_email='levi.john.wolf@gmail.com',
      license='3-Clause BSD',
      python_requires='>=3.5',
      packages=['cenpy'],
      install_requires=['pandas', 'requests', 'pysal'],
      package_data={'cenpy': ['stfipstable.csv']},
      zip_safe=False)
