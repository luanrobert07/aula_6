DROP TABLE IF EXISTS professores;

CREATE TABLE professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    sala_de_atendimento VARCHAR(50) NOT NULL
);

INSERT INTO professores (nome, email, sala_de_atendimento) VALUES 
('Professor 1', 'professor_1@example.com', 'Sala 101'),
('Professor 2', 'professor_2@example.com', 'Sala 102');