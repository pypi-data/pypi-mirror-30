from setuptools import setup

# see http://python-packaging.readthedocs.io/en/latest/minimal.html
# and https://packaging.python.org/guides/migrating-to-pypi-org/#uploading
# and https://gist.github.com/gboeing/dcfaf5e13fad16fc500717a3a324ec17
# 
# one time:
# 
#   $ python setup.py register
# 
# add following to ~/.pypirc:
# 
# [distutils]
# index-servers =
#     pypi
# 
# [pypi]
# username:charlesreid1
# password:YOURPASSWORDHERE
#
# make distribution package bundle:
# 
#   $ python setup.py sdist
#
# upload it to pypi:
# 
#   $ python setup.py sdist upload
#
# test it out with virtualenv:
#
#   $ virtualenv vp && cd vp
#   $ source bin/activate
#   $ bin/pip install rainbowmindmachine


setup(name='rainbowmindmachine',
      version='0.6.1',
      description='An extendable framework for running Twitter bot flocks.',
      url='http://charlesreid1.github.io/rainbow-mind-machine',
      author='charlesreid1',
      author_email='charles@charlesreid1.com',
      install_requires = ['simplejson==3.13',
          'oauth2>=1.5','python-twitter==3.4.1',
          'TwitterAPI==2.4.6','TextBlob==0.15'],
      license='MIT',
      packages=['rainbowmindmachine'],
      zip_safe=False)

