import html
import matplotlib.pyplot as plt
import re
import urllib.request


def get_page(url):
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req) as response:
        page = response.read().decode("utf-8")
        page = html.unescape(page)
    return page


def extract_info(page):
    reg_word = re.compile("<ul><li><b>(.*)?<\/b>(?:.)*\n<\/li><\/ul>\n<dl><dd><i>(.*)?\.<\/i>")
    words = re.findall(reg_word, page)
    alphabet_dict = {}
    pos_dict = {}
    for word, pos in words:
        first_letter = word.lower()[0]
        if first_letter not in alphabet_dict:
            alphabet_dict[first_letter] = 1
        else:
            alphabet_dict[first_letter] += 1
        if pos not in pos_dict:
            pos_dict[pos] = 1
        else:
            pos_dict[pos] += 1
    return alphabet_dict, pos_dict


def plot_feature(feature_dict, title):
    if len(feature_dict) > 30:
        rotation = "vertical"
    else:
        rotation = "horizontal"
    x_names = list(feature_dict.keys())
    x_values = range(len(feature_dict))
    y_values = list(feature_dict.values())
    plt.title(title)
    plt.bar(x_values, y_values)
    plt.xticks(x_values, x_names, rotation=rotation)
    plt.show()


def main():
    url = "http://wiki.dothraki.org/Vocabulary"
    page = get_page(url)
    alphabet, pos = extract_info(page)
    plot_feature(alphabet, "Распределение слов по алфавиту")
    plot_feature(pos, "Распределение слов по частям речи")


if __name__ == "__main__":
    main()