from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='bvtextprocessing',
      version='0.1',
      description='Small library for text processing',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='text processing',
      author='Dmitry Bolkunov',
      author_email='d.bolkunov@gmail.com',
      url='https://bitbucket.org/dbolkunov/bvtextprocessing/src',
      license='MIT',
      packages=['bvtextprocessing'],
      install_requires=[
                'snowballstemmer',
            ],
      zip_safe=False)
