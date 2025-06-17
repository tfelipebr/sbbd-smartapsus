-- DENSIDADE DE PROFISSIONAIS (qtd de profissionais de saúde a cadas 100000 pessoas) --

WITH 
populacao_por_cidade_ano AS (
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
    COUNT(DISTINCT te.profissional_id) AS total_profissionais,
    pca.populacao_total,
    ROUND(
        (COUNT(DISTINCT te.profissional_id)::numeric / NULLIF(pca.populacao_total, 0)) * 100000, 
        2
    ) AS densidade_profissionais
FROM 
    public.cidade c
JOIN 
    public.unidadeaps ua ON ua.cidade_id = c.id
JOIN 
    public.trabalha_em te ON te.unidadeaps_id = ua.id
JOIN 
    populacao_por_cidade_ano pca ON pca.cidade_id = c.id
WHERE 
    te.data_inicio <= (pca.ano || '-12-31')::date
    AND (te.data_fim IS NULL OR te.data_fim >= (pca.ano || '-01-01')::date)
GROUP BY 
    c.id, pca.ano, pca.populacao_total
ORDER BY 
    pca.ano DESC, densidade_profissionais DESC;



