from setuptools import setup

setup(name='nxaddons',
      version='0.0.2',
      description='Extended tools for NetworkX package',
      url='https://github.com/harsgak/nxaddons',
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