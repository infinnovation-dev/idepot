from setuptools import setup
setup(name='idepot',
      version='0.1',
      description="Manage software updates via symlinks",
      author="Colin Hogben",
      author_email="colin@infinnovation.co.uk",
      project_urls={
          "Source Code": "https://github.com/infinnovation-dev/iidepot.git",
      },
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: System Administrators',
          'Topic :: System :: Systems Administration',
          'Operating System :: POSIX :: Linux'
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      py_modules=['idepot'],
      entry_points={
          'console_scripts': [
              'idepot = idepot:main',
          ],
      },
)
