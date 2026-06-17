@echo off
echo ========================================================
echo   INICIANDO ROTINA DE QUALIDADE DE DADOS (EDGE COMPUTING)
echo ========================================================
echo.

echo 1. Validando lotes de telemetria dos sensores...
python validaXML.py --batch ./exemplos_sensores/ --xsd ./exemplos_sensores/schema_telemetria.xsd -o relatorio_validacao.json --quiet

echo.
echo 2. Exportando dados consolidados para o BI...
python gerar_relatorio_bi.py

echo.
echo ========================================================
echo   ROTINA FINALIZADA! ABRA O ARQUIVO .CSV NO EXCEL/POWER BI
echo ========================================================
pause