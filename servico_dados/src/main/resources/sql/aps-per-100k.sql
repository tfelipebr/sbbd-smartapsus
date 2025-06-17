-- Active: 1737565399754@@127.0.0.1@5435@postgis
-- Total de unidades APS per capita (resultado a cada 100000 pessoas) --

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
),
unidades_aps_por_cidade_ano AS (
    SELECT 
        ua.cidade_id,
        EXTRACT(YEAR FROM ua.data_criacao)::int AS ano,
        COUNT(ua.id) AS total_unidades
    FROM 
        public.unidadeaps ua
    GROUP BY 
        ua.cidade_id, EXTRACT(YEAR FROM ua.data_criacao)
)

SELECT 
    c.id AS cidade_id,
    pca.ano,
    COALESCE(uaca.total_unidades, 0) AS total_unidades,
    pca.populacao_total,
    ROUND(
        (COALESCE(uaca.total_unidades, 0)::numeric / NULLIF(pca.populacao_total, 0)) * 100000,
        2
    ) AS unidades_per_100k_habitantes
FROM 
    public.cidade c
JOIN 
    populacao_por_cidade_ano pca ON pca.cidade_id = c.id
LEFT JOIN 
    unidades_aps_por_cidade_ano uaca 
    ON uaca.cidade_id = c.id 
    AND uaca.ano = pca.ano
ORDER BY 
    pca.ano DESC, unidades_per_100k_habitantes DESC;


