from setuptools import setup, find_packages

setup(
    name='facenet',
    version='1.0.1',
    description="Face recognition using TensorFlow",
    long_description="Face recognition with Google's FaceNet deep neural network & TensorFlow",
    url='https://github.com/jonaphin/facenet',
    packages= find_packages(),
    maintainer='Jonathan Lancar',
    maintainer_email='jonaphin@gmail.com',
    include_package_data=True,
    license='MIT',
    install_requires=[
        'tensorflow', 'scipy', 'scikit-learn', 'opencv-python',
        'h5py', 'matplotlib', 'Pillow', 'requests', 'psutil'
    ]
)