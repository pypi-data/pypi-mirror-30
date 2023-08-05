from setuptools import setup

setup(
    name='hn-tops-topics',
    version='0.1.1',
    scripts=['hn-tops-topics'],
    description = 'Scrap the tops HN news and filters by topics',
    author = 'Juan Chavat',
    author_email = 'jupach@gmail.com',
    install_requires=[
        'colorconsole',
        'requests_html',
    ]
)