from flask import render_template, session, redirect, url_for, current_app, flash, request
from .. import db
from ..models import User, db, RegisterCheckOutFile, Recipients, Systemm, Projectm, Liaisonf, Qahf, Qadf, Feedback, Updatelog, Qadfproof, Role
from ..email import askchk_send_email
from . import main
from .forms import NameForm
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required, Permission
from datetime import date,datetime


@main.route('/')
@login_required
def index():
    return render_template('index.html')


@main.route('user/<username>')          # 资料页面的路由
def user(username):
    # user = User.query.filter_by(username=username).first_or_404()       # 如果传入路由的用户名不存在，则返回404 错误
    # return render_template('user.html', user=user)
    if current_user.can(Permission.WRITE) and request.method == 'POST':
        filter = []
        filter1 = []
        fsystem = request.values.get('fsystem')
        fcomment = request.values.get('fcomment')
        fchkoutobj = request.values.get('fchkoutobj')
        fslipno = request.values.get('fslipno')
        filter.append(RegisterCheckOutFile.fsystem == fsystem)
        filter.append(RegisterCheckOutFile.fcomment == fcomment)
        filter.append(RegisterCheckOutFile.fchkoutobj == fchkoutobj)
        filter.append(RegisterCheckOutFile.fchkstatus != '3-Check In')
        chkcount = RegisterCheckOutFile.query.filter(*filter).all()
        for chk in chkcount:
            if chk.fchkstatus != '4-Un Check Out':
                flash("该对象已经被迁出！")
                return redirect(url_for('.user', username=current_user.username))
        if len(fchkoutobj.strip()) == 0:
            flash("迁出对象不可为空！")
        elif len(fslipno.strip()) == 0:
            flash("联络票号不可为空！")
        else:
            chk = RegisterCheckOutFile(
                fsystem=request.values.get('fsystem'),
                fchkoutobj=request.values.get('fchkoutobj'),
                fcomment=request.values.get('fcomment'),
                fslipno=request.values.get('fslipno'),
                fapplicant=current_user.name,
                fchkoutperson=request.values.get('chkoutperson'),
                fchkstatus='1-ASK',
                fchkinperson=request.values.get('chkinperson'),
                applicant_id=current_user.id
            )
            db.session.add(chk)
            db.session.commit()
            session['fsystem'] = chk.fsystem
            session['fcomment'] = chk.fcomment
            session['fslipno'] = chk.fslipno
            return redirect(url_for('.user', username=current_user.username))

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.checkouts.order_by(RegisterCheckOutFile.fchkstatus, RegisterCheckOutFile.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    checkouts = pagination.items
    return render_template('user.html', user=user, checkouts=checkouts,
                           pagination=pagination, fcomment=session.get("fcomment"), fsystem=session.get("fsystem"),
                           fslipno=session.get("fslipno"))


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


# @main.route('/check-out/<int:id>')
# @login_required
# def check_out(id):
#     checkout = RegisterCheckOutFile.query.get_or_404(id)
#     return render_template('_post_bysys.html', checkouts=[checkout])


@main.route('/system/<system>/')                    # 程序管理 - 显示迁出文件的工厂名,例:OMS, OMR
@login_required
def system(system):
    checkout = RegisterCheckOutFile.query.filter_by(fsystem=system).order_by(RegisterCheckOutFile.fregisterdte.desc()).all()
    return render_template('_post_bysys.html', checkouts=checkout)


@main.route('/file/<fchkoutobj>')                   # 程序管理 - 显示迁出文件的文件名称
@login_required
def file(fchkoutobj):
    checkout = RegisterCheckOutFile.query.filter_by(fchkoutobj=fchkoutobj).all()
    return render_template('_post_bysys.html', checkouts=checkout)


@main.route('/status/<fchkstatus>')                 # 程序管理 - 显示迁出文件的状态
@login_required
def status(fchkstatus):
    checkout = RegisterCheckOutFile.query.filter_by(fchkstatus=fchkstatus).order_by(RegisterCheckOutFile.fregisterdte.desc()).all()
    return render_template('_post_bysys.html', checkouts=checkout)


@main.route('/slipno/<fslipno>')                    # 程序管理 - 显示迁出文件的联络票号
@login_required
def fslipno(fslipno):
    checkout = RegisterCheckOutFile.query.filter_by(fslipno=fslipno).order_by(RegisterCheckOutFile.fregisterdte.desc()).all()
    return render_template('_post_bysys.html', checkouts=checkout)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])  # 程序管理 - 编辑迁出文件的状态
@login_required
def edit_status(id):
    if request.method == 'GET':
        session["HTTP_REFERER"] = request.environ['HTTP_REFERER']

    checkout = RegisterCheckOutFile.query.filter_by(id=id).first_or_404()
    if current_user.can(Permission.WRITE) and request.method =='POST':
        fchkstatus = request.values.get('chkstatus')
        checkout.fchkstatus = fchkstatus
        checkout.fsystem = request.values.get('fsystem')
        checkout.fchkoutfile = request.values.get('fchkoutfile')
        if fchkstatus=='2-Check Out':
            checkout.fchkoutperson = current_user.name
            checkout.fchkoutdte = date.today()
        elif fchkstatus=='3-Check In':
            checkout.fchkinperson = current_user.name
            checkout.fchkindte = date.today()
        db.session.add(checkout)
        db.session.commit()
        return redirect(session.get("HTTP_REFERER"))
    return render_template('edit_post.html', checkouts=[checkout])


@main.route('/profiledelete/<int:id>')                  # 程序管理 - 删除这条迁出记录
@login_required
def user_delete(id):
    checkout=RegisterCheckOutFile.query.filter_by(id=id).first_or_404()
    if checkout.fchkstatus != '1-ASK':
        flash('只能删除状态为“ASK”的文件！')
    else:
        db.session.delete(checkout)
        db.session.commit()
    return redirect(url_for('.user', username=current_user.username))


@main.route('/feedback', methods=['GET', 'POST'])           # About - Feedback
@login_required
def feedback():
    feedbacks = Feedback.query.order_by(Feedback.fstatus,Feedback.fid.desc())

    if request.method=='POST':
        fcontent = request.values.get('fcontent')
        fd = Feedback(
            fcontent = fcontent,
            fstatus = '1',
            fentusr=current_user.name,
            fentdt=datetime.utcnow(),
            fupdteprg = 'new feedback'
        )
        db.session.add(fd)
        db.session.commit()
        flash("反馈添加成功！")
        return redirect(url_for('.feedback'))
    return render_template('feedback.html',feedbacks=feedbacks)


@main.route('/updatelog', methods=['GET', 'POST'])          # About - Update log
@login_required
def updatelog():
    updatelogs = Updatelog.query.order_by(Updatelog.fid.desc())

    if request.method=='POST':
        fcontent = request.values.get('fcontent')
        fversion = request.values.get('fversion')
        uplog = Updatelog(
            fcontent = fcontent,
            fversion = fversion,
            fentusr=current_user.name,
            fentdt=datetime.utcnow(),
            fupdteprg = 'new update log'
        )
        db.session.add(uplog)
        db.session.commit()
        flash("更新日志添加成功！")
        return redirect(url_for('.updatelog'))
    return render_template('updatelog.html',updatelogs=updatelogs)


@main.route('/about')                                       # About - About System
@login_required
def about():
    return render_template('about.html')


@main.route('/mcl/<name>')                  # 联络票管理 - 进入
@login_required
def mcl_index(name):
    user = User.query.filter_by(name=name).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Liaisonf.query.filter(Liaisonf.fassignedto==name).order_by(Liaisonf.fstatus, Liaisonf.fid.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_MCLPAGE'],
        error_out=False)
    liaisonfs = pagination.items
    return render_template('mcl_index.html',pagination=pagination, liaisonfs=liaisonfs, user=user)


@main.route('/pcl/pcl_list')                # 结合测试 - 进入
@login_required
def pcl_list():
    page = request.args.get('page', 1, type=int)
    pagination = Qahf.query.filter(Qahf.ftesttyp=='PCL').order_by(Qahf.fstatus,
                                                                             Qahf.fqahfid.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_MCLPAGE'],
        error_out=False)
    qahfs = pagination.items
    print(type(qahfs))
    for qahf in qahfs:
        print(type(qahf))
        # fnote = db.session.execute("select fnote from odrrlsf where fodrno = {}".format(qahf.fslipno),
        #                    bind=db.get_engine(current_app, bind='ManPower'))
        # fnote = list(fnote)[0][0]
        # if fnote is None:
        #     fnote = "******"
        fnote = "******"
        qahf.fnote = fnote
    return render_template('pcl_qa.html', pagination=pagination, qahfs=qahfs)


@main.route('/search/', methods=['GET', 'POST'])        # 程序管理 - Search
@login_required
def file_search():
    type = ''
    filter = []
    page = 1
    fsystem = session.get("fsystem")
    fapplicant = session.get("fapplicant")
    fslipno = session.get('fslipno')
    fchkoutobj = session.get('fchkoutobj')
    fchkstatus = session.get('fchkstatus')

    lasturl=session.get("HTTP_REFERER")
    if lasturl is not None:
        type = lasturl[22:28]
    if current_user.can(Permission.WRITE) and request.method == 'POST':
        if request.form["search"] == "notall":
            fsystem = request.values.get('fsystem')
            fapplicant = request.values.get('fapplicant')
            fslipno = request.values.get('fslipno')
            fchkoutobj = request.values.get('fchkoutobj')
            fchkstatus = request.values.get('fchkstatus')
            if len(fsystem)>0:
                filter.append(RegisterCheckOutFile.fsystem==fsystem)
            if len(fapplicant)>0:
                filter.append(RegisterCheckOutFile.fapplicant==fapplicant)
            if len(fslipno)>0:
                filter.append(RegisterCheckOutFile.fslipno==fslipno)
            if len(fchkoutobj)>0:
                filter.append(RegisterCheckOutFile.fchkoutobj==fchkoutobj)
            if len(fchkstatus)>0:
                filter.append(RegisterCheckOutFile.fchkstatus == fchkstatus)

            if fsystem !=session.get("fsystem") or fapplicant != session.get("fapplicant") or fslipno !=session['fslipno'] or session['fchkoutobj'] != fchkoutobj or session['fchkstatus'] != fchkstatus:
                page = 1
            else:
                page = request.args.get('page', 1, type=int)

            session['fsystem'] = fsystem
            session['fapplicant'] = fapplicant
            session['fslipno'] = fslipno
            session['fchkoutobj'] = fchkoutobj
            session['fchkstatus'] = fchkstatus
        else:
            session['fsystem'] = ""
            session['fapplicant'] = ""
            session['fslipno'] = ""
            session['fchkoutobj'] = ""
            session['fchkstatus'] = ""

        pagination = RegisterCheckOutFile.query.filter(*filter).order_by(RegisterCheckOutFile.fchkstatus ,RegisterCheckOutFile.id.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        checkouts = pagination.items
        return render_template('search.html', checkouts=checkouts,
                               pagination=pagination, fsystem=session.get("fsystem"),
                               fapplicant=session.get("fapplicant"), fslipno=session.get('fslipno'),
                               fchkoutobj=session.get('fchkoutobj'), fchkstatus=session.get('fchkstatus'))

    elif type=="search":
        fsystem = session.get("fsystem")
        fapplicant = session.get("fapplicant")
        fslipno = session.get('fslipno')
        fchkoutobj = session.get('fchkoutobj')
        fchkstatus = session.get('fchkstatus')

    if fsystem is not None:
        if len(fsystem) > 0 :
            filter.append(RegisterCheckOutFile.fsystem == fsystem)
    if fapplicant is not None:
        if len(fapplicant) > 0:
            filter.append(RegisterCheckOutFile.fapplicant == fapplicant)
    if fslipno is not None:
        if len(fslipno) > 0:
            filter.append(RegisterCheckOutFile.fslipno == fslipno)
    if fchkoutobj is not None:
        if len(fchkoutobj) > 0:
            filter.append(RegisterCheckOutFile.fchkoutobj == fchkoutobj)
    if fchkstatus is not None:
        if len(fchkstatus) > 0:
            filter.append(RegisterCheckOutFile.fchkstatus == fchkstatus)

    page = request.args.get('page', 1, type=int)
    pagination = RegisterCheckOutFile.query.filter(*filter).order_by(RegisterCheckOutFile.fchkstatus,
                                                                     RegisterCheckOutFile.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    checkouts = pagination.items
    return render_template('search.html', checkouts=checkouts,
                           pagination=pagination, fsystem=session.get("fsystem"),
                           fapplicant=session.get("fapplicant"), fslipno=session.get('fslipno'),
                           fchkoutobj=session.get('fchkoutobj'), fchkstatus=session.get('fchkstatus'))

    # return render_template('search.html')


@main.route('/sendemail/', methods=['GET', 'POST'])     # 程序管理 - Send Email
@login_required
def send_email():
    filter = []
    checkoutlists = []
    filter.append(RegisterCheckOutFile.fchkstatus == '1-ASK')
    filter.append(RegisterCheckOutFile.applicant_id == current_user.id)
    checkouts = RegisterCheckOutFile.query.filter(*filter).all()
    user = User.query.filter_by(username=current_user.username).first_or_404()
    recipients = Recipients.query.filter_by(applicant_id=user.id).all()
    if current_user.can(Permission.WRITE) and request.method=='POST':
        recipients = request.values.getlist('recipients')

        if len(checkouts)==0:
            flash('没有需要被迁出的程序！')
        elif len(recipients)==0:
            flash('请勾选收件人！')
        else:
            for checkout in checkouts:
                checkoutlists.append(checkout.fslipno)
            checkoutlists = set(checkoutlists)
            for checkoutlist in checkoutlists:
                filter2 = []
                filter2.append(RegisterCheckOutFile.fchkstatus == '1-ASK')
                filter2.append(RegisterCheckOutFile.applicant_id == current_user.id)
                filter2.append(RegisterCheckOutFile.fslipno == checkoutlist)
                checkouts2 = RegisterCheckOutFile.query.filter(*filter2).all()
                askchk_send_email(current_user.email, '程序迁出-'+current_user.name.strip()+'-'+checkoutlist,
                                  'auth/email/askcheckout', recipients=recipients ,user=current_user, checkouts=checkouts2)
            flash('程序迁出申请已经发送！')
            return redirect(url_for('.send_email',checkouts=checkouts, recipients=recipients))
    # return redirect(url_for('.send_email'))
    return render_template('sendemail.html', checkouts=checkouts, recipients=recipients)


@main.route('/recipients/', methods=['GET', 'POST'])
@login_required
def recipients():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    recipients = Recipients.query.filter_by(applicant_id=user.id).all()
    if current_user.can(Permission.WRITE) and request.method == 'POST':
        name=request.values.get('name')
        email=request.values.get('email')
        if len(name)==0 or len(email)==0:
            flash('姓名或者邮箱不可为空！')
        else:
            rec = Recipients(
                email=email,
                name=name,
                applicant_id=current_user.id
            )
            db.session.add(rec)
            db.session.commit()
            return redirect(url_for('.recipients'))
    return render_template('recipients.html', recipients=recipients)


@main.route('/user_rights/', methods=['GET', 'POST'])               # 首页 - User Rights - User Rights
@admin_required
@login_required
def user_rights():
    users = User.query.all()
    if current_user.can(Permission.WRITE) and request.method=='POST':
        name=request.values.get('name')
        role=request.values.get('role')
        if role=='User':
            roleid=1
        elif role=='Moderator':
            roleid=2
        else:
            roleid=3
        if name=='None':
            flash("姓名不可为None！")
            return redirect(url_for('.user_rights'))
        if len(name)<1:
            flash("姓名不可为None！")
            return redirect(url_for('.user_rights'))
        # users = User.query.filter(User.name==name).all()

        userids = db.session.execute("select id from `users` where name='{}'".format(name))
        userid = list(userids)[0][0]
        user = User.query.filter_by(id=userid).first_or_404()
        user.role_id=roleid
        db.session.add(user)
        db.session.commit()
        flash("权限修改完成！")
        return redirect(url_for('.user_rights'))
    return render_template('user_rights.html', users=users)
