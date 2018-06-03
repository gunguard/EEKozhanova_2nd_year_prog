# ДЗ по графам и word2vec
# Ваша задача построить сеть для произвольного семантического поля, где узлами будут слова, а ребрами наличие косинусного расстояния больше 0.5 в word2vec-модели.
# Вычислите самые центральные слова графа, его радиус (для каждой компоненты связности) и коэффициент кластеризации.

# Нужный семинар:
# https://github.com/ancatmara/learnpython2017/blob/master/%D0%A1%D0%B5%D0%BC%D0%B8%D0%BD%D0%B0%D1%80%D1%8B/word2vec.ipynb
# https://github.com/ancatmara/learnpython2017/blob/master/%D0%A1%D0%B5%D0%BC%D0%B8%D0%BD%D0%B0%D1%80%D1%8B/%D0%93%D1%80%D0%B0%D1%84%D1%8B%2C%20networkx.ipynb

# Полицейский, нелегальный, запрещенный, насильный, неоправданный, арестный, криминальный, злостный
# Политические координаты: либерализм_NOUN анархизм_NOUN марксизм_NOUN коммунизм_NOUN демократия_NOUN
# фашизм_NOUN нацизм_NOUN национализм_NOUN либертарианствоа_NOUN консерватизм_NOUN джамахирия_NOUN традиционализм_NOUN феминизм_NOUN
# радикализм_NOUN волюнтаризм_NOUN  социализм_NOUN монархизм_NOUN объективизм_NOUN центризм_NOUN ленинизм_NOUN агоризм_NOUN
#

import networkx
import gensim
import matplotlib.pyplot as plt

# модель
model_p = 'ruscorpora_upos_skipgram_300_5_2018.vec'

model = gensim.models.KeyedVectors.load_word2vec_format(model_p, binary=False)
model.init_sims(replace=True)

field = ['авторитаризм_NOUN', 'либерализм_NOUN', 'анархизм_NOUN', 'марксизм_NOUN', 'коммунизм_NOUN',
             'демократия_NOUN', 'фашизм_NOUN', 'нацизм_NOUN', 'национализм_NOUN',
             'консерватизм_NOUN', 'традиционализм_NOUN', 'радикализм_NOUN',
             'волюнтаризм_NOUN', 'социализм_NOUN', 'монархизм_NOUN', 'объективизм_NOUN', 'центризм_NOUN',
             'ленинизм_NOUN', 'исламизм']
# граф
graph = networkx.Graph()
graph.add_nodes_from(field)

field_2 = [i for i in field[1:]]
edges = []
for word1 in field:
    for word2 in field_2:
        closure = model.similarity(word1,word2)
        print(word1,word2,closure)
        if closure > 0.5:
            edges.append((word1,word2))
    if field_2:
        field_2.pop(0)
graph.add_edges_from(edges)

# центральные слова графа
deg = networkx.degree_centrality(graph)
for nodeid in sorted(deg, key=deg.get, reverse=True):
    print(nodeid,deg[nodeid])

# кластеризация
print(networkx.average_clustering(graph))

# компонент связности
components = [i for i in networkx.connected_component_subgraphs(graph) if len(i.nodes())>1]
print('Центр',"Количество вершин",'Радиус',"Кластеризации", sep='\t')
for component in components:
    print(sorted(networkx.degree_centrality(component), key = lambda x: deg[x], reverse = True)[0],
          len(component.nodes()),networkx.radius(component), networkx.average_clustering(component),sep='\t')

# визуализация
plt.figure(figsize=(15,15))
pos = networkx.spring_layout(graph)
networkx.draw_networkx_nodes(graph, pos, node_color='green', node_size=12)
networkx.draw_networkx_edges(graph, pos, edge_color='blue')
networkx.draw_networkx_labels(graph, pos, font_size=10, font_family='Arial')
plt.axis('off')
plt.show()