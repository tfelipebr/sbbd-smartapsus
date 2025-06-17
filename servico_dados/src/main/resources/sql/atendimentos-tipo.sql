-- Total de atendimentos por tipo --

SELECT 
    aa.tipo,
    SUM(aa.quantidade) AS total_atendimentos
FROM 
    public.atendimento_agregado aa
GROUP BY 
    aa.tipo
ORDER BY 
    total_atendimentos DESC;
