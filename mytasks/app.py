from flask import Flask, session, request, render_template, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app) #Configura app para trabalhar junto com flask-login

#configurações necessárias para usar o mysql:
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
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
        if not User.exists(email): #Se o usuário não tiver cadastro
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
   if request.method == 'POST':
        status = request.form.get('status') or None #tenta pegar o valor, se n tiver status=None
        prioridade = request.form.get('prioridade') or None
        categoria = request.form.get('categoria') or None
        data_limite_srt = request.form.get('data-limite') or None
        data_criacao_srt = request.form.get('data-criacao') or None
        
        data_limite = datetime.strptime(data_limite_srt, '%Y-%m-%d').date() if data_limite_srt else None
        data_criacao = datetime.strptime(data_criacao_srt, '%Y-%m-%d').date() if data_criacao_srt else None

        tarefas = User.get_filtros(current_user._id, status=status, prioridade=prioridade, categoria=categoria, data_limite=data_limite, data_criacao=data_criacao)
    else:
        tarefas = User.get_tasks(current_user._id)
    
    nome = current_user._nome
    return render_template('pages/dash.html', tarefas=tarefas, nome=nome)

@app.route('/novatask', methods = ['POST', 'GET'])
@login_required
def newtask():
    if request.method == 'GET':
        return render_template('pages/newtask.html')
    else:
        titulo = request.form['titulo']
        descricao = request.form['conteudo']
        status = request.form['status']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        data_limite_srt = request.form['data-limite']
        data_limite = datetime.strptime(data_limite_srt, '%Y-%m-%d').date()
        data_criacao = datetime.now()

        if User.save_task(titulo, descricao, status, prioridade, data_criacao, data_limite, categoria, current_user._id):
            return redirect(url_for('dash'))
        else:
            return "Erro ao cadastrar tarefa."

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
