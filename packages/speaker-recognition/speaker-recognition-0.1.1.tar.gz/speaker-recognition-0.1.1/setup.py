from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='speaker-recognition',
    version='0.1.1',
    packages=['speaker_recognition', 'speaker_recognition.feature',
              'speaker_recognition.filters'],
    url='',
    license='MIT',
    author='jarbasAi',
    author_email='',
    install_requires=required,
    description=''

)
