from setuptools import setup

setup(name='photo-gen',
      version='0.2',
      description='Generate HTML galleries from a folder of folder of jpegs',
      url='http://github.com/hjertnes/photo2',
      author='Eivind Hjertnes',
      author_email='me@hjertnes.me',
      packages=['photo-gen'],
      install_requires=['pillow', 'jinja2'],
      zip_safe=False)
