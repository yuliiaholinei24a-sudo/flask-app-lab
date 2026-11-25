from flask import flash, redirect, render_template, url_for

from app import db

from . import post_bp
from .forms import DeletePostForm, PostForm
from .models import Post, Tag


@post_bp.route("")
def all_posts():
    stmt = (
        db.select(Post)
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc(), Post.id.desc())
    )

    posts = db.session.scalars(stmt).all()

    return render_template(
        "posts/all_posts.html",
        title="Пости",
        posts=posts,
    )


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        selected_tags = []
        if form.tags.data:
            selected_tags = db.session.scalars(
                db.select(Tag).where(Tag.id.in_(form.tags.data))
            ).all()

        post = Post(
            title=form.title.data,
            content=form.content.data,
            posted=form.publish_date.data,
            category=form.category.data,
            is_active=form.enabled.data,
            user_id=form.author_id.data,
            tags=selected_tags,
        )

        db.session.add(post)
        db.session.commit()

        flash("Пост успішно створено.", "success")

        return redirect(
            url_for("posts.detail_post", id=post.id)
        )

    return render_template(
        "posts/add_post.html",
        title="Створення поста",
        form=form,
        post=None,
    )


@post_bp.route("/<int:id>")
def detail_post(id):
    post = db.get_or_404(Post, id)

    return render_template(
        "posts/detail_post.html",
        title=post.title,
        post=post,
    )


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)

    if not form.is_submitted():
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted
        form.author_id.data = post.user_id
        form.tags.data = [tag.id for tag in post.tags]

    if form.validate_on_submit():
        selected_tags = []
        if form.tags.data:
            selected_tags = db.session.scalars(
                db.select(Tag).where(Tag.id.in_(form.tags.data))
            ).all()

        post.title = form.title.data
        post.content = form.content.data
        post.posted = form.publish_date.data
        post.category = form.category.data
        post.is_active = form.enabled.data
        post.user_id = form.author_id.data
        post.tags = selected_tags

        db.session.commit()

        flash("Пост успішно оновлено.", "success")

        return redirect(
            url_for("posts.detail_post", id=post.id)
        )

    return render_template(
        "posts/add_post.html",
        title="Редагування поста",
        form=form,
        post=post,
    )


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)
    form = DeletePostForm()

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()

        flash("Пост успішно видалено.", "success")

        return redirect(url_for("posts.all_posts"))

    return render_template(
        "posts/delete_confirm.html",
        title="Видалення поста",
        form=form,
        post=post,
    )