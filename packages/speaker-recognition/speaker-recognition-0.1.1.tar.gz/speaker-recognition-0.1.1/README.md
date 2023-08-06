## About

This is a [Speaker Recognition](https://en.wikipedia.org/wiki/Speaker_recognition)

For more details of this project, please see:

+ Our [presentation slides](https://github.com/ppwwyyxx/speaker-recognition/raw/master/doc/Presentation.pdf)
+ Our [complete report](https://github.com/ppwwyyxx/speaker-recognition/raw/master/doc/Final-Report-Complete.pdf)

## Dependencies

+ [scikit-learn](http://scikit-learn.org/)
+ [scikits.talkbox](http://scikits.appspot.com/talkbox)
+ [pyssp](https://pypi.python.org/pypi/pyssp)
+ [PyQt4](http://sourceforge.net/projects/pyqt/)
+ [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/)
+ (Optional)[bob](http://idiap.github.io/bob/).

## Installation / Compilation

### (Optional) Bob:

Install `blitz` as Bob dependency.
See [here](https://github.com/idiap/bob/wiki/Packages) for more instructions on bob core library installation.

Bob python bindings are available on [PyPI](https://pypi.python.org/pypi).
You may need to install bob packages in the following order:
+ bob.extension
+ bob.blitz (require blitz++)
+ bob.core
+ bob.sp
+ bob.ap

Note: We also have a MFCC implementation on our own
which will be used as a fallback when bob is unavailable.
But it's not so efficient as the C implementation in bob.


## Algorithms Used

_Voice Activity Detection_(VAD):
+ [Long-Term Spectral Divergence](http://www.sciencedirect.com/science/article/pii/S0167639303001201) (LTSD)

_Feature_:
+ [Mel-Frequency Cepstral Coefficient](http://en.wikipedia.org/wiki/Mel-frequency_cepstrum) (MFCC)
+ [Linear Predictive Coding](http://en.wikipedia.org/wiki/Linear_predictive_coding) (LPC)

_Model_:
+ [Gaussian Mixture Model](http://en.wikipedia.org/wiki/Mixture_model#Gaussian_mixture_model) (GMM)
+ [Universal Background Model](http://www.sciencedirect.com/science/article/pii/S1051200499903615) (UBM)
+ Continuous [Restricted Boltzman Machine](https://en.wikipedia.org/wiki/Restricted_Boltzmann_machine) (CRBM)
+ [Joint Factor Analysis](http://speech.fit.vutbr.cz/software/joint-factor-analysis-matlab-demo) (JFA)

# usage

    from speaker_recognition import SpeakerRecognizer
    from os.path import join, dirname
    from os import listdir

    test_dir = join(dirname(__file__), "test_users")
    train_dir = join(dirname(__file__), "users")
    sr = SpeakerRecognizer()
    sr.train_single_file()

    train_set = listdir(train_dir)
    # train speakers
    for speaker in train_set:
        wavs = listdir(join(train_dir, speaker))
        for wav in wavs:
            wav = join(train_dir, speaker, wav)
            result = sr.train_single_file(speaker, wav)
            if result.get("success", False):
                print "trained", wav
            else:
                print "train failed", wav

    test_set = listdir(test_dir)
    # test speakers
    for speaker in test_set:
        wavs = listdir(join(test_dir, speaker))
        for wav in wavs:
            wav = join(test_dir, speaker, wav)
            result = sr.recognize(wav)
            print speaker,  result