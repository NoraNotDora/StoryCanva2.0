from flask import Flask, render_template

app = Flask(__name__)

# 基础路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/achievement')
def achievement():
    return render_template('achievement.html')

@app.route('/community')
def community():
    return render_template('community.html')






























@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

# 将debug判断移到路由注册之后
if __name__ == '__main__':
    # 先设置debug模式
    app.debug = True
    
    # 注册测试路由（仅在开发模式）
    if app.debug:
        @app.route('/base')
        def show_base_template():
            return render_template('base.html')
    
    app.run() 