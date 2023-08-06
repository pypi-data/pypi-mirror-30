from setuptools import setup


with open('requirements.txt') as fp:
    requirements = fp.read().splitlines()

with open('README.md') as fp:
    readme = fp.read()


setup(
    name='mrkd',
    version='0.1.5',
    description='Write man pages using Markdown, and convert them to Roff or HTML',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Ryan Gonzalez',
    author_email='rymg19@gmail.com',
    license='BSD',
    url='https://github.com/kirbyfan64/mrkd',
    py_modules=['mrkd'],
    entry_points={
        'console_scripts': [
            'mrkd=mrkd:main',
        ],
    },
    package_data={
        '': ['template.html'],
    },
    install_requires=requirements,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3.6',
    ],
    keywords='man markdown roff html',
)
