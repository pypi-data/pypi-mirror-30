from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='UmbrellaIntegrate',
      version='0.41',
      description='The umbrella integration algorithm.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry'
      ],
      python_requires='>=3',
      keywords='umbrella integration',
      url='https://github.com/shirui816/UmbrellaIntegrate.py',
      author='Shirui',
      author_email='Shirui816@gmail.com',
      license='MIT',
      scripts=['ubint'],
      install_requires=[
          'numpy',
          'scipy',
          'pandas'
      ],
      include_package_data=True,
      zip_safe=False)
