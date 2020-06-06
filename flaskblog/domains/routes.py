from flaskblog.domains.forms import DomainForm, UpdateDomainForm, Follow
from flaskblog import db
from flask import url_for, redirect, Blueprint, request, render_template, current_app, flash
from flaskblog.models import Domain, Post
from flask_login import current_user, login_required
domains = Blueprint('domains',__name__)

@domains.route('/create_domain', methods=['GET','POST'])
def create_domain():
    if not current_user.is_authenticated:
        abort(403)
    form = DomainForm(request.form)
    if form.validate_on_submit():
        
        domain=Domain(domain_name=form.domain_name.data, user_id=current_user.id)        
        db.session.add(domain)
        db.session.commit()
        return redirect(url_for('posts.new_post'))

@domains.route('/get_domains', methods=['GET'])
def get_domains():
    lst=[]
    for domain in Domain.query.all():
        lst.append(domain.domain_name)
    return lst

@domains.route('/get_domains2', methods=['GET'])
def get_domains2():
    lst=[]
    for domain in Domain.query.all():
        lst.append(domain)
    return render_template('domain_categories.html',lst=lst)


@domains.route('/get_domains_posts/<string:domain_name>', methods=['GET','POST'])
@login_required
def domain_profile(domain_name):
    form=Follow()
    domain=Domain.query.filter_by(domain_name=domain_name).first_or_404()
    page=request.args.get('page',1, type=int)
    if current_user.is_following_domain(domain):
        form.follow_button.label.text='Followed'
    posts=Post.query.filter_by(domain=domain)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5)
    return render_template('domain_profile.html', domain=domain, posts = posts, form = form)

@domains.route("/domain/<int:domain_id>/follow", methods=['POST'])
def follow(domain_id):
    domain=Domain.query.get_or_404(domain_id)
    if request.args.get('str') == 'Follow':
        current_user.follow_domain(domain)
    else:
        current_user.unfollow_domain(domain)
    return redirect(url_for('domains.domain_profile', domain_name=domain.domain_name))

@domains.route('/domain/<int:domain_id>/update_domain', methods=['GET','POST'])
def update_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    if domain.creator != current_user:
        abort(403)
    form = UpdateDomainForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            domain.domain_image=picture_file
        domain.domain_name= form.domain_name.data
        db.session.commit()
        flash('Your domain has been updated', 'success')
        return redirect(url_for('domains.domain_profile', domain_name=domain.domain_name))
    elif request.method=='GET':
        form.domain_name.data=domain.domain_name

    domain_image = url_for('static', filename ="domain_pics/"+domain.domain_image)
    return render_template('domain_update.html', form=form, domain=domain)

