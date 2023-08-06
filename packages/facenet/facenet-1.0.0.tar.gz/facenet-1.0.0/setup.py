from setuptools import setup, find_packages

setup(
    name='facenet',
    version='1.0.0',
    description="Face recognition with Google's FaceNet deep neural network & TensorFlow",
    url='https://github.com/jonaphin/facenet',
    packages= find_packages(),
    include_package_data=True,
    license='MIT',
    author='David Sandberg',
    packageAuthor='Jonathan Lancar',
    install_requires=[
        'tensorflow', 'scipy', 'scikit-learn', 'opencv-python',
        'h5py', 'matplotlib', 'Pillow', 'requests', 'psutil'
    ]
)