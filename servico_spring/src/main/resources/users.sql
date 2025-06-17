------------------------------------------
-- INSERIR OS TIPOS DE USUÁRIOS
------------------------------------------

-- ADMIN
INSERT INTO public.tipo_usuario (nome)
SELECT 'ROLE_ADMIN'
WHERE NOT EXISTS (
    SELECT 1 FROM public.tipo_usuario WHERE nome = 'ROLE_ADMIN'
);

-- GESTOR ESTADUAL
INSERT INTO public.tipo_usuario (nome)
SELECT 'ROLE_GESTOR_ESTADUAL'
WHERE NOT EXISTS (
    SELECT 1 FROM public.tipo_usuario WHERE nome = 'ROLE_GESTOR_ESTADUAL'
);

-- GESTOR MUNICIPAL
INSERT INTO public.tipo_usuario (nome)
SELECT 'ROLE_GESTOR_MUNICIPAL'
WHERE NOT EXISTS (
    SELECT 1 FROM public.tipo_usuario WHERE nome = 'ROLE_GESTOR_MUNICIPAL'
);

-- FUNCIONARIO ESTADUAL
INSERT INTO public.tipo_usuario (nome)
SELECT 'ROLE_FUNCIONARIO_ESTADUAL'
WHERE NOT EXISTS (
    SELECT 1 FROM public.tipo_usuario WHERE nome = 'ROLE_FUNCIONARIO_ESTADUAL'
);

-- FUNCIONARIO MUNICIPAL
INSERT INTO public.tipo_usuario (nome)
SELECT 'ROLE_FUNCIONARIO_MUNICIPAL'
WHERE NOT EXISTS (
    SELECT 1 FROM public.tipo_usuario WHERE nome = 'ROLE_FUNCIONARIO_MUNICIPAL'
);

-- PESQUISADOR
INSERT INTO public.tipo_usuario (nome)
SELECT 'ROLE_PESQUISADOR'
WHERE NOT EXISTS (
    SELECT 1 FROM public.tipo_usuario WHERE nome = 'ROLE_PESQUISADOR'
);

------------------------------------------
-- INSERIR OS USUÁRIOS
------------------------------------------

-- usuário: admin@smartapsus.com
-- senha: 1234
INSERT INTO public.usuario
(ativo, area_estudo_id, data_cadastro, tipo_usuario_id, cargo, email, funcao, nome, senha)
VALUES(true, NULL, '2024-05-28 00:21:41.998', 
    (SELECT id FROM public.tipo_usuario WHERE nome = 'ROLE_ADMIN'), 
    'Admininistrador', 'admin@smartapsus.com.br', 'Administrador', 'Administrativa', '{bcrypt}$2a$04$8w5iQPBGAbXBFI8yIb.W/O.d7hvgQigmM5Ezuqv6ZpITPfIpldbCW');
	
    
-- usuário: pesquisador@smartapsus.com.br
-- senha: 1234
INSERT INTO public.usuario
(ativo, area_estudo_id, data_cadastro, tipo_usuario_id, cargo, email, funcao, nome, senha)
VALUES(true, NULL, '2024-05-28 00:21:41.998', 
    (SELECT id FROM public.tipo_usuario WHERE nome = 'ROLE_PESQUISADOR'), 
    'Pesquisador', 'pesquisador@smartapsus.com.br', 'Pesquisador', 'Carl', '{bcrypt}$2a$04$8w5iQPBGAbXBFI8yIb.W/O.d7hvgQigmM5Ezuqv6ZpITPfIpldbCW');
            
    
---- usuário: gestore@smartapsus.com
---- senha: 1234
--INSERT INTO public.usuario
--(ativo, area_estudo_id, data_cadastro, tipo_usuario_id, cargo, email, funcao, nome, senha)
--VALUES(true, NULL, '2024-05-28 00:21:41.998', 
--    (SELECT id FROM public.tipo_usuario WHERE nome = 'ROLE_GESTOR_ESTADUAL'), 
--    'Gestor Estadual', 'gestore@smartapsus.com.br', 'Administrativa', 'Paul', '{bcrypt}$2a$04$8w5iQPBGAbXBFI8yIb.W/O.d7hvgQigmM5Ezuqv6ZpITPfIpldbCW');
    
    
---- usuário: gestorm@smartapsus.com
---- senha: 1234
--INSERT INTO public.usuario
--(ativo, area_estudo_id, data_cadastro, tipo_usuario_id, cargo, email, funcao, nome, senha)
--VALUES(true, NULL, '2024-05-28 00:21:41.998', 
--    (SELECT id FROM public.tipo_usuario WHERE nome = 'ROLE_GESTOR_MUNICIPAL'), 
--    'Gestor Municipal', 'gestorm@smartapsus.com.br', 'Administrativa', 'Robert', '{bcrypt}$2a$04$8w5iQPBGAbXBFI8yIb.W/O.d7hvgQigmM5Ezuqv6ZpITPfIpldbCW');
    
    
---- usuário: funcionarioe@smartapsus.com.br
---- senha: 1234
--INSERT INTO public.usuario
--(ativo, area_estudo_id, data_cadastro, tipo_usuario_id, cargo, email, funcao, nome, senha)
--VALUES(true, NULL, '2024-05-28 00:21:41.998', 
--    (SELECT id FROM public.tipo_usuario WHERE nome = 'ROLE_FUNCIONARIO_ESTADUAL'), 
--    'Funcionário Estadual', 'funcionarioe@smartapsus.com.br', 'Operacional', 'Bryan', '{bcrypt}$2a$04$8w5iQPBGAbXBFI8yIb.W/O.d7hvgQigmM5Ezuqv6ZpITPfIpldbCW');
    
    
---- usuário: funcionariom@smartapsus.com.br
---- senha: 1234
--INSERT INTO public.usuario
--(ativo, area_estudo_id, data_cadastro, tipo_usuario_id, cargo, email, funcao, nome, senha)
--VALUES(true, NULL, '2024-05-28 00:21:41.998', 
--    (SELECT id FROM public.tipo_usuario WHERE nome = 'ROLE_FUNCIONARIO_MUNICIPAL'), 
--    'Funcionário Municipal', 'funcionariom@smartapsus.com.br', 'Operacional', 'John', '{bcrypt}$2a$04$8w5iQPBGAbXBFI8yIb.W/O.d7hvgQigmM5Ezuqv6ZpITPfIpldbCW');
   
    
    
    
    
    
    
    
    
    