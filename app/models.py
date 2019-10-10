from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from . import login_manager, db


class Permission:       # 权限常量
    FOLLOW = 1          # 关注用户
    COMMENT = 2         # 在他人的文章中发表评论
    WRITE = 4           # 写文章
    MODERATE = 8        # 管理他人发表的评论
    ADMIN = 16          # 管理员权限


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                              Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    groupid = db.Column(db.String(20))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    checkouts = db.relationship('RegisterCheckOutFile', backref='applicant', lazy='dynamic')
    # recipients = db.relationship('Recipients', backref='sender', lazy='dynamic')
    # slmsname = db.Column(db.String(10))  # for slms 2019-07-11

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()      # 将email为FLASKY_ADMIN的用户权限设为管理员
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()              # 默认角色权限
            # if self.email is not None and self.avatar_hash is None:
            #     self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):           # 密码生成
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):    # 密码校验
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):     # 生成一个确认令牌，有效期默认为一小时
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')    # 为指定的数据生成一个加密签名，然后再对数据和签名进行序列化，生成令牌字符串。

    def confirm(self, token):               # 检验令牌，如果检验通过，就把用户模型中新添加的confirmed 属性设为True
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))       # 解码令牌。检验签名和过期时间，如果都有效，则返回原始数据。
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # def generate_reset_token(self, expiration=3600):       # 生成密码重设的令牌
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'reset': self.id}).decode('utf-8')

    # @staticmethod
    # def reset_password(token, new_password):               # 密码重设
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except:
    #         return False
    #     user = User.query.get(data.get('reset'))
    #     if user is None:
    #         return False
    #     user.password = new_password
    #     db.session.add(user)
    #     return True

    # def generate_email_change_token(self, new_email, expiration=3600):      # 生成邮箱重设的令牌
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps(
    #         {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    # def change_email(self, token):                          # 邮箱重设
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except:
    #         return False
    #     if data.get('change_email') != self.id:
    #         return False
    #     new_email = data.get('new_email')
    #     if new_email is None:
    #         return False
    #     if self.query.filter_by(email=new_email).first() is not None:
    #         return False
    #     self.email = new_email
    #     self.avatar_hash = self.gravatar_hash()
    #     db.session.add(self)
    #     return True

    def can(self, perm):        # 判断用户是否具有什么权限
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):     # 判断是否为管理员
        return self.can(Permission.ADMIN)

    def ping(self):             # 刷新用户的最后访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # def gravatar_hash(self):
    #     return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):      # 生成Gravatar URL
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):        # 检查用户是否有指定的权限
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class RegisterCheckOutFile(db.Model):
    __tablename__ = 'movedoc'
    id = db.Column(db.Integer, primary_key=True)
    fregisterdte = db.Column(db.DateTime, index=True, default=date.today)
    fsystem = db.Column(db.String(6))
    fchkoutobj = db.Column(db.String(40))
    fapplicant = db.Column(db.String(20))
    fchkstatus = db.Column(db.String(20))
    fchkoutperson = db.Column(db.String(20))
    fchkoutdte = db.Column(db.DateTime, index=True, default=date.today)
    fchkoutfile = db.Column(db.String(40))
    fchkinperson = db.Column(db.String(20))
    fcomment = db.Column(db.String(100))
    fslipno = db.Column(db.String(20))
    fchkindte = db.Column(db.DateTime, index=True, default=date.today)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # fsendemail = db.Column(db.String(1), default='N')


class Feedback(db.Model):
    __tablename__ ='feedback'
    fid = db.Column(db.Integer, primary_key=True)
    fcontent = db.Column(db.Text)
    fstatus = db.Column(db.String(1))
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))


class Updatelog(db.Model):
    __tablename__ ='updatelog'
    fid = db.Column(db.Integer, primary_key=True)
    fcontent = db.Column(db.Text)
    fversion = db.Column(db.String(10))
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))


class Liaisonf(db.Model):
    __tablename__='liaisonf'
    fid = db.Column(db.Integer, primary_key=True)
    fsystemcd = db.Column(db.String(20))
    fprojectcd = db.Column(db.String(20))
    fslipno = db.Column(db.String(20))
    fsernum = db.Column(db.String(3))
    ftype = db.Column(db.String(10))
    fstatus = db.Column(db.String(15))
    fodrno = db.Column(db.String(20))
    fcreatedte = db.Column(db.DateTime)
    fcreateusr = db.Column(db.String(24))
    frequestor = db.Column(db.String(24))
    fassignedto = db.Column(db.String(24))
    fsubsystem = db.Column(db.String(100))
    fbrief = db.Column(db.Text)
    fcontent = db.Column(db.Text)
    fanalyse = db.Column(db.Text)
    fsolution = db.Column(db.Text)
    fassignedt = db.Column(db.DateTime)
    fplnstart = db.Column(db.DateTime)
    fplnend = db.Column(db.DateTime)
    factstart = db.Column(db.DateTime)
    factend = db.Column(db.DateTime)
    freleasedt = db.Column(db.DateTime)
    fischarge = db.Column(db.String(1))
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))
    freleaserpt = db.Column(db.Text)   #程序发布变更报告书
    # fsirno = db.Column(db.String(10))  #for slms


class Qahf(db.Model):
    __tablename__='qahf'
    fqahfid = db.Column(db.Integer, primary_key=True)
    ftesttyp = db.Column(db.String(6))
    fsystemcd = db.Column(db.String(20))
    fprojectcd = db.Column(db.String(20))
    fslipno = db.Column(db.String(20))
    fobjectid = db.Column(db.String(50))
    fobjectnm = db.Column(db.String(50))
    fcreatedte = db.Column(db.DateTime)
    fcreateusr = db.Column(db.String(24))
    fstatus = db.Column(db.String(1))
    fauditdte =db.Column(db.DateTime)
    fauditor = db.Column(db.String(24))
    ftestdte = db.Column(db.DateTime)
    ftestusr = db.Column(db.String(24))
    fconfirmdte = db.Column(db.DateTime)
    fconfirmusr = db.Column(db.String(24))
    fttlcodelines = db.Column(db.Numeric, default=0)
    fmodifiedlines = db.Column(db.Numeric, default=0)    #2019.06.19 将这三个字段的默认值设置为 0
    fcomplexity = db.Column(db.DECIMAL(10,1), default=0) #该字段应保留一位小数
    fnote = db.Column(db.Text)
    freviewcode = db.Column(db.Text)
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))
    # fobjmodification = db.Column(db.Text)   #2019.7.31 MCL对象修改详情


class Qadf(db.Model):
    __tablename = 'qadf'
    fqadfid = db.Column(db.Integer, primary_key=True)
    fclass1 = db.Column(db.String(20))
    fclass2 = db.Column(db.String(20))
    ftag = db.Column(db.Text)
    fregression = db.Column(db.String(1))
    fcontent_text = db.Column(db.Text)
    fcontent= db.Column(db.Text)
    ftestdte= db.Column(db.DateTime)
    ftestusr = db.Column(db.String(24))
    fimpdte = db.Column(db.DateTime)
    fimpusr = db.Column(db.String(24)) #fimpdte、fimpusr为测试用例的添加时间和添加者（2019-05-13）
    fisplan = db.Column(db.String(1))
    fapproval = db.Column(db.String(1))
    fresult = db.Column(db.String(10))
    fnote = db.Column(db.Text)
    fsuggestion = db.Column(db.Text)
    fdtlobj = db.Column(db.Text)
    fattachment = db.Column(db.Text)
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))
    fqahfid = db.Column(db.Integer, db.ForeignKey('qahf.fqahfid'))
    fngcnt = db.Column(db.Integer, default=0)   #该字段用来记录当前测试case总共NG多少次
    flastapproveid = db.Column(db.Integer, default=0)  #该字段为确认NG后，对应Qadfproof的ID
    flastsubmitid = db.Column(db.Integer, default=0)   #该字段为提交后，对应Qadfproof的ID


class Qadfproof(db.Model):
    __tablename__ = 'qadfproof'
    fqadfproofid = db.Column(db.Integer, primary_key=True)
    fcontent_text = db.Column(db.Text)
    forifilename = db.Column(db.String(50))  #2019/08/16 add 用来保存上传的测试文档的原始名称，下载时用
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fqadfid = db.Column(db.Integer, db.ForeignKey('qadf.fqadfid'))


class Systemm(db.Model):
    __tablename__='systemm'
    fsystemcd = db.Column(db.String(20), primary_key=True)
    fsystemnm = db.Column(db.String(50))
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))


class Projectm(db.Model):
    __tablename__='projectm'
    fprojectcd = db.Column(db.String(20), primary_key=True)
    fprojectnm = db.Column(db.String(50))
    fentdt = db.Column(db.DateTime)
    fentusr = db.Column(db.String(24))
    fupdtedt = db.Column(db.DateTime)
    fupdteusr = db.Column(db.String(24))
    fupdteprg = db.Column(db.String(110))
    # fprojectsn = db.Column(db.String(10))
    # fautoflg = db.Column(db.String(1))


class Recipients(db.Model):
    __tablename__='recipients'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    name = db.Column(db.String(64))
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'))


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
