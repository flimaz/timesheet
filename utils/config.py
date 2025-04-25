import os
import json

CONFIG_PATH = "config.json"

def carregar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def salvar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

# BANCO DE DADOS

def salvar_caminho_bd(caminho):
    config = carregar_config()
    config["caminho_banco"] = caminho
    salvar_config(config)

def carregar_caminho_bd():
    config = carregar_config()
    caminho = config.get("caminho_banco", None)
    return caminho if caminho and os.path.exists(caminho) else None

# 📁 EXPORTAÇÃO

def carregar_ultimo_diretorio_exportacao():
    config = carregar_config()
    return config.get("ultimo_diretorio_exportacao", "")

def salvar_ultimo_diretorio_exportacao(caminho):
    pasta = os.path.dirname(caminho)
    config = carregar_config()
    config["ultimo_diretorio_exportacao"] = pasta
    salvar_config(config)
