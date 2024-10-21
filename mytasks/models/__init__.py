from flask import Flask
from flask_login import UserMixin, current_user
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
        cursor = get_conexao()
        cursor.execute("SELECT usu_id, usu_nome, usu_email FROM tb_usuarios")
        users = cursor.fetchall()
        cursor.close()
        return users
    
    @classmethod
    def get_by_email(cls,email): #pegar usuário pelo email
        cursor = get_conexao()
        cursor.execute("SELECT usu_id,usu_nome,usu_email,usu_senha FROM tb_usuarios WHERE usu_email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    @classmethod
    def get_username(cls):
        if current_user.is_authenticated:
            return current_user._nome

    
    
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
        cursor.execute("""SELECT tar_id, tar_titulo, tar_descricao, tar_status, cat_categoria, tar_prioridade, tar_data, tar_data_limite FROM tb_tarefas JOIN tb_categorias ON tar_cat_id=cat_id WHERE tar_usu_id = %s""", (id,))
        tarefas = cursor.fetchall()

        cursor.close()
        return tarefas
        
    @classmethod
    def get_filtros(cls, id, status=None, prioridade=None, categoria=None, data_limite=None, data_criacao=None, palavra = None):
        cursor = get_conexao()

        # Query base
        query = "SELECT * FROM tb_tarefas WHERE tar_usu_id = %s"
        params = [id] #lista com os parametros

        # Condições opcionais
        if status: #se tiver sido passado algum status
            query += " AND tar_status = %s" #adiciona à query
            params.append(status) #adiciona o parametro a lista de parâmetros
        if prioridade:
            query += " AND tar_prioridade = %s"
            params.append(prioridade)
        if categoria:
            query += " AND tar_cat_id= %s"
            params.append(categoria)
        if data_limite:
            query += " AND tar_data_limite = %s"
            params.append(data_limite)
        if data_criacao:
            query += " AND tar_data = %s"
            params.append(data_criacao)

        cursor.execute(query, params)
        tarefas = cursor.fetchall()
        cursor.close()
        return tarefas
        
    @classmethod
    def get_task_by_id(cls, task_id): #pega a tarefa pelo id
        cursor = get_conexao()
        cursor.execute("SELECT * FROM tb_tarefas WHERE tar_id = %s", (task_id,))
        tarefa = cursor.fetchone()
        cursor.close()
        return tarefa

    
    @classmethod
    def update_task(cls, task_id, titulo, descricao, status, prioridade, categoria, data_limite):
        cursor = get_conexao()
        try:
            cursor.execute("""UPDATE tb_tarefas 
                              SET tar_titulo = %s, tar_descricao = %s, tar_status = %s, tar_prioridade = %s, tar_cat_id = %s, tar_data_limite = %s 
                              WHERE tar_id = %s""",
                           (titulo, descricao, status, prioridade, categoria, data_limite, task_id))
            commit_con()
        except:
            print(f"Erro ao atualizar tarefa")
            return False
        finally:
            cursor.close()
        return True

        
    @classmethod
    def delete_task(cls, task_id):
        cursor = get_conexao()
        try:
            cursor.execute("DELETE FROM tb_tarefas WHERE tar_id = %s", (task_id,))
            commit_con()
        except Exception as e:
            print(f"Erro ao excluir tarefa: {e}")
            return False
        finally:
            cursor.close()
        return True
    
    @classmethod
    def busca_task(cls,chaves):
        cursor = get_conexao()
        cursor.execute("""
        SELECT * FROM tb_tarefas WHERE  tar_descricao LIKE %s
        """, )

        busca = cursor.fetchall()
        cursor.close()

        return busca
