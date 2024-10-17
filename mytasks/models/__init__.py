from flask import Flask
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL


app = Flask(__name__)
conexao = MySQL(app)

#configurações necessárias para usar o mysql:
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_mytasks'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

def get_conexao():
    return conexao.connection.cursor() #conexao com o banco

def commit_con():
    return conexao.connection.commit() #fazer commits



class User(UserMixin): #definindo a classe usuario
    _hash : str
    def __init__(self, **kwargs):
        self._id = None
        self._nome = None
        self._email = None
        self._senha = None  # Adicionei _email e _senha para completar

        if 'usu_id' in kwargs:  # ID do usuário
            self._id = kwargs['usu_id']
        if 'usu_nome' in kwargs:  # Nome do usuário
            self._nome = kwargs['usu_nome']
        if 'usu_email' in kwargs:  # Email do usuário
            self._email = kwargs['usu_email']
        if 'usu_senha' in kwargs:  # Senha (hash) do usuário
            self._senha = kwargs['usu_senha']

    def get_id(self):
        return str(self._id)

    
    # ----------métodos para manipular o banco--------------#
    def save(self):   #Salvar os dados  
        cursor = get_conexao() 
        cursor.execute("INSERT INTO tb_usuarios(usu_nome, usu_email, usu_senha) VALUES (%s, %s, %s)", (self._nome, self._email, self._senha))
        # salva o id no objeto recem salvo no banco
        self._id = cursor.lastrowid
        commit_con()
        cursor.close()
        return True
    
    @classmethod
    def get(cls,user_id): #pegar os dados de um usuário
        cursor = get_conexao()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            loaduser = User(nome=user['usu_nome'] , senha=user['usu_senha'])
            loaduser._id = user['usu_id']
            return loaduser
        else:
            return None
    
    @classmethod
    def exists(cls, email): #Verificar se usário existe
        cursor = get_conexao()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user: #melhorar esse if-else
            return True
        else:
            return False
    
    @classmethod
    def all(cls): #Pegar todos os dados
        cursor = get_conexao
        cursor.execute("SELECT usu_id, usu_nome, usu_email FROM tb_usuarios")
        users = cursor.fetchall()
        cursor.close()
        return users
    
    @classmethod
    def get_by_email(cls,email): #pegar usuário pelo nome
        cursor = get_conexao()
        cursor.execute("SELECT usu_id,usu_nome,usu_email,usu_senha FROM tb_usuarios WHERE usu_email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    
    
     # ----------métodos para manipular as tarefas--------------#

    @classmethod
    def save_task(cls, titulo, descricao, status, prioridade, data_criacao, data_limite, categoria, usuario):
        cursor = get_conexao()
        cursor.execute("""INSERT INTO tb_tarefas(tar_titulo, tar_descricao, tar_status, tar_prioridade, tar_data, tar_data_limite, tar_cat_id, tar_usu_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (titulo, descricao, status, prioridade, data_criacao, data_limite, categoria, usuario))
        commit_con()
        cursor.close()
        return True
    
    @classmethod
    def get_tasks(cls, id):
        cursor = get_conexao()
        cursor.execute("""SELECT * FROM tb_tarefas WHERE tar_usu_id = %s""", (id,))
        tarefas = cursor.fetchall()

        cursor.close()
        return tarefas