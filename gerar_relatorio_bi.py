import json
import csv
import os
from datetime import datetime

# Define os arquivos de entrada e saída
ARQUIVO_JSON = 'relatorio_validacao.json'
ARQUIVO_CSV = f'dashboard_bi_{datetime.now().strftime("%Y%m%d")}.csv'

def converter_para_csv():
    if not os.path.exists(ARQUIVO_JSON):
        print("❌ Arquivo JSON não encontrado. Execute a validação primeiro.")
        return

    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Verifica se a chave 'results' existe no JSON gerado pelo seu validador
    resultados = dados.get('results', [])
    if not resultados:
        print("⚠️ Nenhum dado para processar no JSON.")
        return

    # Cria o CSV para o BI
    with open(ARQUIVO_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        colunas = ['arquivo', 'valido', 'erros_quantidade', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=colunas)
        
        writer.writeheader()
        for item in resultados:
            writer.writerow({
                'arquivo': item.get('file', 'Desconhecido'),
                'valido': 'SIM' if item.get('valid') else 'NÃO',
                'erros_quantidade': len(item.get('errors', [])),
                'timestamp': dados.get('generated_at', datetime.now().isoformat())
            })
    
    print(f"✅ Arquivo para Business Intelligence gerado com sucesso: {ARQUIVO_CSV}")

if __name__ == "__main__":
    converter_para_csv()