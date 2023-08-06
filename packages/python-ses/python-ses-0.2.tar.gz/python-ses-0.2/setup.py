from setuptools import setup

setup(name='python-ses',
      version='0.2',
      description='Simple usefull lib to send email using AWS SES',
      long_description='Really, the best around.',
      url='http://github.com/storborg/funniest',
      author='Aaron Dominguez - Destacame Spa',
      author_email='dominguezaaron75@gmail.com',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='aws ses python email emailing',
      packages=['python-ses'],
      install_requires=[
          'jinja2',
          'boto3'
      ],
      #dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0'],
      zip_safe=False)
