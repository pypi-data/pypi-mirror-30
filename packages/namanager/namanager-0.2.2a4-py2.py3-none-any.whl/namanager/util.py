import re


def gen_unique_str(string):
    u = '_'
    while u in string:
        u += '_'
    return u


def get_first_word(s):
    try:
        beg = s.find(re.search('[A-Za-z]', s).group(0)) if len(s) else -1
    except Exception:
        beg = -1
    end = beg + 1 if len(s) else 0
    while end < len(s):
        # e.g., HTTPResponse
        if (s[end - 1].isupper() and
            s[end].isupper() and
           (end + 1 != len(s) and s[end + 1].islower())):
            break
        # e.g., HttpResponse or Http_response
        if s[end - 1].islower() and not s[end].islower():
            break
        # e.g., HTTP* or HTTP_
        if not s[end].isalpha():
            break

        end += 1

    return (s[beg:end], beg, end)


def get_words(string, include_non_letter=True):
    words = []
    while string != '':
        if include_non_letter and not string[0].isalpha():
            first_letter = re.search('[a-zA-Z]', string)
            if first_letter:
                i = string.find(first_letter.group(0))
                words.append(string[:i])
                string = string[i:]
            else:
                words.append(string)
                string = ''
        else:
            tpl = get_first_word(string)
            if tpl[0]:
                string = string[tpl[2]:]
                words.append(tpl[0])
            else:
                string = ''

    return [w for w in words if w != '']


def convert_sep(string, cases):
    for case in cases:
        if case == 'dash_to_underscore':
            string = string.replace('-', '_')
        if case == 'underscore_to_dash':
            string = string.replace('_', '-')
    return string


def convert_word_to_case(word, case):
    """
    Only support pascal case,
    because camel case is sensible for multiple words,
    user can just change first letter to lowercase.
    """

    if case == 'upper_case':
        word = word.upper()
    if case == 'lower_case':
        word = word.lower()
    if case == 'pascal_case':
        word = word[0].upper() + word[1:].lower()

    return word


def convert_sentence_to_case(sentence, case):
    return ''.join(convert_words_to_case(get_words(sentence), case))


def convert_words_to_case(words, case):
    """
    This function assuming that
    all words are well separated and
    not included empty string:
        Ok:
            ['_*&', 'Http', 'protocol', '#$%']
        Wrong:
            ['_*&h', 'ttp', 'protocol', '#$%']
    """

    converted_words = []

    if case == 'camel_case':
        first_word_occured = False
        for w in words:
            word = convert_word_to_case(w, 'pascal_case')
            if not first_word_occured and word[0].isalpha():
                word = word[0].lower() + word[1:]
                first_word_occured = True
            converted_words.append(word)

    elif case in ['upper_case', 'lower_case', 'pascal_case']:
        for w in words:
            converted_words.append(convert_word_to_case(w, case))

    return converted_words
