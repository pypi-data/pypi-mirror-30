"""Linguistica - Crab Nebula, py 2+3 standalone implementation"""

# Py 2+3 compatibility imports...
from __future__ import division
from io import open

import os
import collections
import time
import re
import textwrap
import itertools
import math


__version__ = "0.07"
__author__ = "Aris Xanthos and John Goldsmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"

# Parameters...
INPUT_FILE = "../LICENSE"
OUTPUT_FILE = "../signatures.txt"
ENCODING = "utf-8"
MIN_STEM_LEN = 3

def main():
    """Main routine"""
    start_time = time.time()

    # Open input file and read content...
    try:
        input_file = open(INPUT_FILE, encoding=ENCODING)
        content = input_file.read()
        input_file.close()
    except IOError:
        print("Couldn't read file ", INPUT_FILE)
        return

    # Split file content into words and count them...
    words = re.findall(r'\w+(?u)', content.lower())
    word_counts = collections.Counter(words)

    # Learn signatures from words.
    signatures, stems, suffixes = find_signatures(word_counts)
    
    # Build a parser and run it...
    parser = build_parser(word_counts, signatures, stems, suffixes)
    for word in word_counts:
        print(word, parser[word])

    # Build sig-tree.
    sig_tree = build_sig_tree(signatures)

    # Compute entropy of final stem letter in signatures...
    final_letter_entropy = get_final_letter_entropy(signatures)

    # Open output file and write signatures to it...
    try:
        output_file = open(OUTPUT_FILE, mode="w", encoding=ENCODING)
        output_file.write(serialize_signatures(signatures))
        output_file.close()
    except IOError:
        print("Couldn't read file ", INPUT_FILE)
        return

    report(start_time, word_counts, signatures)

def find_signatures(word_counts):
    """Find signatures (based on Goldsmith's Lxa-Crab algorithm)"""

    # Find protostems.
    protostems = find_protostems(word_counts)

    # List all possible continuations of each protostem...
    continuations = collections.defaultdict(list)
    for word in word_counts.keys():
        for protostem in protostems:
            if word.startswith(protostem):
                continuations[protostem].append(word[len(protostem):])

    # Find all stems associated with each continuation list...
    protostem_lists = collections.defaultdict(set)
    for protostem, continuation in continuations.items():
        protostem_lists[tuple(sorted(continuation))].add(protostem)

    # Signatures are continuation lists with more than 1 stem...
    signatures = collections.defaultdict(set)
    parasignatures = dict()
    for continuations, protostems in protostem_lists.items():
        container = signatures if len(protostems) > 1 else parasignatures
        container[continuations] = protostems

    # Get list of known suffixes from signatures...
    known_suffixes = set()
    for suffixes in signatures:
        known_suffixes = known_suffixes.union(suffixes)

    # Second generation tentative signatures are parasignatures stripped
    # from unknown suffixes and having at least 2 continuations...
    tentative_signatures = collections.defaultdict(set)
    for continuations, protostems in parasignatures.items():
        good_conts = sorted(c for c in continuations if c in known_suffixes)
        if len(good_conts) > 1:
            tentative_signatures[tuple(good_conts)].add(next(iter(protostems)))

    # Add those tentative signatures which occur with at least 2 stems...
    single_stem_sigs = collections.defaultdict(set)
    for continuations, protostems in tentative_signatures.items():
        container = signatures if len(protostems) > 1 else single_stem_sigs
        container[continuations] = container[continuations].union(protostems)

    # Add each stem in remaining tentative signatures to the existing
    # signature that contains the largest number of its continuations...
    sorted_signatures = sorted(signatures, key=len, reverse=True)
    for continuations, protostems in single_stem_sigs.items():
        continuation_set = set(continuations)
        for suffixes in sorted_signatures:
            if set(suffixes).issubset(continuation_set):
                signatures[suffixes].add(next(iter(protostems)))
                break

    # Get list of known stems from signatures...
    known_stems = set()
    for stems in signatures.values():
        known_stems = known_stems.union(stems)

    return signatures, stems, suffixes

def find_protostems(word_counts):
    """Find potential stems"""
    protostems = set()

    # For each pair of successive words (in alphabetical order)...
    sorted_words = sorted(word_counts.keys())
    for idx in range(len(sorted_words)-1):

        # Add longest common prefix to protostems (if long enough)...
        protostem = os.path.commonprefix(sorted_words[idx:idx+2])
        if len(protostem) >= MIN_STEM_LEN:
            protostems.add(protostem)

    return protostems

def build_parser(word_counts, signatures, stems, suffixes):
    """Build a parser, i.e. a dictionary whose keys are words and whose values
    are themselves dictionaries (whose keys are parses, i.e. (stem, suffix) 
    tuples, and whose values are probabilities).    
    """
    
    # Go through signatures and associate each generated word with its parses...
    sig_num = 1
    parser = collections.defaultdict(dict)
    for suffixes in signatures:
        for pair in itertools.product(signatures[suffixes], suffixes):
            word = "".join(pair)
            parser[word][pair] = sig_num
        sig_num += 1
            
    # Go through each word in the corpus and increment stem and suffix count...
    stem_count = dict()
    suffix_count = dict()
    total_stem_count = total_suffix_count = 0
    for word, count in word_counts.items():
        if len(parser[word]):
            for stem, suffix in parser[word]:
                stem_count[stem] = stem_count.get(stem, 0) + count
                suffix_count[suffix] = suffix_count.get(suffix, 0) + count
                total_stem_count += count
                total_suffix_count += count
        else:
            parser[word][word, ""] = 0
            stem_count[word] = stem_count.get(word, 0) + count
            suffix_count[""] = suffix_count.get("", 0) + count
            total_stem_count += count
            total_suffix_count += count

    # Compute score of each word parse and keep only best parse...
    for word in parser:
        scores = collections.defaultdict(dict)
        total = 0
        for stem, suffix in parser[word]:
            score = (stem_count[stem]/total_stem_count)     \
                  * (suffix_count[suffix]/total_suffix_count)
            scores[word][stem, suffix] = score
        best_parse = sorted(scores[word], key=scores[word].get)[0]
        parser[word] = {best_parse: parser[word][best_parse]}
                        
    return parser            

def build_sig_tree(signatures):
    """AX => JG: would you know how to document this function?"""
    edges = list()

    # Find signatures and stems associated with each word...
    word_to_sigs = collections.defaultdict(list)
    word_to_stems = collections.defaultdict(list)
    for suffixes in signatures:
        for pair in itertools.product(signatures[suffixes], suffixes):
            word = "".join(pair)
            word_to_sigs[word].append(suffixes)
            word_to_stems[word].append(pair[0])

    # Keep only words associated with more than 1 signature.
    word_to_sigs = {w: s for w, s in word_to_sigs.items() if len(s) > 1}

    # AX => JG: would you know how to comment this block?
    sigs_and_morph_to_words = collections.defaultdict(set)
    for word, sigs in word_to_sigs.items():
        sig_pairs = list(itertools.combinations(sigs, 2))
        stem_pairs = list(itertools.combinations(word_to_stems[word], 2))
        for idx, sig_pair in enumerate(sig_pairs):
            stem_pair = stem_pairs[idx]
            morph = suffix_diff(stem_pair[0], stem_pair[1])
            key = (morph, tuple(sorted(sig_pair)))
            sigs_and_morph_to_words[key].add(word)

    return sigs_and_morph_to_words

def get_final_letter_entropy(signatures):
    """Compute entropy over the distribution of final stem letter in sigs"""
    suffix_entropy = dict()
    for suffixes, stems in signatures.items():
        final_letter_freq = collections.Counter(s[-1] for s in stems)
        suffix_entropy[suffixes] = get_entropy(final_letter_freq)
    return suffix_entropy

def suffix_diff(str1, str2):
    """Given 2 strings, one of which is the prefix of the other, returns
    the 'suffix' that must be added to the former to obtain the latter.
    """
    len1 = len(str1)
    len2 = len(str2)
    return str1[len2:] if len(str1) > len(str2) else str2[len1:]

def get_entropy(dictionary):
    """Compute the entropy of a dictionary storing counts"""
    my_sum = 0
    weighted_sum_of_logs = 0
    for freq in dictionary.values():
        if freq:
            my_sum += freq
            weighted_sum_of_logs += freq * math.log(freq)
    return math.log(my_sum) - weighted_sum_of_logs / my_sum

def serialize_signatures(signatures):
    """Pretty-print signatures"""
    signature_num = 1
    output = ""
    for suffixes, stems in signatures.items():
        output += "=" * 80 + "\n"
        output += "Signature #" + str(signature_num) + "\n"
        output += "-" * 80 + "\n"
        output += "\n".join(textwrap.wrap(
            "Stems: " + ", ".join(sorted(stems)), width=80
        )) + "\n"
        output += "\n".join(textwrap.wrap(
            "Suffixes: " + ", ".join(s or "NULL" for s in suffixes), width=80
        )) + "\n"
        output += "=" * 80 + "\n\n"
        signature_num += 1
    return output

def report(start_time, word_counts, signatures):
    """Report execution time and coverage"""

    # Compute and report execution time...
    exec_time = time.time() - start_time
    print(
        "%i word types processed in %.2f secs"
        % (len(word_counts), exec_time)
    )

    # Compute and report coverage...
    covered = collections.Counter()
    for suffixes, stems in signatures.items():
        covered.update(st+su for su, st in itertools.product(suffixes, stems))
    spectrum = collections.Counter(covered.values())
    for frequency in sorted(spectrum):
        print(
            "%i type(s) (%.2f%%) have been assigned to %i signature(s)" % (
                spectrum[frequency],
                100 * spectrum[frequency] / len(word_counts),
                frequency
            )
        )


if __name__ == "__main__":
    main()
