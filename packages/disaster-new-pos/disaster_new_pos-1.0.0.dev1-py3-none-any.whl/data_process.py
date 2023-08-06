# encoding: utf-8

"""
author: mario
data: 2018/3/20
"""
import os
import codecs
import numpy as np

from pyltp import Postagger
from gensim.corpora.dictionary import Dictionary
from gensim.models import KeyedVectors
from keras.preprocessing import sequence

path = '/Users/bai/学习文件/GitHub项目/哈工大/ltp_data_v3.4.0/'
maxlens = 10
embed_dim = 128
def read_corpus(filename):
    """读取语料,这里只需要读取word/tag形式的语料就可以了"""
    data = []
    with filename as fr:
        for lines in fr:
            if lines != '\n':
                split_line = lines.strip().split()
                data.extend(split_line)
    filename.close()
    return data

def read_seg_data():
    filename = codecs.open('./data/seg_disasters.txt', 'r', encoding='utf-8')
    seg_datas = []
    with filename as fr:
        for line in fr:
            seg_list = []
            seg = line.split('  ')
            for s in seg:
                seg_list.append(s)
            seg_datas.append(seg_list)
    filename.close()
    return seg_datas
# def pos_tag(words):
#     """词性标注"""
#     out_path = codecs.open('./data/word_tag.txt', 'w', encoding='utf-8')
#     # 加载模型
#     postagger = Postagger()
#     postags = []
#     pos_model_path = os.path.join(path, 'pos.model')
#     postagger.load(pos_model_path)  # 词性标注
#     for word in words:
#         postag = postagger.postag(word)
#         postags.append(list(postag))
#     for word, tag in zip(words, postags):
#         for w, t in zip(word, tag):
#             out_path.write(str(w)+'/'+str(t) + '  ')
#     postagger.release()
#     out_path.close()

# def seg_data(contents):
#     """测试的时候用来做分词"""
#     segmentor = Segmentor()
#     cws_model_path = os.path.join(path, 'cws.model')
#     # 使用领域字典来进行分词
#     segmentor.load_with_lexicon(cws_model_path, './data/lexic.txt')
#     words = []
#     for content in contents:
#         word = segmentor.segment(content.encode('utf-8'))
#         words.append(list(word))
#     segmentor.release()
#     return words

def mark_tag_dis(word, tag):
    """标注灾害类型的语料"""
    co_disaster = codecs.open('./data/disaster.txt', 'r', encoding='utf-8')
    tag_disaster = codecs.open('./data/tag_disaster_update.txt', 'w', encoding='utf-8')
    co_disasters = []
    count = 0
    for data in co_disaster:
        data = data.split()
        co_disasters.extend(data)
    for (w, t) in zip(word, tag):
        count += 1
        if t in ['ns']:
            tag_disaster.write(w + '/' + 'LOC' + '  ')
            # len_word = len(w)
            # tag_disaster.write(w[0] + '/' + "B-LOC" + '  ')
            # for each in w[1: len_word - 1]:
            #     tag_disaster.write(each + '/' + "M-LOC" + '  ')
            # tag_disaster.write(w[len_word - 1] + '/' + "E-LOC" + '  ')
        elif t in ['nt']:
            tag_disaster.write(w + '/' + 'TIME' + '  ')
            # len_word = len(w)
            # tag_disaster.write(w[0] + '/' + 'B-TIME' + '  ')
            # for each in w[1: len_word - 1]:
            #     tag_disaster.write(each + '/' + 'M-TIME' + '  ')
            # tag_disaster.write(w[len_word - 1] + '/' + 'E-TIME' + '  ')
        elif w in co_disasters:
            tag_disaster.write(w + '/' + 'DIS' + '  ')
            # len_word = len(w)
            # tag_disaster.write(w[0] + '/' + "B-DIS" + '  ')
            # for each in w[1: len_word - 1]:
            #     tag_disaster.write(each + '/' + "M-DIS" + '  ')
            # tag_disaster.write(w[len_word - 1] + '/' + "E-DIS" + '  ')
        else:
            # len_word = len(w)
            # tag_disaster.write(w[0] + '/' + "O" + '  ')
            # for each in w[1: len_word - 1]:
            #     tag_disaster.write(each + '/' + "O" + '  ')
            # tag_disaster.write(w[len_word - 1] + '/' + "O" + '  ')
            tag_disaster.write(w + '/' + 'O' + '  ')
        if count % 100 == 0:
            tag_disaster.write('\n')
    co_disaster.close()
    tag_disaster.close()

def get_disaster_corpus():
    """读取灾害类型分词后的语料"""
    input_path = codecs.open('./data/seg_disasters.txt', 'r', encoding='utf-8')
    with input_path as ip:
        for lines in ip:
            print("lines", lines[:5])
    input_path.close()



def split_word_tag(data):
    """将word/tag形式的语料切分开，分别存储到word和tag列表中"""
    word, tag = [], []
    for word_tag_pair in data:
        # print('word_tag_pair', word_tag_pair)
        pairs = word_tag_pair.split('/')
        try:
            if(len(pairs[0].strip()) != 0 and len(pairs[1].strip()) != 0):
                word.append(pairs[0].strip())
                tag.append(pairs[1].strip())
        except:
            pass

    return word, tag

def mark_tag(word, tag):
    """标注特定领域命名实体"""
    # 打开文件夹一定要记得关闭
    output_file = codecs.open('./data/tag_news_update.txt', 'w', encoding='utf-8')
    input_file = codecs.open('./data/disaster.txt', 'r', encoding='utf-8')
    disaster_data = []
    count = 0
    for data in input_file:
        data = data.split()
        disaster_data.extend(data)
    print('disaster_data', disaster_data)
    for(w, t) in zip(word, tag):
        count += 1
        if t in ['ns', 'nsf']:
            # len_word = len(w)
            # output_file.write(w[0] + '/' + "B-LOC" + '  ')
            # for each in w[1: len_word - 1]:
            #     output_file.write(each + '/' + "M-LOC" + '  ')
            # output_file.write(w[len_word - 1] + '/' + "E-LOC" + '  ')
            output_file.write(w + '/' + 'LOC' + '  ')
        elif t in ['t']:
            # len_word = len(w)
            # output_file.write(w[0] + '/' + 'B-TIME' + '  ')
            # for each in w[1: len_word - 1]:
            #     output_file.write(each + '/' + 'M-TIME' + '  ')
            # output_file.write(w[len_word - 1] + '/' + 'E-TIME' + '  ')
            output_file.write(w + '/' + 'TIME' + '  ')
        elif w in disaster_data:
            # len_word = len(w)
            # output_file.write(w[0] + '/' + "B-DIS" + '  ')
            # for each in w[1: len_word - 1]:
            #     output_file.write(each + '/' + "M-DIS" + '  ')
            # output_file.write(w[len_word - 1] + '/' + 'E-DIS' + '  ')
            output_file.write(w + '/' + 'DIS' + '  ')
        else:
            # len_word = len(w)
            # output_file.write(w[0] + '/' + "O" + '  ')
            # for each in w[1: len_word - 1]:
            #     output_file.write(each + '/' + "O" + '  ')
            # output_file.write(w[len_word - 1] + '/' + "O" + '  ')
            output_file.write(w + '/' + 'O' + '  ')
        if count % 100 == 0:
            output_file.write('\n')
    output_file.close()
    input_file.close()


def word2vec_obtain():
    """词向量的获取"""
    model = KeyedVectors.load_word2vec_format('./vec_model/word2vec_models.txt', binary=False)
    w2index, w2vec = create_dictionaries(model=model)
    return w2index, w2vec

def create_dictionaries(model=None):
    """创建词向量字典"""
    if model is not None:
        gensim_dict = Dictionary()    # 创建字典对象, key是字典中的词, 其val实词对应的唯一数值型ID
        gensim_dict.doc2bow(model.vocab.keys(), allow_update=True)
        w2index = {v: k+1 for k, v in gensim_dict.items()}    # 词语的索引，从1开始编号，如{中国: 1}
        w2vec = {word: model[word] for word in w2index.keys()}
        return w2index, w2vec

def text2index(w2index, data):
    """词转换为索引,比如[中国，安徽，合肥]--->[1, 5, 30]"""
    new_datas = []
    for word in data:
        new_word = []
        for each in word:
            try:
                new_word.append(w2index[each])
            except:
                new_word.append(0)
        new_datas.append(new_word)
    new_datas = sequence.pad_sequences(new_datas, padding='post', maxlen=maxlens)
    return new_datas

def get_data(w2index, w2vec):
    """获取所有词语的个数和词索引与词向量对应的矩阵"""
    word_count = len(w2index) + 1
    index_embed_martix = np.zeros((word_count, embed_dim))
    for word, index in w2index.items():    # 创建一个 word_cout * embed_dim的0矩阵
        index_embed_martix[index, :] = w2vec[word]    # 词向量矩阵，第一行是0向量(没有索引为0的词语，未被填充)
    return word_count, index_embed_martix
def generate_label(datas):
    """将标签生成词向量的形式"""
    label_path = codecs.open('./data/tag.txt', 'r', encoding='utf-8')
    label_dict = {}
    label_data = [label.split() for label in label_path]
    label_len = len(label_data)
    for i in range(label_len):
        label_one_hot = np.zeros(label_len, dtype=int)
        label_one_hot[i] = 1
        label_dict[label_data[i][0]] = label_one_hot
    labels = []
    for data in datas:
        labels.append(label_dict[data])

    # for data in datas:
    #     label = []
    #     for word in data:
    #         label.append(label_dict[word])
    #     labels.append(label)
    #     label_path.close()
    return labels
# if __name__ == '__main__':
#     train_path = codecs.open('./data/train_data.txt', 'r', encoding='utf-8')
#     disaster_path = codecs.open('./data/word_tag.txt', 'r', encoding='utf-8')
#     # data = read_seg_data()
#     # pos_tag(data)
#     # seg_data()
#     # data = read_corpus(disaster_path)
#     # word, tag = split_word_tag(data)
#     # mark_tag_dis(word, tag)
#
#     # generate_label()
#
#     # word2vec_obtain()
#     # data = read_corpus(train_path)
#     # word, tag = split_word_tag(data)
#     # mark_tag(word, tag)
#     # print('word', word[:5])
#     # print('tag', tag[:5])
#     # mark_tag(word, tag)
#     # get_disaster_corpus()
#     mark_disaster_tag()

















