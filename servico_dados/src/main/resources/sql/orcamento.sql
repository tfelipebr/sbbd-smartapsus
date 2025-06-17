-- Orçamento da APS por atendimentos --

SELECT 
    ua.id AS unidadeaps_id,
    SUM(o.valor) AS orcamento_total,
    COUNT(a.id) AS total_atendimentos,
    ROUND(
        SUM(o.valor) / NULLIF(COUNT(a.id), 0), 
        2
    ) AS orcamento_por_atendimento
FROM 
    public.unidadeaps ua
LEFT JOIN 
    public.orcamento o ON o.unidadeaps_id = ua.id
LEFT JOIN 
    public.atendimento_agregado a ON a.unidadeaps_id = ua.id
GROUP BY 
    ua.id
ORDER BY 
    orcamento_por_atendimento DESC;
