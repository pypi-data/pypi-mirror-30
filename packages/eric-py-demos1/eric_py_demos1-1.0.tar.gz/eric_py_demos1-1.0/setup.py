# coding=utf-8
# author:dn_eric(qq:2384363842)
# 动脑学院pythonVip课程
# 创建于: 2018/3/20 16:54
from setuptools import setup

setup(
    name='eric_py_demos1',  # 应用名
    version='1.0',  # 版本号
    description='setuptools demos',
    packages=['eric_py_demos',],  # 包括在安装包内的Python包
    author="dn_eric",  # 作者
    author_email="hustcsxg@163.com",  # 邮箱
    url="http://hustcsxg.github.io",  # 主页
    license='MIT',
    install_requires=['requests', ],
    entry_points={
        'console_scripts': ['eric_py_demos=eric_py_demos.command_lines:main'],
    },
)
