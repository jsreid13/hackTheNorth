import gensim

model = gensim.models.FastText.load('./fasttext.model')

def suggest_items(items, n):
	return model.wv.most_similar(positive=items, topn=n)