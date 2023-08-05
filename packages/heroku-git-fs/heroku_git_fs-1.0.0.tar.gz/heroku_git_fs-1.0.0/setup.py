from setuptools import setup

setup(name='heroku_git_fs',
      version='1.0.0',
      packages=['heroku_git_fs'],
      license='GNU GPLv3.0',
      install_requires=[
          'GitPython',
      ],
      description='A python module/class to sync data to a git repository. Designed for ephemeral filesystems.',
      long_description=open('README.md').read(),
      url='https://github.com/ev1l0rd/heroku_git_fs',
      author='Valentijn "ev1l0rd"',
      author_email='contact@ev1l0rd.info',
      project_urls={'Documentation': 'http://heroku-git-fs.readthedocs.io/en/latest/'}
      )
