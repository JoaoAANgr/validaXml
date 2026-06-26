@echo off
echo Validando XMLs da pasta exemplos...
python validaXML.py --batch ./exemplos/ --xsd ./exemplos/schema_pdv.xsd -o relatorio_validacao.json --quiet

echo Exportando para CSV...
python gerar_relatorio_bi.py

echo Pronto. Abra o arquivo .csv no Excel ou Power BI.
pause
