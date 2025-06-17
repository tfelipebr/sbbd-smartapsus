-- ORÇAMENTO PER CAPITA --

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
orcamento_por_cidade_ano AS (
    SELECT 
        ua.cidade_id,
        o.ano,
        SUM(o.valor) AS orcamento_total
    FROM 
        public.orcamento o
    JOIN 
        public.unidadeaps ua ON ua.id = o.unidadeaps_id
    GROUP BY 
        ua.cidade_id, o.ano
)

SELECT 
    c.id AS cidade_id,
    pca.ano,
    COALESCE(opca.orcamento_total, 0) AS orcamento_total,
    pca.populacao_total,
    ROUND(
        COALESCE(opca.orcamento_total, 0) / NULLIF(pca.populacao_total, 0), 
        2
    ) AS orcamento_per_capita
FROM 
    public.cidade c
JOIN 
    populacao_por_cidade_ano pca ON pca.cidade_id = c.id
LEFT JOIN 
    orcamento_por_cidade_ano opca 
    ON opca.cidade_id = c.id AND opca.ano = pca.ano
ORDER BY 
    pca.ano DESC, orcamento_per_capita DESC;

