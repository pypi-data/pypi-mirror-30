#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# File: interface.py
# Date: Thu Sep 14 14:56:58 2017 -0700
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import cPickle as pickle
import time
import traceback as tb
from collections import defaultdict

import numpy as np
from speaker_recognition.filters.VAD import \
    VAD
from scipy.io import wavfile

from speaker_recognition.feature import \
    mix_feature
from skgmm import GMMSet

CHECK_ACTIVE_INTERVAL = 1  # seconds


class ModelInterface(object):
    UBM_MODEL_FILE = None

    def __init__(self):
        self.features = defaultdict(list)
        self.gmmset = GMMSet()
        self.vad = VAD()

    def init_noise(self, fs, signal):
        """
        init vad from environment noise
        """
        self.vad.init_noise(fs, signal)

    def filter(self, fs, signal):
        """
        use VAD (voice activity detection) to filter out silence part of a signal
        """
        ret, intervals = self.vad.filter(fs, signal)
        orig_len = len(signal)

        if len(ret) > orig_len / 3:
            # signal is filtered by VAD
            return ret
        return np.array([])

    def enroll(self, name, fs, signal):
        """
        add the signal to this person's training dataset
        name: person's name
        """
        feat = mix_feature((fs, signal))
        self.features[name].extend(feat)

    def _get_gmm_set(self):
        return GMMSet()

    def train(self):
        self.gmmset = self._get_gmm_set()
        start = time.time()
        print "Start training..."
        for name, feats in self.features.iteritems():
            self.gmmset.fit_new(feats, name)
        print time.time() - start, " seconds"

    def predict(self, fs, signal):
        """
        return a label (name)
        """
        try:
            feat = mix_feature((fs, signal))
        except Exception as e:
            print tb.format_exc()
            return None
        return self.gmmset.predict(feat)

    def predict_scores(self, fs, signal):
        """
        return scores
        """
        try:
            feat = mix_feature((fs, signal))
        except Exception as e:
            print tb.format_exc()
            return None
        return self.gmmset.predict_scores(feat)

    def dump(self, fname):
        """ dump all models to file"""
        self.gmmset.before_pickle()
        with open(fname, 'w') as f:
            pickle.dump(self, f, -1)
        self.gmmset.after_pickle()

    @staticmethod
    def load(fname):
        """ load from a dumped model file"""
        with open(fname, 'r') as f:
            R = pickle.load(f)
            R.gmmset.after_pickle()
            return R


if __name__ == "__main__":
    """ some testing"""
    m = ModelInterface()
    fs, signal = wavfile.read(
        "../corpus.silence-removed/Style_Reading/f_001_03.wav")
    m.enroll('h', fs, signal[:80000])
    fs, signal = wavfile.read(
        "../corpus.silence-removed/Style_Reading/f_003_03.wav")
    m.enroll('a', fs, signal[:80000])
    m.train()
    print m.predict(fs, signal[:80000])
