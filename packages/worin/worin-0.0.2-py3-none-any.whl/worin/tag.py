from pathlib import Path
import re

from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy


한글초성 = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]
한글중성 = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ",
    "ㅣ"
]
한글종성 = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]
대문자 = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
소문자 = [chr(i) for i in range(ord('a'), ord('z') + 1)]
숫자 = [chr(i) for i in range(ord('0'), ord('9') + 1)]
글자 = list(sorted(set(한글초성) | set(한글중성) | set(한글종성) |
                   set(대문자) | set(소문자) | set(숫자) | set('%')))
글자 += [' ']

letter2id = {c: i for i, c in enumerate(글자)}
id2letter = {i: c for i, c in enumerate(글자)}
NCHAR = len(id2letter)
SPACE = NCHAR - 1
SPAN = 5
WINDOW = 1 + 2 * SPAN

중성수 = len(한글중성)
종성수 = len(한글종성)


def split_hangul(hangul):
    글자코드 = ord(hangul) - ord('가')
    종성위치 = 글자코드 % 종성수
    종성 = 한글종성[종성위치]
    글자코드 //= 종성수
    초성위치 = 글자코드 // 중성수
    초성 = 한글초성[초성위치]
    중성위치 = 글자코드 % 중성수
    중성 = 한글중성[중성위치]
    return 초성, 중성, 종성


def composite_hangul(초성, 중성, 종성):
    first = 한글초성.index(초성)
    middle = 한글중성.index(중성)
    last = 한글종성.index(종성)
    return chr(first * 중성수 * 종성수 + middle * 종성수 + last + ord('가'))


def code_nouns(word, tokens):
    """
    단어에서 명사인 부분만 BIO 코딩

    TODO
    ====

    축약형은 처리 못함. 예시:
    - 게: 것 + 이
    - 내: 나 + 의
    - 건: 것 + ㄴ
    """
    code = [0 for c in word]
    for token, pos in tokens:
        if pos.startswith('N'):
            try:
                idx = word.index(token)
            except ValueError:
                continue

            code[idx] = 2
            for i in range(idx + 1, idx + len(token)):
                code[i] = 1
    return code


def split_word_code(word, codes):
    char_re = re.compile(r'[a-zA-Z0-9]')
    for ch, code in zip(word, codes):
        if '가' <= ch <= '힣':
            for i, x in enumerate(split_hangul(ch)):
                if code == 2:
                    if i == 0:
                        yield x, 2
                    else:
                        yield x, 1
                else:
                    yield x, code
        elif char_re.match(ch):
            yield ch, code
        else:
            yield '%', code


def load_data():
    """data.bin에서 데이터를 불러들인다."""
    all_data = []
    with open('data.bin', 'rb') as f:
        data = f.read()
        N = len(data)
        i = 0
        while i < N:
            n = data[i]  # 길이
            j = i + 2 * n + 1  # 끝 위치
            eojeol = list(data[i + 1:j])  # 한 어절 분량의 데이터 읽음
            chars = eojeol[::2]  # 글자 낱자들
            code = eojeol[1::2]  # 코드(2: 명사 begin, 1: 명사 inside, 0: outside)
            all_data.append((chars, code))
            i = j
    return all_data


def split_word(word):
    char_re = re.compile(r'[a-zA-Z0-9]')
    for ch in word:
        if '가' <= ch <= '힣':
            yield from split_hangul(ch)
        elif char_re.match(ch):
            yield ch
        elif ch == ' ':
            yield ' '
        else:
            yield '%'


class FeedForward():
    def __init__(self):
        self.model = Sequential([
            Dense(256, input_shape=(WINDOW * NCHAR,)),
            Activation('relu'),
            Dense(3),
            Activation('softmax'),
        ])
        model_path = Path(__file__).parent / 'ff.h5'
        self.model.load_weights(model_path)

    def nouns(self, example):
        chars = list(split_word(example))
        padded = [SPACE] * SPAN + [letter2id[x] for x in chars] +  [SPACE] * SPAN

        N = len(padded) - SPAN
        X_new = numpy.zeros((N, NCHAR * WINDOW))
        for i in range(0, N):
            char_que = padded[i:i+WINDOW]

            for k, char in enumerate(char_que):
                j = k * NCHAR + char
                X_new[i, j] = 1

        code = self.model.predict_classes(X_new)
        i = 0
        noun_list = []
        begin_noun = False
        while i < len(chars):
            ch = chars[i]
            noun_char = None

            if 'ㄱ' <= ch <= 'ㅎ':
                #if code[i] > 0 and code[i + 1] > 0 and code[i + 2] > 0:
                if int(code[i] > 0) + int(code[i + 1] > 0) + int(code[i + 2] > 0) > 1:
                    noun_char = composite_hangul(*chars[i:i+3])
                i += 3
            else:
                if ch != ' ' and code[i] > 0:
                    noun_char = ch
                i += 1

            if begin_noun:
                if noun_char:
                    noun_list[-1] += noun_char
                else:
                    begin_noun = False
            elif noun_char:
                begin_noun = True
                noun_list.append(noun_char)

        return noun_list
