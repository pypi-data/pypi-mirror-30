from setuptools import setup, find_packages
setup(
    name='dxl-medimage',
    version='0.0.4',
    description='Medical Image Processing Library.',
    url='https://github.com/Hong-Xiang/dxmedimage',
    author='Hong Xiang',
    author_email='hx.hongxiang@gmail.com',
    license='MIT',
    namespace_packages=['dxl'],
    packages=find_packages('src/python'), 
    package_dir={'': 'src/python'},
    install_requires=[],
    scripts=[],
    #   namespace_packages = ['dxl'],
    zip_safe=False)
