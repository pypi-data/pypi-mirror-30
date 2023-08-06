from setuptools import setup

readme = open('README.rst').read()

requirements = {
    "package": [
        'six',
        'requests',
        'yamlsettings>=1.0.1',
    ],
    "setup": [
        "pytest-runner",
    ],
    "test": [
        "responses",
        "pytest",
        "pytest-pudb",
    ],
}

requirements.update(all=sorted(set().union(*requirements.values())))

setup(
    name='yamlsettings-requests',
    version='1.0.0',
    author='Kyle Walker',
    author_email='KyleJamesWalker@gmail.com',
    description='YamlSettings Request Extension',
    long_description=readme,
    py_modules=['yamlsettings_requests'],
    extras_require=requirements,
    install_requires=requirements['package'],
    setup_requires=requirements['setup'],
    tests_require=requirements['test'],
    entry_points={
        'yamlsettings10': [
            'ext = yamlsettings_requests:RequestsExtension',
        ],
    },
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
