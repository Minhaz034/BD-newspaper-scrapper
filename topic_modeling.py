import sys
# !{sys.executable} -m spacy download en
import re, numpy as np, pandas as pd
from pprint import pprint
import pyLDAvis.gensim_models
# pyLDAvis.enable_notebook()
# Gensim
import gensim, spacy, logging, warnings
import gensim.corpora as corpora
import nltk
from gensim.utils import  simple_preprocess
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt
# nltk.download('stopwords')
# NLTK Stop words
from nltk.corpus import stopwords


warnings.filterwarnings("ignore",category=DeprecationWarning)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

class TopicModel():
    stop_words = stopwords.words('english')
    stop_words.extend(
        ['from', 'subject', 're', 'edu', 'use', 'not', 'would', 'say', 'could', '_', 'be', 'know', 'good', 'go', 'get',
         'do', 'done', 'try', 'many', 'some', 'nice', 'thank', 'think', 'see', 'rather', 'easy', 'easily', 'lot',
         'lack', 'make', 'want', 'seem', 'run', 'need', 'even', 'right', 'line', 'even', 'also', 'may', 'take', 'come',
         'aci'])


    def sentence_to_words(self,sentences):
        for sent in sentences:
            sent = re.sub('\S*@\S*\s?', '', sent)  # remove emails
            sent = re.sub('\s+', ' ', sent)  # remove newline chars
            sent = re.sub("\'", "", sent)  # remove single quotes
            sent = gensim.utils.simple_preprocess(str(sent), deacc=True)
            yield (sent)

    def process_words(self, texts, stop_words=stop_words, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        data_words = self.sentence_to_words(texts)
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod = gensim.models.phrases.Phraser(trigram)

        texts = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
        texts = [bigram_mod[doc] for doc in texts]
        texts = [trigram_mod[bigram_mod[doc]] for doc in texts]
        # texts_out = []
        # nlp = spacy.load('en', disable=['parser', 'ner'])
        # for sent in texts:
        #     doc = nlp(" ".join(sent))
        #     texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        # remove stopwords once more after lemmatization

        # texts_out = [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts_out]
        return texts

    def make_topic_model(self,data_ready):
        id2word = corpora.Dictionary(data_ready)
        corpus = [id2word.doc2bow(text) for text in data_ready]

        # Build LDA model
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=4,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=10,
                                                    passes=10,
                                                    alpha='symmetric',
                                                    iterations=100,
                                                    per_word_topics=True)

        # pprint(lda_model.print_topics())
        vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary=lda_model.id2word)

        return lda_model, vis






if __name__ == '__main__':
    sample_raw_inputs = ["Agricultural machinery is beyond the reach of farmers",
                         "Alamgir, who wanted to teach in exchange for rice, got a job in ACI Logistics Limited",
                         "Job opportunities in ACI Group with attractive salary"]

    raw_inputs = []
    df = pd.read_csv("outputs.csv")
    for tweet in df['description']:
        if isinstance(tweet, str):
            raw_inputs.append(tweet)
    # print(raw_inputs)
    obj = TopicModel()
    data_ready = obj.process_words(texts=raw_inputs)

    model, vis =  obj.make_topic_model(data_ready)
    print(model.print_topics())
    pyLDAvis.save_html(vis, 'lda_outputs.html')


