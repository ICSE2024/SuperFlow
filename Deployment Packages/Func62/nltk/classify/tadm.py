# Natural Language Toolkit: Interface to TADM Classifier
#
# Copyright (C) 2001-2022 NLTK Project
# Author: Joseph Frazee <jfrazee@mail.utexas.edu>
# URL: <https://www.nltk.org/>
# For license information, see LICENSE.TXT

import subprocess
import sys

from nltk.internals import find_binary

try:
    import numpy
except ImportError:
    pass

_tadm_bin = None


def config_tadm(bin=None):
    global _tadm_bin
    _tadm_bin = find_binary(
        "tadm", bin, env_vars=["TADM"], binary_names=["tadm"], url="http://tadm.sf.net"
    )


def write_tadm_file(train_toks, encoding, stream):
    """
    Generate an input file for ``tadm`` based on the given corpus of
    classified tokens.

    :type train_toks: list(tuple(dict, str))
    :param train_toks: Training data, represented as a list of
        pairs, the first member of which is a feature dictionary,
        and the second of which is a classification label.
    :type encoding: TadmEventMaxentFeatureEncoding
    :param encoding: A feature encoding, used to convert featuresets
        into feature vectors.
    :type stream: stream
    :param stream: The stream to which the ``tadm`` input file should be
        written.
    """
    # See the following for a file format description:
    #
    # https://sf.net/forum/forum.php?thread_id=1391502&forum_id=473054
    # https://sf.net/forum/forum.php?thread_id=1675097&forum_id=473054
    labels = encoding.labels()
    for featureset, label in train_toks:
        length_line = "%d\n" % len(labels)
        stream.write(length_line)
        for known_label in labels:
            v = encoding.encode(featureset, known_label)
            line = "%d %d %s\n" % (
                int(label == known_label),
                len(v),
                " ".join("%d %d" % u for u in v),
            )
            stream.write(line)


def parse_tadm_weights(paramfile):
    """
    Given the stdout output generated by ``tadm`` when training a
    model, return a ``numpy`` array containing the corresponding weight
    vector.
    """
    weights = []
    for line in paramfile:
        weights.append(float(line.strip()))
    return numpy.array(weights, "d")


def call_tadm(args):
    """
    Call the ``tadm`` binary with the given arguments.
    """
    if isinstance(args, str):
        raise TypeError("args should be a list of strings")
    if _tadm_bin is None:
        config_tadm()

    # Call tadm via a subprocess
    cmd = [_tadm_bin] + args
    p = subprocess.Popen(cmd, stdout=sys.stdout)
    (stdout, stderr) = p.communicate()

    # Check the return code.
    if p.returncode != 0:
        print()
        print(stderr)
        raise OSError("tadm command failed!")


def names_demo():
    from nltk.classify.maxent import TadmMaxentClassifier
    from nltk.classify.util import names_demo

    classifier = names_demo(TadmMaxentClassifier.train)


def encoding_demo():
    import sys

    from nltk.classify.maxent import TadmEventMaxentFeatureEncoding

    tokens = [
        ({"f0": 1, "f1": 1, "f3": 1}, "A"),
        ({"f0": 1, "f2": 1, "f4": 1}, "B"),
        ({"f0": 2, "f2": 1, "f3": 1, "f4": 1}, "A"),
    ]
    encoding = TadmEventMaxentFeatureEncoding.train(tokens)
    write_tadm_file(tokens, encoding, sys.stdout)
    print()
    for i in range(encoding.length()):
        print("%s --> %d" % (encoding.describe(i), i))
    print()


if __name__ == "__main__":
    encoding_demo()
    names_demo()
