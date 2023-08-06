from setuptools import setup

setup(name='modellogging',
      version='1.0',
      description='Easily configured logging.',
      url='http://github.com/cidrblock/modellogging',
      author='Bradley A. Thornton',
      author_email='brad@thethorntons.net',
      license='MIT',
      packages=[
        'modellogging'
      ],
      install_requires=[
          'python_json_logger'
      ],
      zip_safe=False)
