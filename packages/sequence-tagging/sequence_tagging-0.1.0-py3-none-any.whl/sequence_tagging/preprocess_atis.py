"""Script to transform the ATIS data to a format similar to the pos tags"""

# [ Imports ]
# [ -Python ]
from itertools import chain


def preprocess_file(filename):
    data = []
    labels = []
    slots = []
    with open(filename) as f:
        for line in f:
            parts = line.split()
            start = parts.index("BOS")
            end = parts.index("EOS")
            utterance = parts[start + 1:end]
            intent = parts[-1]
            slot = parts[end + 2:-1]
            if "#" in intent:
                continue
            data.append(utterance)
            labels.append(intent)
            slots.append(slot)
    return data, labels, slots


def write_to_file(filename, dataset):
    with open(filename, 'w') as f:
        for sample in dataset:
            labels = [sample[1]] * len(sample[0])
            for word, slot, label in zip(sample[0], sample[2], labels):
                f.write("{} {} {}\n".format(word, slot, label))
            f.write("\n")

train_data, train_labels, train_slots = preprocess_file("atis.train.w-intent.iob")
train_data2, train_labels2, train_slots2 = preprocess_file("atis-2.train.w-intent.iob")
train_data.extend(train_data2)
train_labels.extend(train_labels2)
train_slots.extend(train_slots2)

dev_data, dev_labels, dev_slots = preprocess_file("atis-2.dev.w-intent.iob")
test_data, test_labels, test_slots = preprocess_file("atis.test.w-intent.iob")

all_labels = set(train_labels) & set(dev_labels) & set(test_labels)
all_slots = set(chain(*train_slots)) & set(chain(*dev_slots)) & set(chain(*test_slots))

train = [[data, label, slots] for data, label, slots in zip(train_data, train_labels, train_slots) if label in all_labels and all(slot in all_slots for slot in slots)]
dev = [[data, label, slots] for data, label, slots in zip(dev_data, dev_labels, dev_slots) if label in all_labels and all(slot in all_slots for slot in slots)]
test = [[data, label, slots] for data, label, slots in zip(test_data, test_labels, test_slots) if label in all_labels and all(slot in all_slots for slot in slots)]

write_to_file("train.txt", train)
write_to_file("dev.txt", dev)
write_to_file("test.txt", test)
