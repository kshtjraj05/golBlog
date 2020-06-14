
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, Response, jsonify, json)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Comment, Downvote_association, Upvote_association, Domain
from flaskblog.posts.forms import PostForm, CommentForm, UpvoteForm, DownvoteForm
from flaskblog.domains.forms import DomainForm
from flaskblog.domains.routes import get_domains
posts = Blueprint('posts',__name__)




@posts.route("/post/new", methods = ['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    domain_form =DomainForm()
    lst = get_domains()
    d=[]
    for x in lst:
        d.append((x,x))
    form.domain.choices=d
    if form.validate_on_submit():
        domain_name=dict(form.domain.choices).get(form.domain.data)
        domain=Domain.query.filter_by(domain_name=domain_name).first_or_404()
        post=Post(title=form.title.data, content = form.content.data, author=current_user,domain_id=domain.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html',title='New Post', form = form, legend = 'New Post', domain_form=domain_form)

@posts.route("/post/<int:post_id>", methods = ['GET', 'POST'])
@login_required
def post(post_id):

    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post=post)

    form = CommentForm()
    if form.validate_on_submit():
        comment=Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        return Response(status=200)
    return render_template('post.html',title=post.title,post=post, form= form, comments=comments)

@posts.route("/post/<int:post_id>/add_comment", methods = ['POST'])
def comment(post_id):
    post=Post.query.get_or_404(post_id)
    form=CommentForm(request.form)
    if form.validate_on_submit():
        comment=Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        return Response(status=200)
    return Response(status=500)

@posts.route("/post/<int:post_id>/update", methods = ['GET','POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if(post.author != current_user):
        abort(403)
    form = PostForm()
    domain_form = DomainForm()
    lst = get_domains()
    d=[]
    for x in lst:
        d.append((x,x))
    form.domain.choices=d
    if form.validate_on_submit():
        domain_name=dict(form.domain.choices).get(form.domain.data)
        domain=Domain.query.filter_by(domain_name=domain_name).first_or_404()
        post.title = form.title.data
        post.content = form.content.data
        post.domain=domain
        db.session.commit()
        flash('Post has been updated','success')
        return redirect(url_for('posts.post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data=post.title
        form.content.data=post.content
        form.submit.data='Update'
    return render_template('create_post.html',title='Update post', form = form, legend = 'Update Post', domain_form=domain_form)

@posts.route('/posts/<int:post_id>/is_upvoted')
@login_required
def is_upvoted(post_id):
    x=Upvote_association.query.get((current_user.id, post_id))
    if x != None:
        return jsonify({'text':'Upvoted'})
    else:
        return jsonify({'text':'Upvote'})
    
@posts.route('/posts/<int:post_id>/is_downvoted')
@login_required
def is_downvoted(post_id):
    x=Downvote_association.query.get((current_user.id, post_id))
    if x != None:
        return jsonify({'text':'Downvoted'})
    else:
        return jsonify({'text':'Downvote'})

@posts.route("/post/<int:post_id>/delete", methods = ['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if(post.author != current_user):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.home'))

@posts.route('/post/<int:post_id>/upvote', methods=['POST'])
def upvote(post_id):
    x=Upvote_association.query.get((current_user.id, post_id))
    y=Downvote_association.query.get((current_user.id, post_id))

    a=Upvote_association()
    a.post=Post.query.get_or_404(post_id)
    a.user=current_user
    if y != None:
        db.session.delete(y)
    current_user.children_upvoted_posts.append(a)
    db.session.commit()
    status_code = Response(status=200)
    return status_code 

@posts.route('/post/<int:post_id>/remove_upvote', methods=['POST'])
def remove_upvote(post_id):
    x=Upvote_association.query.get((current_user.id, post_id))
    db.session.delete(x)
    db.session.commit()
    status_code = Response(status=200)
    return status_code 


@posts.route('/post/<int:post_id>/downvote',methods=['POST'])
def downvote(post_id):
    x=Upvote_association.query.get((current_user.id, post_id))
    y=Downvote_association.query.get((current_user.id, post_id))
    a=Downvote_association()
    a.post=Post.query.get_or_404(post_id)
    a.user=current_user
    if x != None:
        db.session.delete(x)
    current_user.children_downvoted_posts.append(a)
    db.session.commit()
    status_code = Response(status=200)
    return status_code 

@posts.route('/post/<int:post_id>/remove_downvote', methods=['POST'])
def remove_downvote(post_id):
    y=Downvote_association.query.get((current_user.id, post_id))
    db.session.delete(y)
    db.session.commit()
    status_code = Response(status=200)
    return status_code 