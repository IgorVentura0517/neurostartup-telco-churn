import os
import shutil
import kagglehub
import pandas as pd

path = kagglehub.dataset_download("blastchar/telco-customer-churn")
arquivo_origem = os.path.join(path, "WA_Fn-UseC_-Telco-Customer-Churn.csv")
arquivo_destino = os.path.join(os.getcwd(), "WA_Fn-UseC_-Telco-Customer-Churn.csv")

if not os.path.exists(arquivo_destino):
    shutil.copy(arquivo_origem, arquivo_destino)

df = pd.read_csv(arquivo_destino)
print("Arquivo salvo em:", arquivo_destino)