try:
    from setuptools import setup
except:
    from distutils.core import setup
setup(
    name='super-crawler',
    packages=['package1', 'package2'],
    version='0.1.0',
    description='第一個上架套件',
    author='telliex',
    author_email='telliexyuzo@gmail.com',
    url='https://github.com/telliex/pip_project_1.git',
    download_url='https://github.com/telliex/pip_project_1/archive/v0.1.0.zip',
    keywords=['crawler'],
    classifiers=['License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Intended Audience :: Developers',
                 'Operating System :: OS Independent', ]
)
