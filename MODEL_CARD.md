# Model Card — Keras_1

## Visão geral

A `Keras_1` é a rede neural usada na demonstração da Atividade Prática 3.
Ela recebe características de um cliente de telecomunicações e gera uma
pontuação de risco de cancelamento. A demonstração sinaliza risco de
cancelamento quando a pontuação é igual ou superior a `0.275`,
limiar definido no conjunto de validação.

- Modelo salvo em [`artefatos/modelo_churn.keras`](artefatos/modelo_churn.keras)
- Pré-processador salvo em [`artefatos/preprocessador.joblib`](artefatos/preprocessador.joblib)
- Configuração em [`artefatos/configuracao_escolhida.json`](artefatos/configuracao_escolhida.json)

## Uso previsto

Demonstrar como uma equipe de retenção poderia priorizar contatos com
clientes de uma operadora. A pontuação serve como apoio à análise humana.

## Não usar para

- Cancelar contratos, alterar preços ou restringir serviços automaticamente.
- Tomar decisões sobre um cliente com base apenas na pontuação.
- Aplicar o modelo em outra operadora sem avaliar seu desempenho com dados locais.

## Dados e treinamento

Foi usado o [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn),
com `Churn=Yes` como classe positiva. Os dados foram divididos de forma
estratificada em 60% para treino, 20% para validação e 20% para teste,
com seed `42`. O pré-processador foi ajustado apenas no treino.

A `Keras_1` foi escolhida pelo desempenho na validação entre as três
redes avaliadas. A regressão logística foi usada como baseline.

## Desempenho no teste reservado

O teste incluiu 1.409 clientes, dos quais 374 cancelaram.

| Modelo | Limiar | Precisão | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Regressão logística | 0,375 | 55,97% | 68,98% | 61,80% |
| Keras_1 | 0,275 | 52,13% | 75,13% | 61,56% |

A `Keras_1` identificou 281 dos 374 cancelamentos e deixou passar 93.
Também sinalizou 258 clientes que permaneceram. Em relação à regressão
logística, identificou 23 cancelamentos a mais e gerou 55 falsos
positivos adicionais.

Consulte as matrizes de confusão no [notebook de avaliação final](avaliacao_final.ipynb).

## Limitações

- As métricas descrevem o teste desta base. O desempenho em outras
  operadoras ou períodos ainda precisa ser avaliado.
- A pontuação deve ser interpretada como um indicador de risco.
  A calibração como probabilidade de cancelamento não foi avaliada.
- A avaliação mediu a capacidade de identificar cancelamentos. O efeito
  de uma ação de retenção sobre esses clientes não foi medido.