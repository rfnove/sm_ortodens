
DROP TABLE IF EXISTS feedbacks CASCADE;

CREATE TABLE feedbacks(
    id_feddback SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NUll,
    nota INTEGER NOT NULL,
    comentario VARCHAR(200) NOT NULL,
    data_resposta DATE NOT NULL
);

SELECT * FROM FEEDBACKS;
