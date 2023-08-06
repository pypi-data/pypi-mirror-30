from setuptools import setup


setup(name='tdc101',
      version='1.0.0',
      description='Teste de narração',
      author='Klinsman Jorge',
      license='MIT',
      packages=['tdc101'],
      zip_safe=False,
      classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
      install_requires=['python-vlc'],

      data_files=[('tdc101',['data/Problema de rede.mp3'])]
      )

