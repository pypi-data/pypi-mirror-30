'''
setup安装配置详细参考文档，只使用项目相关的用法后续根据项目需要再完善。
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
'''
import io
import re
import os
import sys
from setuptools import setup, find_packages

# 约定当前文件所在的父目录名为包名称
PACKAGE_NAME = os.path.basename(os.path.dirname(__file__))


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# TODO 可以根据需要扩展相关的属性发布到PYPI服务器上分享传播
setup(
    name=PACKAGE_NAME,
    version=find_version('%s/__init__.py' % PACKAGE_NAME),
    packages=find_packages(),
    install_requires=['xbase', ],
    package_data={
        'autoweb': ['bin/darwin/chromedriver', 'bin/linux/phantomjs'],
    },
    # install_requires=[
    #     'django>=1.4',
    #     'django-braces>=1.2.2',
    #     'oauthlib==1.0.1',
    #     'six',
    # ],
)
