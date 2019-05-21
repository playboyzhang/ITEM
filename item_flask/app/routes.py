#导入模板模块
from flask import render_template,flash,redirect,url_for,request
from app import app,db
from flask_login import current_user,login_user,logout_user,login_required
from app.models import User
from app.forms import LoginForm,RegistrationForm,EditProfileForm
from werkzeug.urls import url_parse
from datetime import  datetime
@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username':'boy'}
    #将需要展示的数据传递给模板进行显示
    posts = [
        {
            'author': {'username': 'hu'},
            'body': '这是模板模块中的循环例子～1'
        },
        {
            'author': {'username': 'shuangli'},
            'body': '这是模板模块中的循环例子～2'
        }
    ]
    return render_template('index.html',title='我的',user=user,posts =posts)

@app.route('/login',methods=['GET','POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('无效的用户或密码')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        # 如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # 综上，登录后要么重定向至跳转前的页面，要么跳转至首页
        return redirect(next_page)
        # return redirect(url_for('index'))
    return render_template('login.html',title='登录',form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register',methods=['GET','POST'])
def register():
    #判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜你注册成功！')
        return redirect(url_for('login'))
    return render_template('register.html',title='注册',form=form)



@app.route('/usr/<username>')
@login_required
def user(username):

    user = User.query.filter_by(username=username).first_or_404()

    posts = [
        {'author':user,'body':'测试Post#1号'},
        {'author':user,'body':'测试Post#2号'}
    ]

    return render_template('user.html',user=user,posts=posts)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('你的提交已变更.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='个人资料编辑',
                           form=form)

