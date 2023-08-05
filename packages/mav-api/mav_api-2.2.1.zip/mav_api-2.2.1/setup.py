from distutils.core import setup
import mavapi.api

setup(
    name='mav_api',
    version=mavapi.api.__version__,
    install_requires=['asyncio', 'aiohttp'],
    packages=['mavapi'],
    url='https://github.com/Ar4ikov/mavapi',
    license='MIT License',
    author='Nikita Archikov',
    author_email='bizy18588@gmail.com',
    description='A simple to use MAV API Wrapper for python (3.5 or newer)',
    keywords='mavapi mav api wrappper rugaming'

)
