"""Functions to read in data."""


def read_data(filename):
    data = []
    labels = []
    sentence = []
    sentence_labels = []
    with open(filename) as f:
        for line in f:
            if line == "\n":
                data.append(sentence)
                labels.append(sentence_labels)
                sentence = []
                sentence_labels = []
                continue
            word, pos, _ = line.split()
            sentence.append(word)
            sentence_labels.append(pos)
    return data, labels
