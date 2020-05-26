import json
import boto3
from botocore.exceptions import NoCredentialsError
import logging
import ask_sdk_core.utils as ask_utils
import os
import calendar

from datetime import date, datetime
from pytz import timezone

from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective)

from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

######################################## ACCESS_KEY NÃO COMPARTILHAR #######################################
ACCESS_KEY = 'COLOCAR AQUI A ACCESS_KEY '
SECRET_KEY = 'COLOCAR AQUI A SECRET_KEY'
######################################## ACCESS_KEY NÃO COMPARTILHAR #######################################

################################# JSON PARA APL PARA EXIBIR TEXTO E IMAGENS ################################
################################# JSON PARA APL PARA EXIBIR TEXTO E IMAGENS ################################

def jsonToAPL(texto):
    displayAPL = {
        "type": "APL",
        "version": "1.3",
        "settings": {},
        "theme": "dark",
        "import": [
            {
                "name": "alexa-layouts",
                "version": "1.1.0"
            }
        ],
        "resources": [],
        "styles": {
            "bigText": {
                "values": [
                    {
                        "fontSize": "52dp",
                        "textAlign": "center"
                    }
                ]
            }
        },
        "onMount": [],
        "graphics": {},
        "commands": {},
        "layouts": {},
        "mainTemplate": {
            "parameters": [
                "text",
                "assets"
            ],
            "items": [
               
                {
                    "type": "Container",
                    "when": "${@viewportProfile!=@hubRoundSmall}",
                    "items": [
                         {
                        "type": "AlexaBackground",
                        "backgroundColor": "rgba(64,192,255,100%)",
                        "backgroundAlign": "center"


                        },
                        {
                            "type": "Text",
                            "paddingTop": "12dp",
                            "paddingBottom": "12dp",
                            "style": "bigText",
                            "text": texto,
                            "fontSize": "40dp",
                            "textAlign": "center",
                            "textAlignVertical": "center",
                            "fontStyle": "normal",
                            "fontFamily": "times new roman"
                        }
                    ],
                    "height": "100%",
                    "width": "100%"
                }
            ]
        }
    }
    
    return displayAPL 

################################# JSON PARA APL PARA EXIBIR TEXTO E IMAGENS ################################
################################# JSON PARA APL PARA EXIBIR TEXTO E IMAGENS ################################


############################## VERIFICA SE O USUARIO TEM SUPORTE PARA DISPLAY ##############################
############################## VERIFICA SE O USUARIO TEM SUPORTE PARA DISPLAY ##############################

def supportInterfaces(handle_input):
    if handle_input is not None:
        return True
    else:
        return False

############################## VERIFICA SE O USUARIO TEM SUPORTE PARA DISPLAY ##############################
############################## VERIFICA SE O USUARIO TEM SUPORTE PARA DISPLAY ##############################

############################################# RENDERIZA O DISPLAY ##########################################
############################################# RENDERIZA O DISPLAY ##########################################

def textoToAPL(handler_input,texto):
    handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                token="displayToken",
                document= jsonToAPL(texto)
                )
            )

############################################# RENDERIZA O DISPLAY ##########################################
############################################# RENDERIZA O DISPLAY ##########################################

############################### FAZ O UPLOAD PARA O BUCKET USANDO O BOTO3 ###########################################
############################### FAZ O UPLOAD PARA O BUCKET USANDO O BOTO3 ###########################################

def upload_to_aws(local_file, bucket, s3_file):

    s3 = boto3.resource(
        's3',
        region_name='sa-east-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
        ) # metodo de acesso direto ao Bucket. utiliza as credenciais root


    try:
        s3.Bucket(bucket).Object(s3_file).put(Body=local_file) # metodo utilzado que funciona aqui
        logger.info("Upload Successful")
        return True
    except FileNotFoundError:
        logger.info("The file was not found")
        return False
    except NoCredentialsError:
        logger.info("Credentials not available")
        return False

############################### FAZ O UPLOAD PARA O BUCKET USANDO O BOTO3 ###########################################
############################### FAZ O UPLOAD PARA O BUCKET USANDO O BOTO3 ###########################################

############################### FAZ O DOWNLOAD DO BUCKET USANDO O BOTO3 #############################################
############################### FAZ O DOWNLOAD DO BUCKET USANDO O BOTO3 #############################################

def download_s3_file(bucket, s3_file):

    s3 = boto3.resource(
        's3',
        region_name='sa-east-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
        ) # metodo de acesso direto ao Bucket. utiliza as credenciais root
    obj = {}
    try:
        obj = s3.Bucket(bucket).Object(s3_file)
        obj = json.loads( obj.get()['Body'].read().decode('utf-8') )
        return (True, obj)
    except s3.meta.client.exceptions.NoSuchKey:
        logger.info("No Such Key in bucket")
        return (False, obj)
    
############################### FAZ O DOWNLOAD DO BUCKET USANDO O BOTO3 #############################################
############################### FAZ O DOWNLOAD DO BUCKET USANDO O BOTO3 #############################################


############################### FAZ O FILTRO DO BUCKET USANDO O BOTO3 ###############################################
############################### FAZ O FILTRO DO BUCKET USANDO O BOTO3 ###############################################

def filtrar_s3_file(bucket, prefix):

    filtro = ""
    filtro_tam = 0
    
    s3 = boto3.resource(
        's3',
        region_name='sa-east-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
        ) # metodo de acesso direto ao Bucket. utiliza as credenciais root
    
    try:
        mybucket = s3.Bucket("alexaaws-diegocampos")
        for files in mybucket.objects.filter(Prefix=prefix):
            separar = files.key.split("/")
            data = separar[1]
            data = data.split("_")
            suffix = data[0] + " de " + retornandoMes(data[1]) + " de " + data[2]
            filtro = filtro + "\n" + suffix
            filtro_tam = filtro_tam + 1
        return (True, filtro, filtro_tam)

    except s3.meta.client.exceptions.NoSuchKey:
        logger.info("No Such Key in bucket")
        return (False, filtro, filtro_tam)

############################### FAZ O FILTRO DO BUCKET USANDO O BOTO3 ###############################################
############################### FAZ O FILTRO DO BUCKET USANDO O BOTO3 ###############################################

######################### PEGA O CAMINHO COMPLETO PARA O FILTRO DO BUCKET USANDO O BOTO3 ############################
######################### PEGA O CAMINHO COMPLETO PARA O FILTRO DO BUCKET USANDO O BOTO3 ############################

def caminhoCompleto(day,month,year,file):
    s3_file = file
    
    mes = pegandoMes(month)
        
    # CONVERTE o mes para NUMERO para salvar o objeto no s3 
    month_as_index = list(calendar.month_abbr).index(mes)
    
    s3_file = s3_file + "/" + day + "_" + str(month_as_index) + "_" + year
        
    logger.info(s3_file)

    return s3_file

######################### PEGA O CAMINHO COMPLETO PARA O FILTRO DO BUCKET USANDO O BOTO3 ############################
######################### PEGA O CAMINHO COMPLETO PARA O FILTRO DO BUCKET USANDO O BOTO3 ############################

#################################### SALVA O ARQUIVO NO BUCKET USANDO O BOTO3 #######################################
#################################### SALVA O ARQUIVO NO BUCKET USANDO O BOTO3 #######################################

def salvarArquivo(attributes, s3_file):
    
    if attributes and s3_file:
        
        dados = json.dumps(attributes)
        
        upload_to_aws(dados, "COLOCAR AQUI O NOME DO SEU BUCKET", s3_file)
        return True
    
    else:
        logger.info("attributes vazio")
        return False

#################################### SALVA O ARQUIVO NO BUCKET USANDO O BOTO3 #######################################
#################################### SALVA O ARQUIVO NO BUCKET USANDO O BOTO3 #######################################


############################### LIMPA O NOME PARA QUE POSSA SER USADO NO BUCKET COM O BOTO3 #########################
############################### LIMPA O NOME PARA QUE POSSA SER USADO NO BUCKET COM O BOTO3 #########################

def limparNome(name):
    name = name.split()
        
    s3_file = ""
        
    for i in name:
        s3_file = s3_file + i
        
    logger.info(s3_file)    
    return s3_file

############################### LIMPA O NOME PARA QUE POSSA SER USADO NO BUCKET COM O BOTO3 #########################
############################### LIMPA O NOME PARA QUE POSSA SER USADO NO BUCKET COM O BOTO3 #########################

############# CONVERTE O NOME DO MES PARA INGLES PARA SER USADO NA FUNÇAO QUE TRANSFORMA NOME EM NUMERO #############
############# CONVERTE O NOME DO MES PARA INGLES PARA SER USADO NA FUNÇAO QUE TRANSFORMA NOME EM NUMERO #############

def pegandoMes(month):
    mes = ""
    if  month[:3].title().lower() == 'jan':
        mes = 'Jan'
    elif month[:3].title().lower() == 'fev':
        mes = 'Feb'
    elif month[:3].title().lower() == 'mar':
        mes = 'Mar'
    elif month[:3].title().lower() == 'abr':
        mes = 'Apr'
    elif month[:3].title().lower() == 'mai':
        mes = 'May'
    elif month[:3].title().lower() == 'jun':
        mes = 'Jun'
    elif month[:3].title().lower() == 'jul':
        mes = 'Jul'
    elif month[:3].title().lower() == 'ago':
        mes = 'Aug'
    elif month[:3].title().lower() == 'set':
        mes = 'Sep'
    elif month[:3].title().lower() == 'out':
        mes = 'Oct'
    elif month[:3].title().lower() == 'nov':
        mes = 'Nov'
    elif month[:3].title().lower() == 'dez':
        mes = 'Dec'

    return mes

############# CONVERTE O NOME DO MES PARA INGLES PARA SER USADO NA FUNÇAO QUE TRANSFORMA NOME EM NUMERO #############
############# CONVERTE O NOME DO MES PARA INGLES PARA SER USADO NA FUNÇAO QUE TRANSFORMA NOME EM NUMERO #############

######## CONVERTE O NUMERO DO MES PARA O NOME EM PORTUGUES PARA SER USADO NA FUNÇAO QUE FILTRA OS REGISTROS #########
######## CONVERTE O NUMERO DO MES PARA O NOME EM PORTUGUES PARA SER USADO NA FUNÇAO QUE FILTRA OS REGISTROS #########

def retornandoMes(month):
    mes = ""
    if  month == "1":
        mes = 'janeiro'
    elif month == "2":
        mes = 'fevereiro'
    elif month == "3":
        mes = 'março'
    elif month == "4":
        mes = 'abril'
    elif month == "5":
        mes = 'maio'
    elif month == "6":
        mes = 'junho'
    elif month == "7":
        mes = 'julho'
    elif month == "8":
        mes = 'agosto'
    elif month == "9":
        mes = 'setembro'
    elif month == "10":
        mes = 'outubro'
    elif month == "11":
        mes = 'novembro'
    elif month == "12":
        mes = 'dezembro'

    return mes

######## CONVERTE O NUMERO DO MES PARA O NOME EM PORTUGUES PARA SER USADO NA FUNÇAO QUE FILTRA OS REGISTROS #########
######## CONVERTE O NUMERO DO MES PARA O NOME EM PORTUGUES PARA SER USADO NA FUNÇAO QUE FILTRA OS REGISTROS #########



################################################# VALIDA O CPF ######################################################
################################################# VALIDA O CPF ######################################################

def validaCPF(cpf_1,cpf_2,cpf_3,cpf_dv):
    soma = (int(cpf_1[0]) * 10) + (int(cpf_1[1]) * 9) + (int(cpf_1[2]) * 8) + (int(cpf_2[0]) * 7) + (int(cpf_2[1]) * 6) + (int(cpf_2[2]) * 5) 
    soma = soma + (int(cpf_3[0]) * 4) + (int(cpf_3[1]) * 3) + (int(cpf_3[2]) * 2) 
    
    valor = (soma * 10)% 11
    
    soma2 = (int(cpf_1[0]) *11 ) + (int(cpf_1[1]) * 10) + (int(cpf_1[2]) * 9) + (int(cpf_2[0]) * 8) + (int(cpf_2[1]) * 7) + (int(cpf_2[2]) * 6)
    soma2 = soma2 + (int(cpf_3[0]) * 5) + (int(cpf_3[1]) * 4) + (int(cpf_3[2]) * 3) + (int(cpf_dv[0]) * 2) 
    
    valor2 = (soma2 * 10) % 11
    if valor == int(cpf_dv[0]) and valor2 == int(cpf_dv[1]):
        return True
    else:
        return False

################################################# VALIDA O CPF ######################################################
################################################# VALIDA O CPF ######################################################

