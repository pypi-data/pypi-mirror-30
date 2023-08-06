# Setup file needed for distribution on PyPI.
#
# See the following blog post for a quick guide:
#
#     http://peterdowns.com/posts/first-time-with-pypi.html
#

from setuptools import setup, find_packages

# Setup function
setup(name='ostsa',
      packages=find_packages(),
      version='0.1.8.1',
      description=('A library for classifying malware files. This library '
                   'also contains various utilities for extending/building '
                   'your own specialized machine learning classifiers.'),
      author='Caleb Rush, Austin Julio, Andy Zheng',
      author_email='cir5274@psu.edu',
      url='https://github.com/psb-seclab/malware_classifier',
      download_url='https://github.com/psb-seclab/malware_classifier/archive/0.1.1.tar.gz',
      keywords=['machine learning', 'malware', 'pe', 'exe', 'dll', 
                'classifier', 'security', 'analysis'],
      install_requires=['scipy', 'mahotas', 'numpy', 'scikit-learn==0.18.1',
                        'capstone', 'pefile', 'Pillow', 'matplotlib'],
      include_package_data=True)
