-- Número de atendimentos na unidade APS por mês --

SELECT 
    aa.ano,
    aa.mes,
    aa.unidadeaps_id,
    COUNT(*) AS total_atendimentos
FROM 
    public.atendimento_agregado aa
GROUP BY 
    aa.ano,
    aa.mes,
    aa.unidadeaps_id
ORDER BY 
    aa.ano DESC, 
    aa.mes ASC, 
    total_atendimentos DESC;
