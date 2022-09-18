from app import app
import requests
from flask import render_template, request, url_for, flash, redirect
from . import util

our_feeds = {
     '3dnews': 'https://3dnews.ru/news/rss/'}
#  'hi-tech':'https://hi-tech.mail.ru/rss/all/'}
f_all_news = 'allnews.csv'
f_certain_news = 'certainnews23march.csv'
vector1 = 'ДолЛАР|РубЛ|ЕвРО'
vector2 = 'ЦБ|СбЕРбАНК|курс'


@app.route('/')
def index():
    news = util.News(our_feeds, f_all_news, f_certain_news, vector1, vector2)
    news.addNews()
    news.write_all_news(f_all_news)
    conn = util.get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    count = len(news.alldescriptions)
    conn.close()
    return render_template('/blog/index.html', posts=posts, temperature=util.temperature(),
                           desc=news.alldescriptions, title=news.allheadlines,
                           links=news.alllinks, datetime=news.alldates, img=news.allImg, count=count)


@app.route('/<int:post_id>')
def post(post_id):
    post = util.get_post(post_id)
    return render_template('/blog/post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = util.get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('/blog/create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = util.get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = util.get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('/blog/edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = util.get_post(id)
    conn = util.get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/registration')
def registration():
    return render_template('/auth/registration.html')


@app.route('/city')
def search_city():
    API_KEY = '01711b167ecd7d1e5977867e1453a795'  # initialize your key here
    city = request.args.get('q')  # city name passed as argument

    # call API and convert response into Python dictionary
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={API_KEY}'
    response = requests.get(url).json()

    # error like unknown city name, inavalid api key
    if response.get('cod') != 200:
        message = response.get('message', '')
        return f'Error getting temperature for {city.title()}. Error message = {message}'

    # get current temperature and convert it into Celsius
    current_temperature = response.get('main', {}).get('temp')
    if current_temperature:
        current_temperature_celsius = round(current_temperature - 273.15, 2)
        return f'Current temperature of {city.title()} is {current_temperature_celsius} &#8451;'
    else:
        return f'Error getting temperature for {city.title()}'
