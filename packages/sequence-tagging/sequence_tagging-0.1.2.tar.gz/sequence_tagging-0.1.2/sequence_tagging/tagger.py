"""Part of Speech Tagger that uses the Averaged Perceptron."""

# [ Imports ]
# [ -Python ]
import pickle
import random
import logging
from pathlib import Path
from itertools import chain
from collections import defaultdict
# [ -Project ]
from sequence_tagging.perceptron import AveragedPerceptron

logging.getLogger().setLevel(logging.INFO)
random.seed(1337)
MODEL_LOC = Path(__file__).parent / "data" / "model.p"
TAGDICT_LOC = Path(__file__).parent / "data" / "tagdict.p"


class Tagger(object):
    START = ['<START>', '<START2>']
    END = ['<END>', '<END2>']

    def __init__(self, freq_thresh=25, ambiguity_thresh=0.98):
        self.model = AveragedPerceptron()
        self.tagdict = {}
        self.classes = set()
        self.freq_thresh = freq_thresh
        self.ambiguity_thresh = ambiguity_thresh

    @classmethod
    def load(cls, model_loc=MODEL_LOC, tag_loc=TAGDICT_LOC):
        tagger = cls()
        tagger.model = AveragedPerceptron.load(model_loc)
        tagger.classes = tagger.model.classes
        tagger.tagdict = pickle.load(open(tag_loc, "rb"))
        return tagger

    def save(self, model_loc=MODEL_LOC, tag_loc=TAGDICT_LOC):
        self.model.save(model_loc)
        pickle.dump(self.tagdict, open(tag_loc, "wb"))

    def tag(self, corpus):
        tokens = []
        for sentence in corpus:
            prev, prev2 = self.START
            sentence_tokens = []
            context = (
                self.START +
                [_normalize(w) for w in sentence] +
                self.END
            )
            for i, word in enumerate(sentence):
                tag = self.tagdict.get(word)
                if not tag:
                    features = self._get_features(
                        i,
                        word,
                        context,
                        prev, prev2
                    )
                    tag = self.model.predict(features)
                sentence_tokens.append((word, tag))
                prev2 = prev
                prev = tag
            tokens.append(sentence_tokens)
        return tokens

    def evaluate(self, sentences, tags):
        tagged = self.tag(sentences)
        correct = 0
        total = 0
        sent_correct = 0
        sent_total = len(sentences)
        for pred_sent, tag_sent in zip(tagged, tags):
            sentence_correct = True
            for pred, tag in zip(pred_sent, tag_sent):
                if pred[1] == tag:
                    correct += 1
                else:
                    sentence_correct = False
            total += len(pred_sent)
            if sentence_correct:
                sent_correct += 1
        tag_acc = accuracy(correct, total)
        sent_acc = accuracy(sent_correct, sent_total)
        logging.info(
            " Per Tag Accuracy: %d/%d = %.2f",
            correct, total, tag_acc
        )
        logging.info(
            " Per Sentence Accuracy: %d/%d = %.2f",
            sent_correct, sent_total, sent_acc
        )
        return tag_acc, sent_acc

    def train(self, sentences, labels, n_iters=5):
        self._make_tagdict(sentences, labels)
        self.model.classes = self.classes
        for it in range(n_iters):
            correct = 0
            total = 0
            sentences, labels = shuffle(sentences, labels)
            for sentence, sentence_labels in zip(sentences, labels):
                prev, prev2 = self.START
                context = (
                    self.START +
                    [_normalize(w) for w in sentence] +
                    self.END
                )
                for i, (word, tag) in enumerate(zip(sentence, sentence_labels)):
                    guess = self.tagdict.get(word)
                    if not guess:
                        features = self._get_features(i, word, context, prev, prev2)
                        guess = self.model.predict(features)
                        self.model.update(tag, guess, features)
                    # Use predicted tags to generate next example rather than teacher forcing
                    prev2 = prev
                    prev = guess
                    correct += guess == tag
                    total += 1
            logging.info(
                " Iter %d: %d/%d = %.2f",
                it + 1, correct, total, accuracy(correct, total)
            )
        self.model.average_weights()

    def _get_features(self, i, word, context, prev, prev2):
        # move i so it indexes into context rather than sentence
        i += len(self.START)
        features = defaultdict(int)

        def add(name, *args):
            features[' '.join((name,) + tuple(args))] += 1

        add('bias')
        add('i suffix', word[-3:])
        add('i prefix', word[0])
        add('i-1 tag', prev)
        add('i-2 tag', prev2)
        add('i-1 tag + 1-2 tag', prev, prev2)
        add('i word', context[i])
        add('i - 1 tag + i word', prev, context[i])
        add('i - 1 word', context[i - 1])
        add('i - 1 suffix', context[i - 1][-3:])
        add('i - 2 word', context[i - 2])
        add('i + 1 word', context[i + 1])
        add('i + 1 suffix', context[i + 1][-3:])
        add('i + 2 word', context[i + 2])

        return features

    def _make_tagdict(self, sentences, tags):
        # counts for frequency of each class for a given word.
        # counts[word][class] = freq
        counts = defaultdict(lambda: defaultdict(int))
        for word, tag in zip(chain(*sentences), chain(*tags)):
            counts[word][tag] += 1
            self.classes.add(tag)

        for word, tag_freq in counts.items():
            tag, mode = max(tag_freq.items(), key=lambda item: item[1])
            total = sum(tag_freq.values())
            # Don't use this lookup for rare words
            # Don't use thus lookup for words that have many classes
            if total >= self.freq_thresh and mode / total >= self.ambiguity_thresh:
                self.tagdict[word] = tag


def _normalize(word):
    if '-' in word:
        return "!HYPHEN"
    elif word.isdigit() and len(word) == 4:
        return '!YEAR'
    elif word[0].isdigit():
        return '!DIGITS'
    return word.lower()


def accuracy(n, d):
    return (n / d) * 100


def shuffle(x, y):
    together = list(zip(x, y))
    random.shuffle(together)
    x, y = zip(*together)
    return x, y
