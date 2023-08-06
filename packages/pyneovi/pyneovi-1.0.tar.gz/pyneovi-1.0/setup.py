from setuptools import setup

readme_file = open('README.txt', 'r')
long_description = '\n'.join(readme_file.readlines())
readme_file.close()

setup(name='pyneovi',
      packages=['neovi'],
      version='1.0',
      description='A wrapper around the API provided by Intrepid Control Systems for communicating with their NeoVI range of devices',
      long_description=long_description,
      author='John Kemp',
      author_email='kemp@kempj.co.uk',
      url='http://kempj.co.uk/projects/pyneovi/',
      license='MIT',
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
      ]
)
