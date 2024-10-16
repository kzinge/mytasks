CREATE DATABASE db_mytasks;
USE db_mytasks;

CREATE TABLE tb_usuarios(
usu_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
usu_nome VARCHAR(90) NOT NULL,
usu_senha VARCHAR(255) NOT NULL,
usu_email VARCHAR(100) NOT NULL
);

CREATE TABLE tb_categorias(
cat_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
cat_categoria VARCHAR(50) NOT NULL
);

INSERT INTO tb_categorias(cat_categoria)
VALUES ('Trabalho'), ('Estudo'), ('Pessoal');

CREATE TABLE tb_tarefas(
tar_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
tar_titulo VARCHAR(100),
tar_descricao TEXT NOT NULL,
tar_status ENUM('Concluída', 'Pendente', 'Fazendo') NOT NULL,
tar_prioridade ENUM('Alta', 'Média', 'Baixa'),
tar_data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
tar_data_limite DATE NOT NULL,
tar_data_conlusao TIMESTAMP NULL,
tar_cat_id INT NOT NULL,
tar_usu_id INT NOT NULL,
FOREIGN KEY (tar_cat_id) REFERENCES tb_categorias(cat_id),
FOREIGN KEY (tar_usu_id) REFERENCES tb_usuarios(usu_id)
);
