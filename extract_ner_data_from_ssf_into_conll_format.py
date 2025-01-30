"""Convert ssf ner data into CoNLL format."""
from argparse import ArgumentParser
from re import S
from re import search
from re import findall
import os
from glob import glob


def find_sentences_from_ssf_text(text):
    """Find sentences from the ssf text."""
    return findall('(<Sentence id=.*?>)(.*?)(</Sentence>)', text, S)


def read_text_from_file(file_path):
    """Read text from a file."""
    with open(file_path, 'r', encoding='utf-8') as file_read:
        return file_read.read().strip()


def create_feature_dictionary_from_morph(morph_features):
    """Create feature dictionary from morph for a token."""
    feature_dict = {}
    for morph_feature in morph_features:
        key, val = morph_feature.split('=')
        if val[0] == "'" and val[-1] == "'":
            val = val[1: -1]
        feature_dict[key] = val
    return feature_dict


def extract_ner_data_in_ssf_form(ssf_sentences):
    """Extract NE information from chunk data and keep them in CONLL form."""
    ner_annotations = []
    for header, sent_text, footer in ssf_sentences:
        lines = sent_text.split('\n')
        sent_ner_annotation = []
        ne_tag = ''
        for line in lines:
            line = line.strip()
            print(line)
            if line:
                line_split = line.split('\t')
                if len(line_split) > 1:
                    addr = line_split[0]
                    token = line_split[1]
                if line == '))':
                    ne_type = ''
                    ne_tag = ''
                    ner_tag = ''
                elif not line.find('0\t((\tSSF'):
                    continue
                elif len(line_split) == 3 and search('^\d+$', addr):
                    ner_tag = 'O'
                    token_ner_annotation = '\t'.join([token, ner_tag])
                    sent_ner_annotation.append(token_ner_annotation)
                elif len(line_split) == 3 and search('^\d+\.\d+$', addr):
                    ner_tag = ne_type + '-' + ne_tag
                    if ne_type == 'B':
                        ne_type = 'I'
                    token_ner_annotation = '\t'.join([token, ner_tag])
                    sent_ner_annotation.append(token_ner_annotation)
                elif len(line_split) == 2 and search('^\d+\.\d+$', addr):
                    ner_tag = ne_type + '-' + ne_tag
                    if ne_type == 'B':
                        ne_type = 'I'
                    token_ner_annotation = '\t'.join([token, ner_tag])
                    sent_ner_annotation.append(token_ner_annotation)
                elif len(line_split) == 2 and search('^\d+$', addr):
                    ner_tag = 'O'
                    token_ner_annotation = '\t'.join([token, ner_tag])
                    sent_ner_annotation.append(token_ner_annotation)
                elif len(line_split) == 4:
                    morph = line_split[3]
                    print(morph)
                    if morph.startswith('<fs'):
                        morph_text = morph[4: -1]
                    else:
                        morph_text = morph[1: -1]
                    morph_features = morph_text.split()
                    print(morph_features)
                    feature_dict = create_feature_dictionary_from_morph(morph_features)
                    if 'ne' in feature_dict:
                        ne_tag = feature_dict['ne']
                        ne_type = 'B'
        if sent_ner_annotation:
            ner_annotations.append('\n'.join(sent_ner_annotation) + '\n')
    return ner_annotations


def write_lines_to_file(lines, file_path):
    """Write lines to a file."""
    with open(file_path, 'w', encoding='utf-8') as file_write:
        file_write.write('\n'.join(lines) + '\n')


def main():
    """Pass arguments and call functions here."""
    parser = ArgumentParser()
    parser.add_argument('--input', dest='inp', help='Enter the input file path')
    parser.add_argument('--output', dest='out', help='Enter the output file path')
    args = parser.parse_args()
    if not os.path.isdir(args.inp):
        input_text = read_text_from_file(args.inp)
        ssf_sentences = find_sentences_from_ssf_text(input_text)
        ner_annotations = extract_ner_data_in_ssf_form(ssf_sentences)
        write_lines_to_file(ner_annotations, args.out)
    else:
        ner_annotations_all = []
        for file_path in glob(args.inp + '/*'):
            input_text = read_text_from_file(file_path)
            ssf_sentences = find_sentences_from_ssf_text(input_text)
            ner_annotations = extract_ner_data_in_ssf_form(ssf_sentences)
            ner_annotations_all.append('\n'.join(ner_annotations) + '\n')
        write_lines_to_file(ner_annotations_all, args.out)


if __name__ == '__main__':
    main()
