from ckiptagger import WS, POS, NER

def wordSegment(TEXT):

    # load models
    ws = WS("./data/Ckipdata")
    pos = POS("./data/Ckipdata")
    ner = NER("./data/Ckipdata")

    word_sentence_list = ws(
    TEXT,
    # sentence_segmentation=True, # To consider delimiters
    # segment_delimiter_set = {",", "��", ":", "?", "!", ";"}, # This is the defualt set of delimiters
    # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
    # coerce_dictionary = dictionary2, # words in this dictionary are forced
    )
    pos_sentence_list = pos(word_sentence_list)
    entity_sentence_list = ner(word_sentence_list, pos_sentence_list)

    # release memory
    del ws
    del pos
    del ner

    return word_sentence_list, pos_sentence_list, entity_sentence_list

# get sutiable list of word segmentation for Rake
def getWSList(TEXT):

    word_sentence_list, pos_sentence_list, entity_sentence_list = wordSegment(TEXT)
    combinedList = []
    for i, paragraph in enumerate(word_sentence_list):
        tempList = zip(word_sentence_list[i], pos_sentence_list[i])
        for eachTuple in tempList:
            combinedList.append(eachTuple)
        for entity in sorted(entity_sentence_list[i]):
            combinedList.append((entity[3], entity[2]))

    return combinedList


def print_word_pos_sentence(word_sentence, pos_sentence):
    assert len(word_sentence) == len(pos_sentence)
    for word, pos in zip(word_sentence, pos_sentence):
        print(f"{word}({pos})", end="\u3000")
    print()
    return

# show the results of word segmentation
def showResults(TEXT, word_sentence_list, pos_sentence_list, entity_sentence_list):
    for i, sentence in enumerate(TEXT):
        print()
        print(f"'{sentence}'")
        print_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i])
        for entity in sorted(entity_sentence_list[i]):
            print(entity)
