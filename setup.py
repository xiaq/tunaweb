from setuptools import setup


setup_args = dict(
    name='tunaweb',
    install_requires=[
        'Flask>=0.8',
        'flatland==dev',
    ],
    entry_points=dict(
        console_scripts=['tunaweb = tunaweb.app:main'],
    ),
)

if __name__ == '__main__':
    setup(**setup_args)
