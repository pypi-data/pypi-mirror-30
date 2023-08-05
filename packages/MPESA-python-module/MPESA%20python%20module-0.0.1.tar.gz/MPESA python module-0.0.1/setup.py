from setuptools import setup

setup(
    name='MPESA python module',
    version='0.0.1',
    description='MPESA Python Module',
    license='MIT',
    py_modules=["src"],
    install_requires=['openssl', 'SWIG', 'M2Crypto', 'requests'], 
    author='Karienye Sheila Wambui',
    author_email='sheila.karienye@gmail.com',
    keywords=['MPESA python module'],
    url='https://developer.safaricom.co.ke'
)