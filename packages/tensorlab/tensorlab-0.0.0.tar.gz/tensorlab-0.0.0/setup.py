from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

name = 'tensorlab'

setup(
    name=name,
    version='0.0.0',
    description='Low-level TensorFlow APIs made easy.',
    long_description=long_description,
    author='Ravindra Marella',
    author_email='mv.ravindra007@gmail.com',
    url='https://marella.github.io/{}/'.format(name),
    license='MIT',
    packages=[name],
    install_requires=['tensorflow'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='{} tensorflow tensor neural networks deep learning machine learning artificial intelligence ml ai'.format(
        name),
)
