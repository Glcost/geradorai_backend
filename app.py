# app.py (Parte 1)
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Importando o que criamos no outro arquivo:
from config import CURRICULO_SCHEMA, SYSTEM_INSTRUCTION

# Carrega as variáveis de ambiente e inicia o Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Inicializa o Flask
app = Flask(__name__)
CORS(app)

# app.py (Parte 2)

def generate_curriculo_ia(dados_usuario):
    
    contato_dados = dados_usuario.get('contato', {})
    email = contato_dados.get('email', '')
    telefone = contato_dados.get('telefone', '')
    
    
    
    
    conteudo_prompt = f"""Gere um currículo profissional e polido com base nos seguintes dados brutos fornecidos pelo usuário:
    
    - Nome Completo: {dados_usuario.get('nome_completo')}
    - Cargo Pretendido: {dados_usuario.get('cargo_pretendido')}
    - Localização: {dados_usuario.get('localizacao')}
    - E-mail: {email}
    - Telefone: {telefone}
    - Tecnologias/Competências: {dados_usuario.get('tecnologias')}
    - Escolaridade/Cursos: {dados_usuario.get('escolaridade')}
    - Projetos ou Experiências contadas pelo usuário: {dados_usuario.get('texto_experiencias')}"""
    
    # Faz a chamada para o modelo pedindo uma resposta estruturada em JSON
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", # Modelo otimizado para tarefas de geração de texto
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json", # Força a saída em formato JSON
            response_schema=CURRICULO_SCHEMA,       # Segue o esquema do config.py
        )
    )
    return response.text



# app.py (Parte 3)

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "message": "API Gerador de Curriculo funcionando!",
        "version": "1.0"
    }), 200

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    
   # Validação: Garante que os campos cruciais foram enviados
    campos_obrigatorios = ["nome_completo", "cargo_pretendido", "texto_experiencias"]
    if not data:
        return jsonify({
            "status": "error",
            "message": "Requisição inválida. Envie os dados do formulário."
        }), 400
        
    for campo in campos_obrigatorios:
        if not data.get(campo):
            return jsonify({
                "status": "error",
                "message": f"O campo '{campo}' é obrigatório para gerar o currículo."
            }), 400
    
    try:
        # Chama a função passando o dicionário completo de dados
        curriculo_json_string = generate_curriculo_ia(data)
        
        # Converte a resposta em objeto Python
        curriculo_estruturado = json.loads(curriculo_json_string)
        
        return jsonify({
            "status": "success",
            "dados_curriculo": curriculo_estruturado
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao otimizar o currículo com IA: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)