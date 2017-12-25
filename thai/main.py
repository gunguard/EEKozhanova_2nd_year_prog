import re
import os
import html
import json
from flask import Flask
from flask import render_template, request


app = Flask(__name__)


def clean_line(line):
    rubbish_reg = re.compile("<.*?>")
    additional_reg = re.compile("\[.*?\]")
    line = rubbish_reg.sub("", line)
    line = additional_reg.sub("", line)
    line = line.strip(" ")
    return line


"""5 баллов. Скачать отсюда https://yadi.sk/d/e6eos6Czyd4Av архив страниц
интернет-сайта с тайско-английским словарём. Извлечь с каждой страницы
пары "тайское слово — английское слово" и поместить их в питоновскую
структуру данных типа "словарь", где ключом будет тайское слово,
а значением — английское."""
def make_dict():
    thai_dict = {}
    thai_reg = re.compile("<tr><td class=th><a (?:.*?)>(.*?)</a></td><td>(?:.*?)</td><td class=pos>(?:.+?)</td><td>(.*?)</td></tr>")
    for page in os.listdir("./thai_pages"):
        if page.endswith(".html"):
            with open("thai_pages" + os.sep + page, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = html.unescape(line)
                    res = re.findall(thai_reg, line)
                    if res:
                        for each in res:
                            thai = clean_line(each[0])
                            eng = clean_line(each[1])
                            if thai and eng and eng != "" and not eng.endswith("\""):
                                thai_dict[thai] = eng
            print("Обработана такая страница: " + page)
    return thai_dict


"""8 баллов. Использовать структуру данных из предыдущего задания, записать
её в файл формата json на диск, а также создать ещё одну структуру данных,
где будет наоборот: английское слово ключ, а значение — массив тайских.
Её тоже записать на диск в формате json."""
def dict_to_json(python_dict):
    thai_to_eng = json.dumps(python_dict)
    with open("thai_to_english.json", "w", encoding="utf-8") as out:
        out.write(thai_to_eng)
    inverted_dict = {eng:thai for thai, eng in python_dict.items()}
    eng_to_thai = json.dumps(inverted_dict)
    with open("english_to_thai.json", "w", encoding="utf-8") as out:
        out.write(eng_to_thai)


"""10 баллов. Создать на фласке веб-приложение "Англо-тайский словарь", где
можно было бы в текстовом поле ввести английское слово и получить в
качестве результата запроса — его перевод на тайский."""
@app.route("/")
def search():
    return render_template("index.html")


@app.route("/results")
def results():
    if request.args:
        res = []
        with open("english_to_thai.json", "r", encoding="utf-8") as f:
            dictionary = json.loads(f.read())
            search_word = request.args.get("english_word")
            if search_word in dictionary:
                res.append([search_word, dictionary[search_word]])
        return render_template("results.html", query=search_word, results=res)
                    
        

def main():
    dictionary = make_dict()
    dict_to_json(dictionary)
    app.run(debug=True)


if __name__ == "__main__":
    main()
