from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer

class DummyTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, column):
        self.column = column
        self.label_binarizer = None

    def fit(self, X, y=None, **kwargs):
        self.label_binarizer = LabelBinarizer()
        self.label_binarizer.fit(X[self.column])
        return self

    def transform(self, X, y=None, **kwargs):
        return self.label_binarizer.transform(X[self.column])
    

class TfidfTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, column):
        self.column = column
        self.tfidf = None

    def fit(self, X, y=None, **kwargs):
        self.tfidf = TfidfVectorizer(token_pattern=r'\b[a-zA-Z0-9-]+\b',
                                     ngram_range=(1,1), min_df=1)
        self.tfidf.fit(X[self.column].values)
        return self

    def transform(self, X, y=None, **kwargs):
        return self.tfidf.transform(X[self.column].values)


class FillNaNTextTransformer(BaseEstimator, TransformerMixin):
    """ fill NaN text features with desired label """

    def __init__(self, columns, replace_value=None):
        self.columns = columns
        self._fill_value = ''
        self._replace_value = replace_value or 'UNKNOWN'
            

    def fit(self, X, y=None, **kwargs):
        return self

    def transform(self, X, y=None, **kwargs):
        X = X.copy()
        for col in self.columns:
            X[col] = X[col].fillna(self._fill_value)\
                     .replace(r'^$', self._replace_value, regex=True)
        return X
