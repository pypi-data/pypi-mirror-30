from setuptools import setup

setup(
    name='zmzget',
    version='0.1.0',
    author='Yuan Chen',
    author_email='huddsinyuan2014@gmail.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: System :: Logging',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows :: Windows 10',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3',
    install_requires=["requests_html"],
    description='CLI Tool for fetching the updating zimuzu tv serials.',
    long_description='This tool is used to fetch update info from zimuzu.\n'
                     'About TV serials.\n'
                     'Any Problem/PR is welcomed.\n'
                     'Mail: huddsinyuan2014@gmail.com\n'
                     '',
    entry_points={
        'console_scripts': [
            'zmzget = main:runPipeline'
        ]
    })
