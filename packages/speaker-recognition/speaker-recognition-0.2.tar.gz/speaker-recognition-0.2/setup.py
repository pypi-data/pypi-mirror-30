from distutils.core import setup

setup(
    name='speaker-recognition',
    version='0.2',
    packages=['speaker_recognition', 'speaker_recognition.feature',
              'speaker_recognition.filters'],
    url='',
    license='MIT',
    author='jarbasAi',
    author_email='',
    install_requires=['xgboost', 'numpy==1.11.2', 'pandoc==1.0.0b2', 'ply==3.9', 'pyssp==0.1.6.5', 'repoze.lru==0.6', 'scikits.talkbox==0.2.5', 'scipy==0.18.1', 'SpeechRecognition==3.5.0'],
    description=''

)
