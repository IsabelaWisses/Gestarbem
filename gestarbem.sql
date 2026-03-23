DROP DATABASE IF EXISTS gestarbem;
CREATE DATABASE gestarbem;
USE gestarbem;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    semana_gestacional INT,
    foto VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE users
ADD COLUMN humor VARCHAR(30) NULL AFTER foto;
ALTER TABLE users
ADD COLUMN tipo_sanguineo VARCHAR(5) NULL AFTER semana_gestacional,
ADD COLUMN idade INT NULL AFTER tipo_sanguineo,
ADD COLUMN problemas_saude TEXT NULL AFTER idade,
ADD COLUMN alergias TEXT NULL AFTER problemas_saude,
ADD COLUMN medicamentos TEXT NULL AFTER alergias,
ADD COLUMN contato_emergencia VARCHAR(120) NULL AFTER medicamentos,
ADD COLUMN info_importantes TEXT NULL AFTER contato_emergencia;


CREATE TABLE lists (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  titulo VARCHAR(120) NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (user_id)
);

CREATE TABLE list_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  list_id INT NOT NULL,
  texto VARCHAR(255) NOT NULL,
  concluido BOOLEAN NOT NULL DEFAULT 0,
  ordem INT DEFAULT 0,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE,
  INDEX (list_id)
);

CREATE TABLE appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  titulo VARCHAR(120) NOT NULL,
  tipo ENUM('consulta','exame','lembrete') NOT NULL,
  data DATE NOT NULL,
  hora TIME NULL,
  observacao TEXT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (user_id, data)
);

CREATE TABLE documents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  tipo VARCHAR(80) NOT NULL,
  nome_original VARCHAR(255) NOT NULL,
  arquivo_url VARCHAR(255) NOT NULL,
  mime_type VARCHAR(80),
  tamanho_bytes INT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (user_id, tipo)
);

select*from users;
INSERT INTO users (
    nome,
    email,
    senha,
    telefone,
    semana_gestacional,
    tipo_sanguineo,
    idade,
    problemas_saude,
    alergias,
    medicamentos,
    contato_emergencia,
    info_importantes,
    foto,
    humor
) VALUES (
    'Gestante 123',
    'gestante123@gmail.com',
    '123456',
    '(31) 99999-0000',
    24,
    'O+',
    22,
    'Nenhum problema de saúde relevante',
    'Alergia a dipirona',
    'Ácido fólico e vitamina pré-natal',
    'Mãe - (31) 98888-0000',
    'Gestação acompanhada regularmente. Em caso de emergência, avisar o contato principal.',
    NULL,
    'feliz'
);
USE gestarbem;

SELECT id, nome, email, senha
FROM users
WHERE email = 'gestante123@gmail.com';