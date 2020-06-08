from flask import Blueprint, request, render_template,g, current_app
from  flaskblog.models import Post
from flask_login import current_user, login_required
from flaskblog.main.forms import SearchForm
from flask_babel import get_locale
import requests
import json
from datetime import datetime
from flaskblog.scrape import scrape_medium
main = Blueprint('main',__name__)


@main.route("/")
@main.route("/home")
def home():
    page=request.args.get('page',1, type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('home.html', posts=posts, current_user=current_user)

@main.route("/about")
def about():
    return render_template('about.html', title = 'About')


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@main.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None

    query_string = g.search_form.q.data
    url= 'https://api.stackexchange.com/2.2/search/advanced?page=1&pagesize=20&order=desc&sort=relevance&site=stackoverflow'    
    payload ={ 'q':query_string , 'accepted':'true', 'closed':'true', 'migrated':'false',}
    stack_response = json.loads(requests.get(url, params=payload).text)
    medium_response = scrape_medium(query_string)
    #for post in stack_response['items']:
        #print(post['title'])
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url, stack_response=stack_response['items'], medium_response=medium_response)
