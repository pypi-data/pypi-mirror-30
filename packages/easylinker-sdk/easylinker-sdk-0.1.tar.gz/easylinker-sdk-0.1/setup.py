from setuptools import setup,find_packages
setup(
    name = 'easylinker-sdk',
    version = 0.1,
    packages = find_packages(),
    author = 'wwhai',
    author_email = '751957846@qq.com',
    url = 'http://www.easylinker.xyz',
    license = 'http://www.apache.org/licenses/LICENSE-2.0.html',
    description = 'EasyLinker python SDK',
    install_requires=['paho-mqtt']
    )
