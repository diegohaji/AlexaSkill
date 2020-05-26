# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.

import json
import boto3
from botocore.exceptions import NoCredentialsError
import logging
import ask_sdk_core.utils as ask_utils
import os
import calendar

from datetime import date, datetime
from pytz import timezone
from utils import *

from ask_sdk_core.skill_builder import CustomSkillBuilder # alterado para uma custom skill # Anterior era SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective)

from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



########################################### vairaveis globais ##############################################
########################################### vairaveis globais ##############################################

obj = {}                        # infomações do BUCKET
attributes = {}                 # infomações para o BUCKET
s3_file = ""                    # nome do arquivo no BUCKET
nome = ""                       # nome que indica o nome da pasta do BUCKET para procurar junto da data
qtd_medicamentos = 0            # quantidade de medicamentos para salvar no json
displayToken = "displayToken"   # token de verificação da APL

                        # APL Document file paths for use in handlers
                        #hello_world_doc_path = "./apl/helloworldDocument.json"
                        #hello_world_button_doc_path = "./apl/helloworldWithButtonDocument.json"
                        # Tokens used when sending the APL directives
                        #HELLO_WORLD_TOKEN = "helloworldToken"
                        #HELLO_WORLD_WITH_BUTTON_TOKEN = "helloworldWithButtonToken"


########################################### vairaveis globais ##############################################
########################################### vairaveis globais ##############################################


#********************************************** PRINCIPAL **********************************************#
#********************************************** PRINCIPAL **********************************************#
#********************************************** PRINCIPAL **********************************************#

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        
        texto = "Olá, bem vindo ao assistente de CADASTRO. \
                <br>Caso deseje começar um cadastro diga criar cadastro e o nome completo do paciente. \
                <br>Caso deseje saber sobre algum paciente já cadastrado, diga 'Encontrar registro de' \
                <br>e o nome completo do paciente para que eu possa procurar na base de dados."
        
        
        handle_input = ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl
        handler_input_apl = handler_input
        if supportInterfaces(handle_input) == True :
            textoToAPL(handler_input_apl,texto)
            
        speak_output = "Olá, bem vindo ao assistente de CADASTRO.  \
                        Caso deseje começar um cadastro diga criar cadastro e o nome completo do paciente. \
                        Caso deseje saber sobre algum paciente já cadastrado, diga 'Encontrar registro de' \
                        e o nome completo do paciente para que eu possa procurar na base de dados."
                         
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
           #     .ask(reprompt)
                .response
        )

#********************************************** PRINCIPAL **********************************************#
#********************************************** PRINCIPAL **********************************************#
#********************************************** PRINCIPAL **********************************************#


#********************************************** DEVOLVE INFOMAÇÕES **********************************************#
#********************************************** DEVOLVE INFOMAÇÕES **********************************************#
#********************************************** DEVOLVE INFOMAÇÕES **********************************************#
#********************************************** DEVOLVE INFOMAÇÕES **********************************************#

############################### PEGA O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS #################################
############################### PEGA O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS #################################

class ObterNomeIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): 
        
        return ask_utils.is_intent_name("ObterNomeIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        global s3_file, nome
        
        s3_file = ""
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        name = slots["name"].value
        nome = ""
        nome = name
        
        s3_file = limparNome(name)
        
        texto = "Nome procurado: {nome}".format(nome=nome)
        
        handle_input = ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl
        handler_input_apl = handler_input

            
        filtro_bool,filtro,filtro_tam = filtrar_s3_file("COLOCAR AQUI O NOME DO SEU BUCKET",s3_file)
        
        if filtro_bool == True :
            
            if filtro_tam == 1 :
                speak_output = "{numero} arquivo encontrado. Agora diga a 'arquivo do dia' e a data \
                            por extenso para saber infomações sobre {nome}.\
                            A data disponível é {filtro}.\
                            ".format(numero=filtro_tam, filtro=filtro, nome=nome)
                
                texto = "{numero} arquivo encontrado. Agora diga a 'arquivo do dia' e a data \
                          <br>por extenso para saber infomações sobre {nome}.\
                          <br>A data disponível é {filtro}.\
                          ".format(numero=filtro_tam, filtro=filtro, nome=nome)
                
            
            else:
                speak_output = "{numero} arquivos encontrados. Qual a data desejada sobre {nome}?\
                            Estas estão disponíveis {filtro}. Agora diga a 'arquivo do dia' e a data \
                            por extenso para saber infomações sobre {nome} \
                            ".format(numero=filtro_tam, filtro=filtro, nome=nome)
                texto = "{numero} arquivos encontrados. Qual a data desejada sobre {nome}?\
                            <br>Estas estão disponíveis {filtro}. Agora diga a 'arquivo do dia' e a data \
                            <br>por extenso para saber infomações sobre {nome} \
                            ".format(numero=filtro_tam, filtro=filtro, nome=nome)
                    
        else:
            speak_output = "Nenhum registro encontrado para {nome}. Tente novamente. \
                            Eu posso armazenar sua data de aniversário, sua altura, seu peso, sua pressão e seus batimentos cardíacos. \
                            Mas primeiro escolha o nome do arquivo a ser armazenado, dizendo,\
                            Criar cadastro e o nome completo do paciente.".format(nome=nome)
            texto = "Nenhum registro encontrado para {nome}. Tente novamente. \
                            <br>Eu posso armazenar sua data de aniversário, sua altura, seu peso, sua pressão e seus batimentos cardíacos. \
                            <br>Mas primeiro escolha o nome do arquivo a ser armazenado, dizendo,\
                            <br>Criar cadastro e o nome completo do paciente.".format(nome=nome)
        if supportInterfaces(handle_input) == True :
            textoToAPL(handler_input_apl,texto)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################### PEGA O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS #################################
############################### PEGA O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS #################################

######### PEGA A DATA PARA JUNTAR COM O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS SE ELE ESTEVE LA NO DIA ########
######### PEGA A DATA PARA JUNTAR COM O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS SE ELE ESTEVE LA NO DIA ########

class ObterDataIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): 
        
        return ask_utils.is_intent_name("ObterDataIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        global obj, s3_file, nome
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        year = slots["ano_numero"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        month = slots["mes_numero"].value # pegar o valor do slot correspondente e armazena em uma variavel
        day = slots["dia_numero"].value   # pegar o valor do slot correspondente e armazena em uma variavel
        
        s3_file = caminhoCompleto(day,month,year,s3_file)
        
        arquivo_bool, obj = download_s3_file("COLOCAR AQUI O NOME DO SEU BUCKET",s3_file)
        
        if arquivo_bool == True :
            
            speak_output = "Pronto! O que deseja saber sobre {nome} nessa data?\
                            Eu posso informar sobre a data de aniversário, altura, peso, pressão e batimentos cardíacos.\
                            ".format(nome=nome)

            
        else:
            speak_output = "O registro encontrado para {nome}. Tente novamente passar novamente o nome e a data. \
                            ".format(nome=nome)

        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

######### PEGA A DATA PARA JUNTAR COM O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS SE ELE ESTEVE LA NO DIA ########
######### PEGA A DATA PARA JUNTAR COM O NOME DA PESSOA PARA VERIFICAR NA BASE DE DADOS SE ELE ESTEVE LA NO DIA ########


############################################ RESPONSAVEL PELO RG  #####################################################
############################################ RESPONSAVEL PELO RG  #####################################################

class ObterRegistroGeralIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ObterRegistroGeralIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes, obj
        
        
        
        try:
            if attributes:
                rg_completo = attributes["RG"]
            elif obj:
                rg_completo = obj["RG"]
            else:
                speak_output = "Esses dados não estão disponíveis!"

            
            if obj or attributes:
                speak_output = 'O RG é {rg}.'.format(rg=rg_completo)

        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)


        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

############################################ RESPONSAVEL PELO RG  #####################################################
############################################ RESPONSAVEL PELO RG  #####################################################

#################################### RESPONSAVEL PELO ORGAO EXPEDIDOR DO RG  ##########################################
#################################### RESPONSAVEL PELO ORGAO EXPEDIDOR DO RG  ##########################################


class ObterOrgaoExpedidorIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ObterOrgaoExpedidorIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes, obj
        
        
        
        try:
            if attributes:
                expedidor = attributes["OE"]
            elif obj:
                expedidor = obj["OE"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            
            if obj or attributes:
                speak_output = 'O orgão expedidor é {oe}.'.format(oe=expedidor)

        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

#################################### RESPONSAVEL PELO ORGAO EXPEDIDOR DO RG  ##########################################
#################################### RESPONSAVEL PELO ORGAO EXPEDIDOR DO RG  ##########################################

############################################ RESPONSAVEL PELO RG  #####################################################
############################################ RESPONSAVEL PELO RG  #####################################################

class ObterCPFIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ObterCPFIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes, obj
        
        
        
        try:
            if attributes:
                cpf_completo = attributes["CPF"]
            elif obj:
                cpf_completo = obj["CPF"]
            else:
                speak_output = "Esses dados não estão disponíveis!"
            
            
            if obj or attributes:
                speak_output = 'O CPF é {cpf}.'.format(cpf=cpf_completo)

                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)


        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

############################################ RESPONSAVEL PELO RG  #####################################################
############################################ RESPONSAVEL PELO RG  #####################################################

################################################## RETORNA O SEXO  ####################################################
################################################## RETORNA O SEXO  ####################################################

class ObterSexoIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterSexoIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
         
        

        try:
            if attributes:
                genero = attributes["Genero"]
            elif obj:
                genero = obj["Genero"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            if obj or attributes:
                speak_output = 'O sexo é {sexo} .'.format(sexo=genero)

        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

################################################## RETORNA O SEXO  ####################################################
################################################## RETORNA O SEXO  ####################################################

############################################### RETORNA A NATURALIDADE ################################################
############################################### RETORNA A NATURALIDADE ################################################

class ObterNaturalidadeIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterNaturalidadeIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
            
        try:
            if attributes:
                pais = attributes["Naturalidade"]
            elif obj:
                pais = obj["Naturalidade"]
            else:
                speak_output = "Esses dados não estão disponíveis!"

            if obj or attributes:
                speak_output = 'É natural de {pais} .'.format(pais=pais)

                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################################### RETORNA A NACIONALIDADE ###############################################
############################################### RETORNA A NACIONALIDADE ###############################################

class ObterNacionalidadeIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterNacionalidadeIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        
        try:
            if attributes:
                pais = attributes["Nacionalidade"]
            elif obj:
                pais = obj["Nacionalidade"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            if obj or attributes:
                speak_output = 'Nacionalidade é {pais} .'.format(pais=pais)

                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################################### RETORNA A NACIONALIDADE ###############################################
############################################### RETORNA A NACIONALIDADE ###############################################

############################################### RETORNA O ESTADO CIVIL  ###############################################
############################################### RETORNA O ESTADO CIVIL  ###############################################

class ObterEstadoCivilIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterEstadoCivilIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        

        try:
            if attributes:
                ec = attributes["Estado_Civil"]
            elif obj:
                ec = obj["Estado_Civil"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            if obj or attributes:
                speak_output = 'Estado civil {ec} .'.format(ec=ec)

        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################################### RETORNA O ESTADO CIVIL  ###############################################
############################################### RETORNA O ESTADO CIVIL  ###############################################

############################################### RETORNA A PROFISSAO  ##################################################
############################################### RETORNA A PROFISSAO  ##################################################

class ObterProfissaoIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterProfissaoIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes

        try:
            if attributes:
                profissao = attributes["Profissao"]
            elif obj:
                profissao = obj["Profissao"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            if obj or attributes:
                speak_output = 'Profissão {profissao} .'.format(profissao=profissao)

        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################################### RETORNA A PROFISSAO  ##################################################
############################################### RETORNA A PROFISSAO  ##################################################

############################################### RETORNA O TELEFONE   ##################################################
############################################### RETORNA O TELEFONE   ##################################################

class ObterTelefoneIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterTelefoneIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes

        try:
            if attributes:
                tel = attributes["Telefone"]
            elif obj:
                tel = obj["Telefone"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            if obj or attributes:
                speak_output = 'Telefone {tel} .'.format(tel=tel)

                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################################### RETORNA O TELEFONE   ##################################################
############################################### RETORNA O TELEFONE   ##################################################

################################################ RETORNA O CELULAR   ##################################################
################################################ RETORNA O CELULAR   ##################################################

class ObterCelularIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterCelularIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        
        try:
            if attributes:
                tel = attributes["Celular"]
            elif obj:
                tel = obj["Celular"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            if obj or attributes:
                speak_output = 'Celular {tel} .'.format(tel=tel)

                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

################################################ RETORNA O CELULAR   ##################################################
################################################ RETORNA O CELULAR   ##################################################

################################################## RETORNA O EMAIL ####################################################
################################################## RETORNA O EMAIL ####################################################

class ObterEmailIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterEmailIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        
        try:
            if attributes:
                email = attributes["Email"]
            elif obj:
                email = obj["Email"]
            else:
                speak_output = "Esses dados não estão disponíveis!"

            if obj or attributes:
                speak_output = 'Email {email} .'.format(email=email)

                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

################################################## RETORNA O EMAIL ####################################################
################################################## RETORNA O EMAIL ####################################################

########################################### RETORNA A DATA DE NASCIMENTO ##############################################
########################################### RETORNA A DATA DE NASCIMENTO ##############################################

class ObterNascimentoIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        

        return ask_utils.is_intent_name("ObterNascimentoIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        
        try:
            if attributes:
                year = attributes["ano"]
                month = attributes["mes"]
                day = attributes["dia"] 
            elif obj:
                year = obj["ano"]
                month = obj["mes"]
                day = obj["dia"] 
            else:
                speak_output = "Esses dados não estão disponíveis!"

            
            if obj or attributes:
                speak_output = 'A data de nascimento é dia {dia} de {mes} de {ano}!'.format(dia=day, mes=month, ano=year)
                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?"
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

########################################### RETORNA A DATA DE NASCIMENTO ##############################################
########################################### RETORNA A DATA DE NASCIMENTO ##############################################

################################################# RETORNA A ALTURA  ###################################################
################################################# RETORNA A ALTURA  ###################################################

class ObterAlturaIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterAlturaIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        try:
            if attributes:
                meter = attributes["Metro"]
                centimeter = attributes["Centimetro"]
            elif obj:
                meter = obj["Metro"]
                centimeter = obj["Centimetro"]
            else:
                speak_output = "Esses dados não estão disponíveis!"
            
            if obj or attributes:
                if meter == "1" :
                    speak_output = 'A altura é {metro} metro e {centimetros} centímetros!'.format(metro=meter, centimetros=centimeter)

                else:
                    speak_output = 'A altura é {metro} metros e {centimetros} centímetros!'.format(metro=meter, centimetros=centimeter)

                    
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
            
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

################################################# RETORNA A ALTURA  ###################################################
################################################# RETORNA A ALTURA  ###################################################

################################################## RETORNA O PESO  ####################################################
################################################## RETORNA O PESO  ####################################################

class ObterPesoIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterPesoIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        
        try:
            if attributes:
                weight = attributes["Peso"]
            elif obj:
                weight = obj["Peso"]
            else:
                speak_output = "Esses dados não estão disponíveis!"

            if obj or attributes:
                speak_output = 'O peso é {massa} quilogramas!'.format(massa=weight)

                    
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

################################################## RETORNA O PESO  ####################################################
################################################## RETORNA O PESO  ####################################################

################################################## RETORNA A IDADE ####################################################
################################################## RETORNA A IDADE ####################################################

class ObterIdadeIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for knowing the age"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario

        return ask_utils.is_intent_name("ObterIdadeIntent")(handler_input) 

    def handle(self, handler_input): 

        global obj, attributes
        
        try:
            if attributes:
                year = attributes["year"]
                month = attributes["month"]
                day = attributes["day"] 
            elif obj:
                year = obj["year"]
                month = obj["month"]
                day = obj["day"]
            else:
                speak_output = "Esses dados não estão disponíveis!"


            
            if obj or attributes:
                
                now_time = datetime.now() # pega a data e a hora atual
                
                # Remove o tempo da data porque afeta o calculo
                now_date = datetime(now_time.year, now_time.month, now_time.day)
                current_year = now_time.year
                
                mes = pegandoMes(month)
                    
                # pegando o proximo aniversario 
                month_as_index = list(calendar.month_abbr).index(mes) # pega as primeiras 3 letras do mes 
                next_birthday = datetime(current_year, month_as_index, day) # passa para o proximo aniversario o ano atual, o indice do mes e o dia
                
                
                # verifica se tem que ajustar o aniversario em um ano 
                if now_date > next_birthday:
                    next_birthday = datetime(
                        current_year + 1,
                        month_as_index,
                        day
                    )
                    current_year += 1
                # setting the default speak_output to Happy xth Birthday!!
                
                #speak_output = 'Feliz aniversário de {} anos!'.format(str(current_year - year))
                if now_date != next_birthday:
                    diff_days = abs((now_date - next_birthday).days)
                    speak_output = '{birthday_num} anos!\
                                    '.format(
                                        birthday_num=(current_year-year - 1),
                                    )

        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
            
        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

################################################## RETORNA A IDADE ####################################################
################################################## RETORNA A IDADE ####################################################

############################################ RETORNA A PRESSÃO SANGUINEA  #############################################
############################################ RETORNA A PRESSÃO SANGUINEA  #############################################

class ObterPressaoIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario
        # extract persistent attributes and check if they are all present
        
        return ask_utils.is_intent_name("ObterPressaoIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): # cuida dos atributos caso existam
        
        global obj, attributes
        try:
            if attributes:
                systolic = attributes["Sistolica"]
                diastolic = attributes["Diastolica"]
                
            elif obj:
                systolic = obj["systolic"]
                diastolic = obj["diastolic"]
                
            else:
                speak_output = "Esses dados não estão disponíveis!"

            if obj or attributes:
                speak_output = 'A pressão arterial era {sistolica} por {diastolica} \
                            '.format(
                                sistolica = systolic,
                                diastolica = diastolic
                            )
                
                
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)

        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

############################################ RETORNA A PRESSÃO SANGUINEA  #############################################
############################################ RETORNA A PRESSÃO SANGUINEA  #############################################

########################################## RETORNA OS BATIMENTOS CARDIACOS ############################################
########################################## RETORNA OS BATIMENTOS CARDIACOS ############################################

class ObterBatimentosIntentHandler(AbstractRequestHandler): # classe que cuida da persistencia e dos dados salvos
    """Handler for launch after they have set their birthday"""

    def can_handle(self, handler_input): # função para verificar se a aplicação já possui os dados do usuario

        
        return ask_utils.is_intent_name("ObterBatimentosIntent")(handler_input) # retorna para o usuario


    def handle(self, handler_input): 
        
        global obj, attributes
        
        speak_output = ""
        
        try:
            if attributes :
                heartbeats = attributes["Batidas"]

            elif obj :
                heartbeats = obj["Batidas"]

            else:
                speak_output = "Esses dados não estão disponíveis!"

            
            if obj or attributes :
                speak_output = 'Os batimentos cardíacos eram {batimentos} \
                             '.format(
                                batimentos = heartbeats
                            )

                    
        except (UnboundLocalError, KeyError):
            speak_output = "Esses dados não estão disponíveis!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)

        handler_input.response_builder.speak(speak_output)
        reprompt = "Deseja mais alguma coisa?Eu posso armazenar a data de nascimento, a altura, o peso, a pressão e os batimentos cardíacos."
        handler_input.response_builder.ask(reprompt)

        return handler_input.response_builder.response

########################################## RETORNA OS BATIMENTOS CARDIACOS ############################################
########################################## RETORNA OS BATIMENTOS CARDIACOS ############################################

#********************************************** DEVOLVE INFOMAÇÕES **********************************************#
#********************************************** DEVOLVE INFOMAÇÕES **********************************************#
#********************************************** DEVOLVE INFOMAÇÕES **********************************************#



#********************************************** GUARDA INFOMAÇÕES **********************************************#
#********************************************** GUARDA INFOMAÇÕES **********************************************#
#********************************************** GUARDA INFOMAÇÕES **********************************************#
#********************************************** GUARDA INFOMAÇÕES **********************************************#



################################ RESPONSAVEL POR ARMAZENAR O ARQUIVO NO S3 ############################################
################################ RESPONSAVEL POR ARMAZENAR O ARQUIVO NO S3 ############################################

class NomeIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NomeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes, s3_file, nome
        
        attributes = {}
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        name = slots["name"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        now_time = datetime.now()
        
        nome = ""
        nome = name
        attributes["Nome"] = nome
        name = name.split()
        
        s3_file = ""
        
        for i in name:
            s3_file = s3_file + i
            
        s3_file = s3_file + "/" + str(now_time.day) + "_" + str(now_time.month) + "_" + str(now_time.year)
        
        logger.info(s3_file)
        
        #handler_input.response_builder.ask("Qual cadastro deseja fazer?")
        speak_output = 'Obrigada, iniciarei o cadastro de {nome}.'.format(nome=slots["name"].value)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

################################ RESPONSAVEL POR ARMAZENAR O ARQUIVO NO S3 ############################################
################################ RESPONSAVEL POR ARMAZENAR O ARQUIVO NO S3 ############################################

###################################### RESPONSAVEL POR SALVAR O CADASTRO #############################################
###################################### RESPONSAVEL POR SALVAR O CADASTRO #############################################

class SalvarCadastroIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SalvarCadastroIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes, s3_file, nome
        
        if salvarArquivo(attributes, s3_file) == True:
            speak_output = 'Registro de {nome} foi armazenado.'.format(nome=nome)
        
        else:
            speak_output = 'Não foi possível armazenar o registro de {nome}.\
                            Verifique se o cadastro foi iniciado, \
                            se os dados do paciente foram registrados\
                            e tente novamente.'.format(nome=nome)

        
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

###################################### RESPONSAVEL POR SALVAR O CADASTRO #############################################
###################################### RESPONSAVEL POR SALVAR O CADASTRO #############################################

############################################ RESPONSAVEL PELO RG  ####################################################
############################################ RESPONSAVEL PELO RG  ####################################################

class RegistroGeralIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RegistroGeralIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        rg_1 = slots["rg_um"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        rg_2 = slots["rg_dois"].value # pegar o valor do slot correspondente e armazena em uma variavel
        rg_3 = slots["rg_tres"].value   # pegar o valor do slot correspondente e armazena em uma variavel
        
        # cria uma variavel para cuidar dos atributos
        
        if len(rg_1) <=1:
            rg_1 = "0" + rg_1
        
        if len(rg_2) <=1:
            rg_2 = "00" + rg_2
        elif len(rg_2) <=2:
            rg_2 = "0" + rg_2
        
        if len(rg_3) <=1:
            rg_3 = "00" + rg_3
        elif len(rg_3) <=2:
            rg_3 = "0" + rg_3
        
        rg_completo = rg_1 + "." + rg_2 + "." + rg_3
        attributes["RG"] = rg_completo
        
        speak_output = 'Obrigada, lembrarei que o érri gê é {rg}.'.format(rg=rg_completo)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

############################################ RESPONSAVEL PELO RG  ####################################################
############################################ RESPONSAVEL PELO RG  ####################################################

##################################### RESPONSAVEL PELO ORGAO EMISSOR DO RG  ##########################################
##################################### RESPONSAVEL PELO ORGAO EMISSOR DO RG  ##########################################

class OrgaoExpedidorIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("OrgaoExpedidorIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        emissor = slots["orgao"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["OE"] = emissor
        
        speak_output = 'Obrigada, lembrarei que o Orgão expedidor é {oe}.'.format(oe=emissor)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

##################################### RESPONSAVEL PELO ORGAO EMISSOR DO RG  ##########################################
##################################### RESPONSAVEL PELO ORGAO EMISSOR DO RG  ##########################################

############################################ RESPONSAVEL PELO CPF ####################################################
############################################ RESPONSAVEL PELO CPF ####################################################

class CPFIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CPFIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        cpf_1 = slots["cpf_um"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        cpf_2 = slots["cpf_dois"].value # pegar o valor do slot correspondente e armazena em uma variavel
        cpf_3 = slots["cpf_tres"].value   # pegar o valor do slot correspondente e armazena em uma variavel
        cpf_dv = slots["cpf_dv"].value   # pegar o valor do slot correspondente e armazena em uma variavel
        # cria uma variavel para cuidar dos atributos
        
        if len(cpf_1) <=1:
            cpf_1 = "00" + cpf_1
        elif len(cpf_1) <=2:
            cpf_1 = "0" + cpf_1
        
        if len(cpf_2) <=1:
            cpf_2 = "00" + cpf_2
        elif len(cpf_2) <=2:
            cpf2 = "0" + cpf_2
        
        if len(cpf_3) <=1:
            cpf_3 = "00" + cpf_3
        elif len(cpf_3) <=2:
            cpf_3 = "0" + cpf_3
        
        if len(cpf_dv) <=1:
            cpf_dv = "0" + cpf_dv
        
        cpf_completo = cpf_1 + "." + cpf_2 + "." + cpf_3 + "-" + cpf_dv
        
        if validaCPF(cpf_1,cpf_2,cpf_3,cpf_dv) == True:
            attributes["CPF"] = cpf_completo 
            speak_output = 'Obrigada, lembrarei que o CPF é {cpf}.'.format(cpf=cpf_completo)
        else:
            speak_output = 'O CPF {cpf} é inválido!.'.format(cpf=cpf_completo)
        
        reprompt = "Por favor, diga novamente o cê pê efi!"
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt)
                .response
        )

############################################ RESPONSAVEL PELO CPF ####################################################
############################################ RESPONSAVEL PELO CPF ####################################################

################################### RESPONSAVEL PELA DATA DE NASCIMENTO  #############################################
################################### RESPONSAVEL PELA DATA DE NASCIMENTO  #############################################

class NacimentoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NascimentoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        year = slots["ano"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        month = slots["mes"].value # pegar o valor do slot correspondente e armazena em uma variavel
        day = slots["dia"].value   # pegar o valor do slot correspondente e armazena em uma variavel
        
        if len(year) <= 2:
            if int(year) < 19:
                year = "20"+ str(year)
            else:
                year = "19"+ str(year)
        
        # cria uma variavel para cuidar dos atributos

        attributes["Dia"] = day
        attributes["Mes"] = month
        attributes["Ano"] = year

        speak_output = 'Obrigada, lembrarei que nasceu em {dia} de {mes} de {ano}.'.format(mes=month, dia=day, ano=year)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

################################### RESPONSAVEL PELA DATA DE NASCIMENTO  #############################################
################################### RESPONSAVEL PELA DATA DE NASCIMENTO  #############################################

########################################## RESPONSAVEL PELO SEXO  ####################################################
########################################## RESPONSAVEL PELO SEXO  ####################################################

class SexoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SexoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        genero = slots["genero"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Genero"] = genero
        
        #handler_input.response_builder.ask("Qual o peso em quilogramas?")
        
        speak_output = 'Obrigada, lembrarei que o sexo é {sexo} .'.format(sexo=genero)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

########################################## RESPONSAVEL PELO SEXO  ####################################################
########################################## RESPONSAVEL PELO SEXO  ####################################################

####################################### RESPONSAVEL PELA NATURALIDADE ################################################
####################################### RESPONSAVEL PELA NATURALIDADE ################################################

class NaturalidadeIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NaturalidadeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        naturalidade = slots["pais"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Naturalidade"] = naturalidade
        
        #handler_input.response_builder.ask("Qual o peso em quilogramas?")
        
        speak_output = 'Obrigada, lembrarei que a naturalidade é {pais} .'.format(pais=naturalidade)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

####################################### RESPONSAVEL PELA NATURALIDADE ################################################
####################################### RESPONSAVEL PELA NATURALIDADE ################################################

####################################### RESPONSAVEL PELA NATURALIDADE ################################################
####################################### RESPONSAVEL PELA NATURALIDADE ################################################

class NacionalidadeIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NacionalidadeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        nacionalidade = slots["nacional"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Nacionalidade"] = nacionalidade
        
        #handler_input.response_builder.ask("Qual o peso em quilogramas?")
        
        speak_output = 'Obrigada, lembrarei que a nacionalidade é {pais} .'.format(pais=nacionalidade)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

####################################### RESPONSAVEL PELA NATURALIDADE ################################################
####################################### RESPONSAVEL PELA NATURALIDADE ################################################

####################################### RESPONSAVEL PELA PROFISSAO ###################################################
####################################### RESPONSAVEL PELA PROFISSAO ###################################################

class ProfissaoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ProfissaoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        trabalho = slots["trabalho"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Profissao"] = trabalho
        
        #handler_input.response_builder.ask("Qual o peso em quilogramas?")
        
        speak_output = 'Obrigada, lembrarei que a profissão é {trabalho} .'.format(trabalho=trabalho)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

####################################### RESPONSAVEL PELA PROFISSAO ###################################################
####################################### RESPONSAVEL PELA PROFISSAO ###################################################

####################################### RESPONSAVEL PELO ESTADO CIVIL ################################################
####################################### RESPONSAVEL PELO ESTADO CIVIL ################################################

class EstadoCivilIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("EstadoCivilIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        ec = slots["estadoCivil"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Estado_Civil"] = ec
        
        #handler_input.response_builder.ask("Qual o peso em quilogramas?")
        
        speak_output = 'Obrigada, lembrarei que o estado civil é {ec} .'.format(ec=ec)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

####################################### RESPONSAVEL PELO ESTADO CIVIL ################################################
####################################### RESPONSAVEL PELO ESTADO CIVIL ################################################

########################################### RESPONSAVEL PELO TELEFONE  ###############################################
########################################### RESPONSAVEL PELO TELEFONE  ###############################################

class TelefoneIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TelefoneIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        tel = slots["numero_telefone"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Telefone"] = "(" + tel[0:2] + ")" + tel[2:]
        
        speak_output = 'Obrigada, lembrarei que o número de telefone é ddd {ddd} {tel}.'.format(ddd=tel[0:2],tel=tel[2:])
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

########################################### RESPONSAVEL PELO TELEFONE  ###############################################
########################################### RESPONSAVEL PELO TELEFONE  ###############################################

########################################### RESPONSAVEL PELO CELULAR   ###############################################
########################################### RESPONSAVEL PELO CELULAR   ###############################################

class CelularIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CelularIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        tel = slots["numero_celular"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Celular"] = "(" + tel[0:2] + ")" + tel[2:]
        
        speak_output = 'Obrigada, lembrarei que o número de celuar é ddd {ddd} {tel}.'.format(ddd=tel[0:2],tel=tel[2:])
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

########################################### RESPONSAVEL PELO CELULAR   ###############################################
########################################### RESPONSAVEL PELO CELULAR   ###############################################

############################################# RESPONSAVEL PELO EMAIL #################################################
############################################# RESPONSAVEL PELO EMAIL #################################################

class EmailIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("EmailIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        nick = slots["nick"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        at = slots["at"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        host = slots["host"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        if at != "@":
            at = "@"
        
        email = nick + at + host
        
        attributes["Email"] = email
        
        speak_output = 'Obrigada, lembrarei que o email é {email}'.format(email=email)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

############################################# RESPONSAVEL PELO EMAIL #################################################
############################################# RESPONSAVEL PELO EMAIL #################################################


########################################## RESPONSAVEL PELO PESO  ####################################################
########################################## RESPONSAVEL PELO PESO  ####################################################

class PesoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PesoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        weight = slots["massa"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        
        attributes["Peso"] = weight
        
        
        speak_output = 'Obrigada, lembrarei que o peso é {peso} quilogramas .'.format(peso=weight)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)    
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

########################################## RESPONSAVEL PELO PESO  ####################################################
########################################## RESPONSAVEL PELO PESO  ####################################################

########################################## RESPONSAVEL PELA ALTURA ###################################################
########################################## RESPONSAVEL PELA ALTURA ###################################################

class AlturaIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return ask_utils.is_intent_name("AlturaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 

        height = slots["comprimento"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        meter = height[0:1]
        centimeter = height[1:]
        
        attributes["Metro"] = meter
        attributes["Centimetro"] = centimeter
        
        speak_output = 'Obrigada, lembrarei que a altura é {metro} metro e {centimetros} centímetros.'.format(metro=meter, centimetros=centimeter)
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)    
                

        
        return (
            handler_input.response_builder
                .speak(speak_output)
            #    .ask(reprompt)
                .response
        )

########################################## RESPONSAVEL PELA ALTURA ###################################################
########################################## RESPONSAVEL PELA ALTURA ###################################################

########################################## RESPONSAVEL PELA PRESSAO ##################################################
########################################## RESPONSAVEL PELA PRESSAO ##################################################

class PressaoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PressaoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        systolic = slots["sistolica"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        diastolic = slots["diastolica"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        

        attributes["Sistolica"] = systolic
        attributes["Diastolica"] = diastolic
        
        speak_output = 'Obrigada, lembrarei que a pressão é {sistolica} por {diastolica} \
        '.format(sistolica=systolic, diastolica=diastolic) 
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)    
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

########################################## RESPONSAVEL PELA PRESSAO ##################################################
########################################## RESPONSAVEL PELA PRESSAO ##################################################

######################################## RESPONSAVEL PELOS BATIMENTOS ################################################
######################################## RESPONSAVEL PELOS BATIMENTOS ################################################

class BatimentosIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BatimentosIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global attributes
        
        slots = handler_input.request_envelope.request.intent.slots # acessa todos os slotes 
        heartbeats = slots["batidas"].value  # pegar o valor do slot correspondente e armazena em uma variavel
        

        attributes["Batimentos"] = heartbeats
        
        speak_output = 'Obrigada, lembrarei que o batimentos cardíacos são {batimentos} \
                        '.format(batimentos=heartbeats) 
        if supportInterfaces(ask_utils.get_supported_interfaces(handler_input).alexa_presentation_apl) == True :
            textoToAPL(handler_input,speak_output)    
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

######################################## RESPONSAVEL PELOS BATIMENTOS ################################################
######################################## RESPONSAVEL PELOS BATIMENTOS ################################################



#********************************************** GUARDA INFOMAÇÕES **********************************************#
#********************************************** GUARDA INFOMAÇÕES **********************************************#
#********************************************** GUARDA INFOMAÇÕES **********************************************#
#********************************************** GUARDA INFOMAÇÕES **********************************************#



#********************************************** FUNÇÕES NECESSÁRIAS DA AMAZON **********************************************#
#********************************************** FUNÇÕES NECESSÁRIAS DA AMAZON **********************************************#
#********************************************** FUNÇÕES NECESSÁRIAS DA AMAZON **********************************************#

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Como posso ajudar?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Cancelado. Agora diga a próxima tarefa!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.


        speak_output = "Saindo. Até mais!"
        handler_input.response_builder.speak(speak_output)
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Desculpe, não entendi. Diga 'cancelar' e tente novamente!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

#********************************************** FUNÇÕES NECESSÁRIAS DA AMAZON **********************************************#
#********************************************** FUNÇÕES NECESSÁRIAS DA AMAZON **********************************************#
#********************************************** FUNÇÕES NECESSÁRIAS DA AMAZON **********************************************#



#********************************************** MAIN **********************************************#
#********************************************** MAIN **********************************************#
#********************************************** MAIN **********************************************#

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = CustomSkillBuilder()


###################################### obter dados ############################

###################################### cadastro ###################################
sb.add_request_handler(ObterEmailIntentHandler())
sb.add_request_handler(ObterCelularIntentHandler())
sb.add_request_handler(ObterTelefoneIntentHandler())
sb.add_request_handler(ObterEstadoCivilIntentHandler())
sb.add_request_handler(ObterNaturalidadeIntentHandler())
sb.add_request_handler(ObterNacionalidadeIntentHandler())
sb.add_request_handler(ObterSexoIntentHandler())
sb.add_request_handler(ObterOrgaoExpedidorIntentHandler())
sb.add_request_handler(ObterCPFIntentHandler())
sb.add_request_handler(ObterProfissaoIntentHandler())
sb.add_request_handler(ObterRegistroGeralIntentHandler())
sb.add_request_handler(ObterDataIntentHandler())
sb.add_request_handler(ObterNomeIntentHandler())
sb.add_request_handler(ObterIdadeIntentHandler())
sb.add_request_handler(ObterBatimentosIntentHandler())
sb.add_request_handler(ObterAlturaIntentHandler())
sb.add_request_handler(ObterPressaoIntentHandler())
sb.add_request_handler(ObterPesoIntentHandler())
sb.add_request_handler(ObterNascimentoIntentHandler())

###################################### PRINCIPAL ##############################
sb.add_request_handler(LaunchRequestHandler())
###################################### PRINCIPAL ##############################

###################################### armazenar dados ########################

###################################### cadastro ###############################
sb.add_request_handler(EmailIntentHandler())
sb.add_request_handler(CelularIntentHandler())
sb.add_request_handler(TelefoneIntentHandler())
sb.add_request_handler(EstadoCivilIntentHandler())
sb.add_request_handler(NacionalidadeIntentHandler())
sb.add_request_handler(NaturalidadeIntentHandler())
sb.add_request_handler(CPFIntentHandler())
sb.add_request_handler(SexoIntentHandler())
sb.add_request_handler(NomeIntentHandler())
sb.add_request_handler(ProfissaoIntentHandler())
sb.add_request_handler(SalvarCadastroIntentHandler())
sb.add_request_handler(RegistroGeralIntentHandler())
sb.add_request_handler(OrgaoExpedidorIntentHandler())
sb.add_request_handler(NacimentoIntentHandler())
sb.add_request_handler(AlturaIntentHandler())
sb.add_request_handler(PesoIntentHandler())
sb.add_request_handler(PressaoIntentHandler())
sb.add_request_handler(BatimentosIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler()) 

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()