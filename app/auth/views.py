from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=request.values.get('email')).first()
        if user is not None and user.verify_password(request.values.get('password')):   # verify_password()其参数是表单中填写的密码
            login_user(user, request.values.getlist('remember_me'))     # login_user()在用户会话中把用户标记为已登录
            next = request.args.get('next')                             # 是否记住我，Flask-Login会把原URL 保存在查询字符串的next 参数中
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.', 'error')
    return render_template('auth/login.html', form=form)

    # form = LoginForm()
    # if form.validate_on_submit():           # validate_on_submit()验证表单数据
    #     user = User.query.filter_by(email=form.email.data).first()
    #     if user is not None and user.verify_password(form.password.data):   # verify_password()其参数是表单中填写的密码
    #         login_user(user, form.remember_me.data)     # login_user()在用户会话中把用户标记为已登录
    #         next = request.args.get('next')             # 是否记住我，Flask-Login会把原URL 保存在查询字符串的next 参数中
    #         if next is None or not next.startswith('/'):
    #             next = url_for('main.index')
    #         return redirect(next)
    #     flash('Invalid username or password.')
    # return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required             # 保护路由：为了保护路由，只让通过身份验证的用户访问
def logout():
    logout_user()           # 删除并重设用户会话
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])       # 首页 - User Rights - Register
@login_required
def register():
    if request.method == 'POST':
        email = request.values.get('email')
        username = request.values.get('username')
        password = request.values.get('password')
        password2 = request.values.get('password2')
        name = request.values.get('name')
        groupid = request.values.get('groupid')
        slmsname = request.values.get('slmsname')

        u1 = User.query.filter_by(email=email).all()
        u2 = User.query.filter_by(username=username).all()
        if len(u1) > 0:
            flash('该邮箱已经被注册！')
        elif len(u2):
            flash('该用户名已经存在！')
        elif password != password2:
            flash('两次输入的密码不匹配！')
        else:
            user = User(email=email,
                        username=username,
                        password=password,
                        name=name,
                        slmsname=slmsname,
                        groupid=groupid)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account',
                       'auth/email/confirm', user=user, token=token)
            flash('A confirmation email has been sent to you by email.')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     user = User(email=form.email.data, username=form.username.data, password=form.password.data)
    #     db.session.add(user)
    #     db.session.commit()
    #     token = user.generate_confirmation_token()
    #     send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
    #     flash('A confirmation email has been sent to you by email.')
    #     return redirect(url_for('auth.login'))
    # return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')     # 确认用户的账户
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.index'))


@auth.before_app_request        # 使用before_app_request 处理程序过滤未确认的账户
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
# is_authenticated 如果用户已通过身份验证，即提供的登录凭据有效，必须返回True，否则返回False
# request.endpoint更新已登录用户的最后访问时间


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
# is_anonymous 对普通用户必须始终返回False，如果是表示匿名用户的特殊用户对象，应该返回True


@auth.route('/confirm')         # 重新发送账户确认邮件
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/personal/<username>', methods=['GET', 'POST'])            # 个人主页
@login_required
def personal(username):

    return render_template("auth/personal.html")


@auth.route('/reset-password/', methods=['GET', 'POST'])                # 首页 - User Rights - Reset Password
@login_required
def reset_password():
    if request.method=='POST':
        email = request.values.get('email')
        newpwd = request.values.get('newpwd')
        newpwd2 = request.values.get('newpwd2')
        user = User.query.filter_by(email=email).first_or_404()

        if newpwd!=newpwd2:
            flash("两次输入的新密码不正确")
        else:
            user.password=newpwd
            db.session.add(user)
            db.session.commit()
            flash('Password has been updated.')
            return redirect(url_for('main.index'))
    return render_template("auth/resetpwd_byadmin.html")
