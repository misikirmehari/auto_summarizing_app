from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from bs4 import BeautifulSoup
from heapq import nlargest
from nltk.probability import FreqDist
from collections import defaultdict
import urllib.request

app = Flask(__name__)


# Prepare our article summarizer


# Gets a url as a parameter and returns an article with
# out the html tags encoded in UTF-8
def getTextWapo(url):
    page = urllib.request.urlopen(url).read().decode('utf8', 'ignore')
    soup = BeautifulSoup(page, "lxml")
    text = ' '.join(map(lambda p: p.text, soup.find_all('article')))
    return text.replace(u'\xa0', u' ')


# Get the article url as a parameter and return the links of all images in the article
def getImages(url):
    r = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(r)  # Setup a "soup" which BeautifulSoup can search
    links = []

    for link in soup.find_all('img'):  # Cycle through all 'img' tags
        imgSrc = link.get('src')  # Extract the 'src' from those tags
        links.append(imgSrc)  # Append the source to 'links'

    return links  # Return 'links'


# Summarize the article
def summarize(text, n):
    sents = sent_tokenize(text)

    assert n <= len(sents)
    word_sent = word_tokenize(text.lower())
    _stopwords = set(stopwords.words('english') + list(punctuation))

    word_sent = [word for word in word_sent if word not in _stopwords]
    freq = FreqDist(word_sent)
    ranking = defaultdict(int)

    for i, sent in enumerate(sents):
        for w in word_tokenize(sent.lower()):
            if w in freq:
                ranking[i] += freq[w]
    sents_idx = nlargest(n, ranking, key=ranking.get)

    return [sents[j] for j in sorted(sents_idx)]


class SummaryForm(Form):
    articleurl = TextAreaField('', [validators.DataRequired()])
    numsent = TextAreaField('', [validators.DataRequired()])


@app.route('/')
def index():
    form = SummaryForm(request.form)
    return render_template('index.html', form=form)


@app.route('/summary', methods=['POST'])
def summary():
    form = SummaryForm(request.form)
    if request.method == 'POST' and form.validate():
        name = request.form['articleurl']
        num = request.form['numsent']
        article_text = getTextWapo(name)
        summarizedarticle = summarize(article_text, int(num))
        article_image = getImages(name)
        image = article_image[7]
        return render_template('summary.html', name=summarizedarticle, webimages=image)
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
