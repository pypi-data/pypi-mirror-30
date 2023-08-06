from setuptools import setup, find_packages


with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

setup(name='py_thesaurus',
      version='1.0.4',
      description='To fetch the thesaurus of an input word',
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Manufacturing',
          'Intended Audience :: Other Audience',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Topic :: Text Processing :: Linguistic'],
      url='https://bitbucket.org/redpills01/py_thesaurus.git',
      keywords='nlp text-mining',
      author='red_pills',
      author_email='redpillsworkspace@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests*', 'red_pill*']),
      install_requires=["lxml", "beautifulsoup4"],
      entry_points={"console_scripts": ['py_thesaurus=py_thesaurus.main:main']},
      zip_safe=False)

