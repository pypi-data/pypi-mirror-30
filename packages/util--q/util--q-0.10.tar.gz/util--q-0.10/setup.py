from setuptools import setup, find_packages

setup(
    name='util--q',  # 名称
    version='0.10',  # 版本
    description="python开发常用工具",  # 描述
    keywords='python english translation dictionary terminal',
    author='qinxiao',  # 作者
    author_email='mllib_fiy@163.com',  # 作者邮箱
    url='https://github.com/MLlibfiy',  # 作者链接
    packages=find_packages(exclude=['SSXRelation']),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [  # 如果你想要以Linux命令的形式使用
            'bword = bword.bword:main'
        ]
    },
)
