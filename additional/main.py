import urllib.request
from urllib.parse import quote, unquote
import re
import pymorphy2
import pymystem3
from flask import Flask
from flask import render_template, request, redirect, url_for

app = Flask(__name__)


def get_page(url):
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req) as response:
        page = response.read().decode("utf-8")
    return page


def get_weather():
    url_skopje = "https://yandex.ru/pogoda/10463?"
    reg_temperature = re.compile("<div class=\"temp fact__temp\"><span class=\"temp__value\">([−+0-9]+)?</span>")
    reg_precip = re.compile(
        "<div class=\"fact__condition day-anchor i-bem\" data-bem='{\"day-anchor\":{\"anchor\":20}}'>(.*)?<\/div><dl")
    page = get_page(url_skopje)
    try:
        temp = re.search(reg_temperature, page).group(1)
    except:
        temp = "Нет данных"
    try:
        precip = re.search(reg_precip, page).group(1)
    except:
        precip = "Нет данных"
    return temp, precip


def get_translit(lemma):
    query = "http://www.dorev.ru/ru-index.html?s={}&q=on".format(quote(lemma), quote(lemma))
    # пытаемся найти в словаре
    reg_old = re.compile("<span class=\"uu\">Предположеніе: <span style=\"color:red;text-decoration:underline\"><b style=\"font-size:16px;color:#336699;line-height:12px;\">(.*)?<\/b><\/span>")
    try:
        page = get_page(query)
        old_ortho = re.search(reg_old, page).group(1)
    except:
        old_ortho = lemma
    return old_ortho


def translit(word):
    m = pymystem3.Mystem()
    word = word.lower()
    # пытаемся найти слово в словаре
    lemma = m.lemmatize(word)[0]
    # запрос
    old_ortho = get_translit(lemma)
    # правила
    vowels = "аеёиоуыэюя"
    for i in range(len(old_ortho) - 1):
        if old_ortho[i] == "и" and old_ortho[i + 1] in vowels:
            old_ortho = old_ortho[:i] + "i" + old_ortho[i + 1:]
    consonants = "бвгджзйклмнпрстфхцчшщ"
    if old_ortho[-1] in consonants:
        old_ortho += "ъ"
    return old_ortho


@app.route('/')
def index():
    sk_temp, sk_precip = get_weather()
    return render_template('index.html', temperature=sk_temp, precip=sk_precip)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/test_result')
def test_result():
    if request.args:
        score = 0
        variants = []
        for i in range(1, 11):
            question = "q" + str(i)
            ans = request.args.get(question)
            if ans == "true":
                score += 1
        point_morph = pymorphy2.MorphAnalyzer().parse("балл")[0]
        points = point_morph.make_agree_with_number(score).word
    return render_template('test_result.html', score=score, points=points)


@app.route('/translit_result')
def translit_result():
    word_old = "Вы не ввели никакого слова"
    if request.args and request.args.get("word_modern") != "":
        word_modern = request.args.get("word_modern")
        word_old = translit(word_modern)
    return render_template('translit_result.html', word_old_ortho=word_old)


if __name__ == '__main__':
    app.run()