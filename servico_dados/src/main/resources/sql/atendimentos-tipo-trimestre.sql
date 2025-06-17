-- Total de atendimentos por tipo (por trimestre)--

SELECT 
    aa.ano,
    CASE 
        WHEN aa.mes BETWEEN 1 AND 3 THEN 1
        WHEN aa.mes BETWEEN 4 AND 6 THEN 2
        WHEN aa.mes BETWEEN 7 AND 9 THEN 3
        WHEN aa.mes BETWEEN 10 AND 12 THEN 4
    END AS trimestre,
    aa.tipo,
    SUM(aa.quantidade) AS total_atendimentos
FROM 
    public.atendimento_agregado aa
GROUP BY 
    aa.ano,
    trimestre,
    aa.tipo
ORDER BY 
    aa.ano DESC, 
    trimestre ASC, 
    total_atendimentos DESC;
