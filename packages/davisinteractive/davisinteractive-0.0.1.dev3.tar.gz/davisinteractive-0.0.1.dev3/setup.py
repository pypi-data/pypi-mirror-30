from setuptools import setup

with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(
    # name='davisinteractive',
    # version='0.0.2',
    # description='Evaluation framework for DAVIS interactive segmentation.',
    # long_description=long_description,
    # long_description_content_type='text/markdown',
    # url='http://github.com/albertomontesg/davis-interactive',
    # author='Alberto Montes',
    # author_email='al.montes.gomez@gmail.com',
    # license='GPL v3',
    # packages=['davisinteractive'],
    install_requires=[
        'numpy>=1.12.1', 'scikit-learn>=0.18', 'scikit-image>=0.13.1',
        'networkx>=2.0', 'scipy>=1.0.0', 'pandas>=0.21.1', 'absl-py>=0.1.13',
        'Pillow>=4.1.1'
    ],
    setup_requires=['pytest-runner'],
    test_require=['pytest', 'pytest-cov'],
    # include_package_data=True,
    # zip_safe=False,
    # project_urls={
    #     'Bug Tracker':
    #     'https://github.com/albertomontesg/davis-interactive/issues',
    #     'Documentation':
    #     'interactive.davischallenge.org',
    #     'Source Code:':
    #     'https://github.com/albertomontesg/davis-interactive'
    # },
    keywords=[],
    classifiers=[])
