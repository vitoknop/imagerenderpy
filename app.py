from flask import Flask, render_template, request, send_file, jsonify
import os
import zipfile
import json
import base64

from flask_cors import CORS

host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', 5000))

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
CORS(app)

# Rotas para páginas HTML
@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/home')
def home():
    return render_template('pages/index.html')

@app.route('/categorias')
def categorias():
    return render_template('pages/categorias.html')

@app.route('/categoria')
def categoria():
    # get request vars
    categoria_caminho = request.args.get('categoria')
    
    titulo = ""
    doencas= []
    
    if categoria_caminho:
        pastas_doencas = os.listdir(categoria_caminho)
        
        for doenca in pastas_doencas:
            doenca_caminho = os.path.join(categoria_caminho, doenca)
            if os.path.isdir(doenca_caminho):
                for arquivo in os.listdir(doenca_caminho):
                    if arquivo.endswith('.json'):
                        arquivo_caminho = os.path.join(doenca_caminho, arquivo)
                        with open(arquivo_caminho, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            data['caminho'] = doenca_caminho
                            doencas.append(data)

    titulo_path = os.path.join(categoria_caminho, 'index.json')
    with open(titulo_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        titulo = data['titulo']
    
    return render_template('pages/categoria.html', doencas=doencas, titulo=titulo)

@app.route('/doenca')
def doencas():
    doenca = {}
    imagens_base64 = []
    
    doenca_caminho = request.args.get('doenca')
    
    info_doenca = os.path.join(doenca_caminho, 'index.json')
    
    with open(info_doenca, 'r', encoding='utf-8') as f:
        data = json.load(f)
        doenca = data
        for imagem in data['imagens']:
            arquivos = imagem['arquivo']
            imagem1, imagem2 = arquivos
            imagem1_caminho = os.path.join(doenca_caminho, imagem1)
            imagem2_caminho = os.path.join(doenca_caminho, imagem2)
            with open(imagem1_caminho, 'rb') as f1:
                with open(imagem2_caminho, 'rb') as f2:
                    imagem1_base64 = base64.b64encode(f1.read()).decode('utf-8')
                    imagem2_base64 = base64.b64encode(f2.read()).decode('utf-8')
                    imagens_base64.append([imagem1_base64, imagem2_base64])
        
    
    return render_template('pages/doenca.html', doenca=doenca, imagens_base64=imagens_base64)

# Rotas para dados
@app.route('/api/get-categorias')
def get_categoria():
    grupos = []
    
    pastas = os.listdir("doencas")
    for pasta in pastas:
        pasta_caminho = os.path.join("doencas", pasta)
        if os.path.isdir(pasta_caminho):
            for doenca in os.listdir(pasta_caminho):
                if doenca.endswith('.json'):
                    doenca_caminho = os.path.join(pasta_caminho, doenca)
                    with open(doenca_caminho, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        group = {
                            "titulo": data['titulo'],
                            "caminho": pasta_caminho,
                        }
                        grupos.append(group)
    
    return jsonify(grupos)

@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    senha = request.args.get('senha')
    if senha != 'abc':
        erro = 'Senha incorreta!'
        return erro
    if request.method == 'POST':
        if 'arquivo' in request.files:
            arquivo_zip = request.files['arquivo']
            if arquivo_zip.filename != '':
                # Salva o arquivo zip no servidor
                caminho_arquivo = os.path.join('uploads', arquivo_zip.filename)
                arquivo_zip.save(caminho_arquivo)
                return f'Arquivo {arquivo_zip.filename} enviado com sucesso!'    
    return render_template('enviar.html')  # Adicione um formulário HTML para enviar arquivos

@app.route('/download')
def download():
    senha = request.args.get('senha')
    if senha != 'abc':
        erro = 'Senha incorreta!'
        return erro
    with zipfile.ZipFile('download.zip', 'w') as zipf:
        # Adiciona arquivos de exemplo ao arquivo zip
        zipf.write('example_file.txt', arcname='example_file.txt')
        zipf.write('another_file.txt', arcname='another_file.txt')

    # Envia o arquivo zip para download
    return send_file('download.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)