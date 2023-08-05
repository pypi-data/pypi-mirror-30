from setuptools import setup

setup(name='nxaddons',
      version='0.0.1',
      description='Extended tools for NetworkX package',
      url='https://gist.github.com/harsgak/37e88b53cf0f3edf4ccf90b5af371bad',
      author='harsgak',
      author_email='harsgak@yahoo.com',
      license='MIT',
      packages=['nxaddons'],
      install_requires=[
          'networkx', 'matplotlib', 'numpy'
      ],
      classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License'
      ],
      zip_safe=False)