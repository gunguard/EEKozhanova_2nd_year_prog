import sqlite3
import matplotlib.pyplot as plt


def open_glosses(path):
    glosses = {}
    gloss_id = 0
    with open(path, "r", encoding="utf-8") as f_glosses:
        for line in f_glosses.readlines():
            parts = line.strip().split(" — ")
            glosses[parts[0]] = (gloss_id, parts[1])
            gloss_id += 1
    return glosses


def work_with_hittite(path, glosses):
    words = {}
    wordform_id = 0
    gloss_id = len(glosses)

    conn = sqlite3.connect(path)
    c = conn.cursor()
    a = c.execute("SELECT * FROM wordforms")

    for item in a:
        lemma, wordform, glosses_str = item[0], item[1], item[2]
        words[wordform] = (wordform_id, lemma, glosses_str)
        wordform_id += 1

        # в словарь с глоссами записываются те глоссы, которых нет в txt, но есть в разметке
        # глоссами считается всё, что записано большими буквами
        for gloss in glosses_str.split("."):
            if gloss not in glosses and gloss.upper() == gloss and gloss != "":
                glosses[gloss] = (gloss_id, gloss)
                gloss_id += 1
    conn.close()
    return words, glosses


def create_new_database(new_path, words, glosses):
    conn = sqlite3.connect(new_path)
    c = conn.cursor()
    c.execute("CREATE TABLE words(word_id integer, Lemma text, Wordform text, Glosses text)")
    for word in words:
        word_id, lemma, glosses_str = words[word]
        c.execute("INSERT INTO words VALUES ({}, '{}', '{}', '{}')".format(word_id, lemma, word, glosses_str))
    c.execute("CREATE TABLE glosses(gloss_id integer, Gloss text, Transcription text)")
    for gloss in glosses:
        gloss_id, transcript = glosses[gloss]
        c.execute("INSERT INTO glosses VALUES ({}, '{}', '{}')".format(gloss_id, gloss, transcript))
    c.execute("CREATE TABLE words_to_glosses(word_id integer, gloss_id text)")
    for word in words:
        word_id = words[word][0]
        glosses_list = words[word][2].split(".")
        gloss_ids = []
        for gloss in glosses_list:
            try:
                # если глосса есть в списке, запишем её id
                gloss_id = glosses[gloss][0]
                gloss_ids.append(str(gloss_id))
            except:
                # если глоссы в списке нет — это корень, запишем его значение
                gloss_ids.append(gloss)
        glosses_ids_line = ",".join(gloss_ids)
        c.execute("INSERT INTO words_to_glosses VALUES ({}, '{}')".format(word_id, glosses_ids_line))
    conn.commit()
    conn.close()


def count_stats(words):
    cases_dict = {"NOM": 0, "ACC": 0, "GEN": 0, "DAT": 0, "ABL": 0, "INSTR": 0, "DAT-LOC": 0}
    pos_dict = {"N": 0, "ADJ": 0, "INDEF": 0, "POSS": 0, "REL": 0, "NUM": 0, "V": 0, "PTCP": 0, "CONJ": 0, "PART": 0}
    for word in words:
        glosses = words[word][2].split(".")
        for gloss in glosses:
            if gloss in cases_dict:
                cases_dict[gloss] += 1
            if gloss in pos_dict:
                pos_dict[gloss] += 1
    return cases_dict, pos_dict


def plot_feature(feature_dict, title):
    x_names = list(feature_dict.keys())
    x_values = range(len(feature_dict))
    y_values = list(feature_dict.values())
    plt.title(title)
    plt.bar(x_values, y_values)
    plt.xticks(x_values, x_names)
    plt.show()


def main():
    path_to_hittite = "./hittite.db"
    path_to_glosses = "./Glossing_rules.txt"
    new_path = "./new_hittite.db"
    glosses = open_glosses(path_to_glosses)
    words, glosses = work_with_hittite(path_to_hittite, glosses)
    create_new_database(words, glosses)
    case_count, pos_count = count_stats(words)
    plot_feature(case_count, "Распределение падежей")
    plot_feature(pos_count, "Распределение частей речи")


if __name__ == "__main__":
    main()