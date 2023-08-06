from os.path import dirname, exists


class SpeakerRecognizer(object):
    def __init__(self, model=dirname(__file__) + "/model"):
        from speaker_recognition.interface import ModelInterface
        from speaker_recognition.utils import read_wav, read_stream
        self.read_wav = read_wav
        self.read_stream = read_stream
        self.model = ModelInterface()
        self.model_path = model
        self.load_model()

    def load_model(self):
        if exists(self.model_path):
            self.model = self.model.load(self.model_path)

    def train_single_file(self, user="unknown", wav_file=None):
        if user == "unknown" or wav_file is None:
            return {"success": False, "error": "invalid args"}
        try:
            wav_file = wav_file
            fs, signal = self.read_wav(wav_file)
            self.model.enroll(user, fs, signal)
            self.model.train()
            self.model.dump(self.model_path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def batch_train_file(self, user="unknown", wav_files=None):
        wav_files = wav_files or []
        if user == "unknown" or not len(wav_files):
            return {"success": False, "error": "invalid args"}
        for wav_file in wav_files:
            try:
                wav_file = wav_file
                fs, signal = self.read_wav(wav_file)
                self.model.enroll(user, fs, signal)
                self.model.train()
                print "trained", user, wav_file
            except Exception as e:
                print e, user, wav_file
        self.model.dump(self.model_path)

    def normalize_score(self, score):
        score = score + 1
        if score > 1:
            score = 1
        if score < 0:
            score = 0
        return score

    def recognize_data(self, audio_data, thresh=0.75, fs=48000):
        fs, signal = self.read_stream(audio_data, fs)
        label, score = self.model.predict(fs, signal)
        score = self.normalize_score(score)
        if thresh and score < thresh:
            label = "unknown"
        return label, score

    def recognize(self, wav_file, thresh=0.75):
        # compatibility only, use recognize_wav and recognize_data instead
        return self.recognize_wav(wav_file, thresh)

    def recognize_wav(self, wav_file, thresh=0.75):
        fs, signal = self.read_wav(wav_file)
        label, score = self.model.predict(fs, signal)
        score = self.normalize_score(score)
        if thresh and score < thresh:
            label = "unknown"
        return label, score

