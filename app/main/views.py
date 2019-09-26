from flask import render_template, session, redirect, url_for, current_app, flash, request
from .. import db
from ..models import User, Role, Permission
from ..email import send_email
from . import main
from .forms import NameForm
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('user/<username>')          # 资料页面的路由
def user(username):
    user = User.query.filter_by(username=username).first_or_404()       # 如果传入路由的用户名不存在，则返回404 错误
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])       # 资料编辑路由
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])      # 管理员的资料编辑路由
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
