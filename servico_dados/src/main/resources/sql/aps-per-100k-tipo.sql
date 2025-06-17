-- Total de unidades APS (por tipo) per capita --

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
unidades_aps_por_cidade_ano_tipo AS (
    SELECT 
        ua.cidade_id,
        EXTRACT(YEAR FROM ua.data_criacao)::int AS ano,
        ua.tipo_unidade_id,
        COUNT(ua.id) AS total_unidades
    FROM 
        public.unidadeaps ua
    GROUP BY 
        ua.cidade_id, ua.tipo_unidade_id, EXTRACT(YEAR FROM ua.data_criacao)
)

SELECT 
    c.id AS cidade_id,
    pca.ano,
    tu.nome AS tipo_unidade_nome,
    COALESCE(uapt.total_unidades, 0) AS total_unidades,
    pca.populacao_total,
    ROUND(
        (COALESCE(uapt.total_unidades, 0)::numeric / NULLIF(pca.populacao_total, 0)) * 100000,
        2
    ) AS unidades_per_100k_habitantes
FROM 
    public.cidade c
JOIN 
    populacao_por_cidade_ano pca ON pca.cidade_id = c.id
LEFT JOIN 
    unidades_aps_por_cidade_ano_tipo uapt 
    ON uapt.cidade_id = c.id 
    AND uapt.ano = pca.ano
LEFT JOIN 
    public.tipo_unidade tu 
    ON tu.id = uapt.tipo_unidade_id
ORDER BY 
    pca.ano DESC, unidades_per_100k_habitantes DESC;

