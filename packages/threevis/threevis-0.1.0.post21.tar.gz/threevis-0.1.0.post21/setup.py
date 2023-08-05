from setuptools import setup


def readme():
    return open('README.md').read()


setup(
    name='threevis',
    use_scm_version={
        'version_scheme': 'post-release',
        'local_scheme': 'dirty-tag'
    },
    description='Visualize meshes, point clouds, and other geometry in a Jupyter Notebook',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://graphics.rwth-aachen.de:9000/threevis/threevis',
    author='Dario Seyb, Isaak Lim, Janis Born',
    author_email='isaak.lim@cs.rwth-aachen.de',
    license='BSD 3-Clause',
    packages=['threevis'],
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'numpy',
        'pythreejs>=1.0.0',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
    ],
    project_urls={
        'Source':'https://www.graphics.rwth-aachen.de:9000/threevis/threevis',
        'Tracker':'https://www.graphics.rwth-aachen.de:9000/threevis/threevis/issues'
    }
)
