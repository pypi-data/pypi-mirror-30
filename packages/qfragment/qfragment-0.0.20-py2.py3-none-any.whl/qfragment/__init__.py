from .feedback import *
from .subject_verb_agreement import check_agreement
from nltk.util import ngrams, trigrams
import csv
import json
import numpy as np
import os
import re
import requests
import spacy
import subprocess
import tensorflow as tf
import tflearn

model_name = os.environ.get('QUILL_SPACY_MODEL', 'en_core_web_lg')
if model_name != 'en_core_web_lg':
    nlp = spacy.load(model_name)
else:
    import en_core_web_lg
    nlp = en_core_web_lg.load()

# relative path resolution 
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

LT_SERVER = 'http://localhost:{}/v2/check'.format(os.environ.get('LT_PORT',
        8081))
_PARTICIPLE_TRIGRAM_INDEX = os.path.join(__location__, 'participlevocabindex.csv')
_PARTICIPLE_MODEL = os.path.join(__location__, 'models', 'participle_model.tfl')

class Feedback(object):
    """Result feedback class"""
    def __init__(self):
        self.human_readable = '' # human readable advice
        self.matches = {}        # possible errors

    def to_dict(self):
        return self.__dict__
    
    def __repr__(self):
        return self.human_readable

# Private methods

def _build_trigram_indices(trigram_index):
    """Build a dictionary of trigrams and their indices from a csv"""
    result = {}
    trigram_count = 0
    for key, val in csv.reader(open(trigram_index)):
        result[key] = int(val)
        trigram_count += 1
    return result, trigram_count

def _build_model(trigram_count):
    # This resets all parameters and variables, leave this here
    tf.reset_default_graph()
    
    net = tflearn.input_data([None, trigram_count])
    net = tflearn.fully_connected(net, 200, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 25, activation='ReLU')      # Hidden
    net = tflearn.fully_connected(net, 2, activation='softmax')   # Output
    net = tflearn.regression(net, optimizer='sgd', learning_rate=0.1, loss='categorical_crossentropy')
    model = tflearn.DNN(net)
    return model

def _textStringToPOSArray(text):
    doc = nlp(text)
    tags = []
    for word in doc:
        tags.append(word.tag_)
    return tags

def _find_ngrams(input_list, n):
    """TODO: this method appears unused. Deprecate it?"""
    return zip(*[input_list[i:] for i in range(n)])

def _getPOSTrigramsForTextString(text):
    tags = _textStringToPOSArray(text)
    tgrams = list(trigrams(tags))
    return tgrams

def _trigramsToDictKeys(trigrams):
    keys = []
    for trigram in trigrams:
        keys.append('>'.join(trigram))
    return keys

def _textToTrigrams(text): 
    return _trigramsToDictKeys(_getPOSTrigramsForTextString(text))

def _text_to_vector(text,trigram2idx, trigram_count):
    wordVector = np.zeros(trigram_count)
    for word in _textToTrigrams(text):
        index = trigram2idx.get(word, None)
        if index != None:
            wordVector[index] += 1
    return wordVector

def _begins_with_one_of(sentence, parts_of_speech):
    """Return True if the sentence or fragment begins with one of the parts of
    speech in the list, else False"""
    doc = nlp(sentence)
    if doc[0].tag_ in parts_of_speech:
        return True
    return False 

# Initializations

## Load fragment dectection models
prefixes = ['participle'] # => eventually, [participle, infinitive,
                          #    afterthought, lonelyverb, subordinate,
                          #    appositive]
models = {}
trigram2idx = {}
trigram_count = {}
for prefix in prefixes:
    _trigram_index = os.path.join(__location__,
            '{}vocabindex.csv'.format(prefix))
    trigram2idx[prefix], trigram_count[prefix] = _build_trigram_indices(_trigram_index)
    models[prefix] = _build_model(trigram_count[prefix])
    models[prefix].load(os.path.join(__location__, 'models',
            '{}_model.tfl'.format(prefix)))
    
# Public methods

def get_subject_verb_agreement_feedback(sentence):
    """Return True if no subject verb agreement errors, else False"""
    return check_agreement(sentence)


def get_language_tool_feedback(sentence):
    """Get matches from languagetool"""
    payload = {'language':'en-US', 'text':sentence}
    try:
        r = requests.post(LT_SERVER, data=payload)
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError('''The languagetool server is
        not running.  Try starting it with "ltserver" ''')
    if r.status_code >= 200 and r.status_code < 300:
        return r.json().get('matches', [])
    return [] 


def is_participle_clause_fragment(sentence):
    """Supply a sentence or fragment and recieve a confidence interval"""
    # short circuit if sentence or fragment doesn't start with a participle
    # past participles can sometimes look like adjectives -- ie, Tired
    if not _begins_with_one_of(sentence, ['VBG', 'VBN', 'JJ']):
        return 0.0

    # short circuit if sentence starts with a gerund and the gerund is the
    # subject.
    
    if _begins_with_one_of(sentence, ['VBG']):
        doc = nlp(sentence)
        fw = [w for w in doc][0]
        # Running is fun
        if fw.dep_.endswith('subj'):
            return 0.0

        fc = [c for c in doc.noun_chunks]
        # Dancing boys can never sing
        if str(fw) in str(fc):
            return 0.0

    positive_prob = models['participle'].predict([_text_to_vector(sentence,
        trigram2idx['participle'], trigram_count['participle'])])[0][1]
    return float(positive_prob)


def check(sentence):
    """Supply a sentence or fragment and recieve feedback"""

    # How we decide what to put as the human readable feedback
    #
    # Our order of prefence is,
    #
    # 1. Spelling errors.
    #   - A spelling error can change the sentence meaning
    # 2. Subject-verb agreement errors
    # 3. Subordinate conjunction starting a sentence
    # 4. Participle phrase fragment
    # 5. Other errors

    result = Feedback()
    is_participle = is_participle_clause_fragment(sentence)
    lang_tool_feedback = get_language_tool_feedback(sentence)
    subject_and_verb_agree = get_subject_verb_agreement_feedback(sentence)
    ####
    if is_participle > .5: # Lowest priority
        result.matches['participle_phrase'] = is_participle
        result.human_readable = PARTICIPLE_FRAGMENT_ADVICE.replace('\n', '')
    if lang_tool_feedback:
        result.matches['lang_tool'] = lang_tool_feedback
        for ltf in lang_tool_feedback:
            if ltf['rule']['id'] == 'SENTENCE_FRAGMENT':
                result.human_readable = lang_tool_feedback[0]['message']
    if not subject_and_verb_agree:
        result.matches['subject_verb_agreement'] = subject_and_verb_agree
        result.human_readable = SUBJECT_VERB_AGREEMENT_ADVICE.replace('\n', '') 
    if lang_tool_feedback: # Highest priority
        result.matches['lang_tool'] = lang_tool_feedback
        for ltf in lang_tool_feedback:
            if ltf['rule']['id'] == 'MORFOLOGIK_RULE_EN_US':
                result.human_readable = lang_tool_feedback[0]['message']
         
    ####
        
    if not result.matches:
        result.human_readable = STRONG_SENTENCE_ADVICE.replace('\n', '')

    return result 


