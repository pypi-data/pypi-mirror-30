from setuptools import setup

# see http://python-packaging.readthedocs.io/en/latest/minimal.html
# 
# python setup.py register
# python setup.py sdist

setup(name='rainbowmindmachine',
      version='0.4',
      description='An extendable framework for running Twitter bot flocks.',
      url='http://github.com/charlesreid1/rainbow-mind-machine',
      author='charlesreid1',
      author_email='charles@charlesreid1.com',
      license='MIT',
      packages=['rainbowmindmachine'],
      zip_safe=False)

