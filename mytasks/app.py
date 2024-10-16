from flask import Flask, session, request, render_template, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app) #Configura app para trabalhar junto com flask-login

#configurações necessárias para usar o mysql:
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kauan123'
app.config['MYSQL_DB'] = 'db_mytasks'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
conexao = MySQL(app)

#chave para critografia de cookies na sessão
app.config['SECRET_KEY'] = 'supermegadificil'

@login_manager.user_loader #Carregar usuário logado
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/cadastro', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('pages/register.html')
    else:
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        if not User.exists(nome): #Se o usuário não tiver cadastro
            user = User(usu_nome = nome, usu_email = email, usu_senha = senha)
            user.save()
            # Logar o usuário depois de cadastrar
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Esse usuário já existe! <a href='" + url_for('index') + "'>Faça Login</a>", 'error')
            return redirect(url_for('register'))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST': #metodo post
        email = request.form['email']
        senha = request.form['senha']
        user = User.get_by_email(email)

        if user is None: # Se o login falhar
            flash("Usuário não cadastrado. <a href='" + url_for('register') + "'>Cadastre-se aqui</a>", "error")
            return redirect(url_for('login')) 
        if check_password_hash(user['usu_senha'], senha):  # Se o usuário for encontrado
                login_user(User.get(user['usu_id'])) 
                return redirect(url_for('dash'))  # Redireciona para a página de filmes
        flash("Senha Incorreta", "error")
        return redirect(url_for('login'))
    
    else:
        return render_template('pages/login.html')
 
@app.route('/inicio', methods = ['POST', 'GET'])
@login_required
def dash():
    return render_template('pages/dash.html')

@app.route('/novatask', methods = ['POST', 'GET'])
@login_required
def newtask():
    if request.method == 'GET':
        return render_template('pages/newtask.html')
    else:
        pass
