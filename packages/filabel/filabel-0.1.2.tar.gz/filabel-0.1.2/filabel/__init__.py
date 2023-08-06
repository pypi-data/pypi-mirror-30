from filabel.main import get_database, get_list

class FileLabel(object):
    def __init__(self, url=None):
        self.db = get_database(url)
        self.data = get_list(self.db)

    def get_split(self, name):
        return SplitLabel(self.data['splits'][name])

class SplitLabel(object):
    def __init__(self, data):
        self.data = data
        self.labels = self.data['labels']
        self.nlabels = len(self.labels)
        self.id2label = dict(enumerate(self.labels))
        self.label2id = dict([[y, x] for x, y in enumerate(self.labels)])
        self.nsamples = sum([len(samples) for samples in self.data['samples']])
        self.samples = self.data['samples']

    def samplesForLabel(self, name):
        return self.samples[self.label2id[name]]

