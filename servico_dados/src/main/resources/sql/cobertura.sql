-- Cobertura populacional estimada -- 

-- equipes * 3000 / população

WITH populacao_por_cidade_ano AS (
    SELECT 
        s.cidade_id,
        e.ano,
        SUM(e.valor::numeric) AS populacao_total
    FROM 
        public.setor_censitario s
    JOIN 
        public.estatistica e ON e.area_estudo_id = s.id
    WHERE 
        e.metrica_id = 1
    GROUP BY 
        s.cidade_id, e.ano
)

SELECT 
    c.id AS cidade_id,
    pca.ano,
    pca.populacao_total,
    ROUND(
--    TODO
        1000 / NULLIF(pca.populacao_total, 0), 
        6
    ) AS resultado
FROM 
    public.cidade c
JOIN 
    populacao_por_cidade_ano pca ON pca.cidade_id = c.id
ORDER BY 
    pca.ano DESC, resultado DESC;
