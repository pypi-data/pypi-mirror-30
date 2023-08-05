"""Driver to train, evaluate and compare to NLTK."""

# [ Imports ]
# [ -Python ]
import time
import random
import logging
import argparse
from itertools import chain
# [ -Projects ]
from sequence_tagging.process_data import read_data
from sequence_tagging.tagger import Tagger, accuracy
from sequence_tagging.tagger import MODEL_LOC, TAGDICT_LOC


def nltk_eval(test_X, test_y):
    import nltk
    tags = []
    for sentence in test_X:
        tags.append(nltk.pos_tag(sentence))
    correct = 0
    total = 0
    sent_correct = 0
    sent_total = 0
    for pred_sent, tags_sent in zip(tags, test_y):
        sentence_correct = True
        for pred, tag in zip(pred_sent, tags_sent):
            if pred[1] == tag:
                correct += 1
            else:
                sentence_correct = False
            total += 1
        if sentence_correct:
            sent_correct += 1
        sent_total += 1
    logging.info(
        " NLTK Tag Accuracy: %d/%d = %.2f",
        correct, total, accuracy(correct, total)
    )
    logging.info(
        " NLTK Sentence Accuracy: %d/%d = %.2f",
        sent_correct, sent_total, accuracy(sent_correct, sent_total)
    )


def main():
    parser = argparse.ArgumentParser("POS Tagger")
    parser.add_argument("type", choices=["train", "eval"])
    parser.add_argument("--iter", "-i", type=int, default=5, dest="iter")
    parser.add_argument("--data", "-d", choices=["pos", "atis"], default="pos", dest="data")
    parser.add_argument("--compare", "-c", action="store_true")
    args = parser.parse_args()

    if args.data == "pos":
        test_file = "data/POS/test.txt"
    else:
        test_file = "data/ATIS/test.txt"
    test_X, test_y = read_data(test_file)
    if args.type == "train":
        if args.data == "pos":
            train_file = "data/POS/train.txt"
        else:
            train_file = "data/ATIS/train.txt"
        train_X, train_y = read_data(train_file)
        tagger = Tagger()
        tagger.train(train_X, train_y, n_iters=args.iter)
        tagger.save("model.p", "tag.p")
    tagger = Tagger.load("model.p", "tag.p")
    t0 = time.time()
    tagger.evaluate(test_X, test_y)
    elapsed_time = time.time() - t0
    logging.info(" Time to run eval: %f", elapsed_time)
    logging.info(" Words per second: %f", len(list(chain(*test_X))) / elapsed_time)
    random_index = random.randint(0, len(test_X))
    print(test_X[random_index])
    print(tagger.tag([test_X[random_index]]))

    if args.data == "pos":
        if args.compare:
            t0 = time.time()
            nltk_eval(test_X, test_y)
            elapsed_time = time.time() - t0
            logging.info(" Time to run eval: %f", elapsed_time)
            logging.info(
                " Words per second: %f",
                len(list(chain(*test_X))) / elapsed_time
            )

if __name__ == "__main__":
    main()
