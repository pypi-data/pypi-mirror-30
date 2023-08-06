from setuptools import setup

setup(name='photo-gen',
      version='0.1',
      description='Generate HTML galleries from a folder of folder of jpegs',
      url='http://github.com/hjertnes/photo2',
      author='Eivind Hjertnes',
      author_email='me@hjertnes.me',
      packages=['photogen'],
      install_requires=['pillow', 'jinja2'],
      zip_safe=False)
