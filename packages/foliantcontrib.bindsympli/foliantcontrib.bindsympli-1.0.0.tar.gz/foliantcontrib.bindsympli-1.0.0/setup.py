from setuptools import setup


SHORT_DESCRIPTION = 'Sympli integration preprocessor for Foliant.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliantcontrib.bindsympli',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='1.0.0',
    author='Artemy Lomov',
    author_email='artemy@lomov.ru',
    url='https://github.com/foliant-docs/foliantcontrib.bindsympli',
    packages=['foliant.preprocessors'],
    license='MIT',
    install_requires=[
        'foliant>=1.0.0'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ],
    data_files=[
        (
            '/usr/local/bin', [
                'non_python_scripts/bind_sympli_imgs.pl',
                'non_python_scripts/get_sympli_design_urls.pl',
                'non_python_scripts/get_sympli_img_urls.js'
            ]
        )
    ]
)
