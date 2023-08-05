from setuptools import setup

setup(name='pyladins',
      version='0.1',
      description='Python API for paladins',
      url='http://github.com/shubhstiws/paladins',
      author='Shubhankar Tiwari',
      author_email='shubhstiws@gmail.com',
      license='MIT',
      packages=['pyladins'],
      zip_safe=False,
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    	keywords='paladins setuptools development'
    	)