import os
import ipaddress
from flask import Flask, render_template, request
 
# Configuração do caminho da pasta templates
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
 
app = Flask(__name__, template_folder=TEMPLATE_DIR)
 
def identificar_classe_real(ip_str):
    try:
        primeiro_octeto = int(ip_str.split('.')[0])
        if 1 <= primeiro_octeto <= 126:
            return "Classe A", 16777216, 8, "Redes de grande porte (Escala Global)."
        elif 128 <= primeiro_octeto <= 191:
            return "Classe B", 65536, 16, "Redes de médio porte (Corporativas)."
        elif 192 <= primeiro_octeto <= 223:
            return "Classe C", 256, 24, "Redes de pequeno porte (Domésticas/Locais)."
        return "Especial", 0, 0, "Uso reservado ou multicast."
    except ValueError:
        return "Inválido", 0, 0, ""
 
def formatar_binario(ip_ou_mask):
    return ".".join([bin(int(x))[2:].zfill(8) for x in str(ip_ou_mask).split('.')])
 
# 🔹 Página inicial
@app.route('/')
def home():
    return render_template('index.html')
 
# (SEM JSON)
@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        #(HTML)
        ip_input = request.form.get('ip')
        prefixo_alvo = int(request.form.get('prefixo', 24))
        n_rede = int(request.form.get('subrede_index', 1))
 
        nome_classe, cap_total, pref_minimo, desc_classe = identificar_classe_real(ip_input)
 
        # 🔹 Validação
        if prefixo_alvo < pref_minimo:
            return render_template(
                "index.html",
                erro=f"Divisão impossível: para {nome_classe}, use no mínimo /{pref_minimo}"
            )
 
        ips_por_subrede = 2**(32 - prefixo_alvo)
        total_subredes = cap_total // ips_por_subrede if cap_total > 0 else 1
 
        ip_base_int = int(ipaddress.IPv4Address(ip_input.split('/')[0]))
        ip_sub_int = ip_base_int + ((n_rede - 1) * ips_por_subrede)
        rede_atual = ipaddress.ip_network(
            f"{ipaddress.IPv4Address(ip_sub_int)}/{prefixo_alvo}",
            strict=False
        )
 
        resultado = {
            "mascara": str(rede_atual.netmask),
            "rede_id": str(rede_atual.network_address),
            "primeiro_ip": str(rede_atual.network_address + 1),
            "ultimo_ip": str(rede_atual.broadcast_address - 1),
            "broadcast": str(rede_atual.broadcast_address),
            "hosts_uteis": f"{ips_por_subrede - 2:,}".replace(",", "."),
            "ip_binario": formatar_binario(rede_atual.network_address),
            "mascara_binaria": formatar_binario(rede_atual.netmask)
        }
 
        return render_template("index.html", resultado=resultado)
 
    except Exception:
        return render_template("index.html", erro="Erro de processamento. Verifique o IP.")
 
if __name__ == '__main__':
    app.run(debug=True)
