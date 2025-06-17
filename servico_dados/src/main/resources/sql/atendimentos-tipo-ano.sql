-- Total de atendimentos por tipo (por ano) --

SELECT 
   	aa.ano,
    aa.tipo,
    SUM(aa.quantidade) AS total_atendimentos
FROM 
    public.atendimento_agregado aa
GROUP BY 
    ano, aa.tipo
ORDER BY 
    ano DESC, total_atendimentos DESC;
