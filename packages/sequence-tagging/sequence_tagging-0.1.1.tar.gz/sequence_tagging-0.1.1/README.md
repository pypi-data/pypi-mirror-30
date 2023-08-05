# Part of Speech Tagging
##

A Part of Speech tagger using the Average Perceptron.

Trained on CoNLL 2000 Chunking data.

This uses the following features:

 * The Suffix (last 3 characters) of the current word (unnormalized).
 * The Prefix (first character) of the current word (unnormalized).
 * The current word.
 * The previous Part of Speech tag and the current word.
 * The Previous Part of Speech tag.
 * The Part of Speech tag from the word before last.
 * Both of the previous Part of Speech tags.
 * The previous word.
 * The previous word suffix.
 * The word from 2 steps back.
 * The next word.
 * The next word suffix.
 * The word after next.
 * A Bias
