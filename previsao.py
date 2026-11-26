"""Previsão de cancelamento de um cliente com os arquivos salvos do treino (issue #5)."""

import json
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from tensorflow import keras

RAIZ = Path(__file__).resolve().parent

CAMPOS_INTERNET = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]


def carregar_artefatos(pasta=RAIZ / "artefatos", caminho_schema=RAIZ / "schema_campos.json"):
    """Lê do disco a rede, o pré-processador, o limiar e o schema dos campos."""
    pasta = Path(pasta)
    configuracao = json.loads((pasta / "configuracao_escolhida.json").read_text(encoding="utf-8"))
    return {
        "rede": keras.models.load_model(pasta / "modelo_churn.keras"),
        "preprocessador": joblib.load(pasta / "preprocessador.joblib"),
        "limiar": configuracao["limiar_rede"],
        "campos": configuracao["features_esperadas"],
        "schema": json.loads(Path(caminho_schema).read_text(encoding="utf-8")),
    }


def _validar(cliente, artefatos):
    """Confere os dados e devolve (cliente pronto para o modelo, avisos)."""
    faltando = [campo for campo in artefatos["campos"] if campo not in cliente]
    if faltando:
        raise ValueError(f"Campos ausentes: {', '.join(faltando)}")

    dados, avisos = {}, []
    for campo in artefatos["campos"]:
        regra = artefatos["schema"][campo]
        valor = cliente[campo]

        if regra["tipo"] == "categoria":
            if valor not in regra["valores_aceitos"]:
                raise ValueError(
                    f"{campo}: valor {valor!r} não aceito. Use um de {regra['valores_aceitos']}."
                )
            dados[campo] = valor
            continue

        # Mesma regra do treino: TotalCharges em branco vale 0.
        if campo == "TotalCharges" and isinstance(valor, str) and not valor.strip():
            valor = 0.0
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{campo}: {valor!r} não é um número.") from None
        if not math.isfinite(numero) or numero < 0:
            raise ValueError(f"{campo}: informe um número maior ou igual a zero.")
        if regra["tipo"] == "int" and not numero.is_integer():
            raise ValueError(f"{campo}: informe um número inteiro.")
        if campo == "SeniorCitizen" and numero not in (0, 1):
            raise ValueError("SeniorCitizen: use 0 (não) ou 1 (sim).")
        if not regra["min"] <= numero <= regra["max"]:
            avisos.append(
                f"{campo}={numero:g} está fora da faixa vista no treino "
                f"({regra['min']:g} a {regra['max']:g})."
            )
        dados[campo] = int(numero) if regra["tipo"] == "int" else numero

    sem_internet = dados["InternetService"] == "No"
    for campo in CAMPOS_INTERNET:
        if (dados[campo] == "No internet service") != sem_internet:
            raise ValueError(f"{campo} não combina com InternetService={dados['InternetService']!r}.")
    if (dados["MultipleLines"] == "No phone service") != (dados["PhoneService"] == "No"):
        raise ValueError(f"MultipleLines não combina com PhoneService={dados['PhoneService']!r}.")

    return dados, avisos


def prever_cancelamento(cliente, artefatos):
    """Recebe os dados de um cliente e retorna a pontuação e a classe prevista.

    cliente: dict com os campos de schema_campos.json (campos extras são ignorados).
    artefatos: resultado de carregar_artefatos().
    """
    dados, avisos = _validar(cliente, artefatos)
    tabela = pd.DataFrame([dados], columns=artefatos["campos"])
    entrada = np.asarray(artefatos["preprocessador"].transform(tabela), dtype=np.float32)
    pontuacao = float(artefatos["rede"].predict(entrada, verbose=0)[0, 0])
    return {
        "pontuacao": pontuacao,
        "classe": "Yes" if pontuacao >= artefatos["limiar"] else "No",
        "limiar": artefatos["limiar"],
        "avisos": avisos,
    }
