from setuptools import setup

setup(name='terraref-stereo_rgb',
      version='1.0.1',
      packages=['terraref.stereo_rgb'],
      include_package_data=True,
      url='https://github.com/terraref/stereo_rgb',
      install_requires=[
            'numpy',
            'scipy',
            'multiprocessing',
            'matplotlib',
            'Pillow'
      ]
      )
