import wikipedia
import requests
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
import json
import os.path
import speech_recognition as escuta                                                                       
import os
import boto3
import vlc
import serial
from serial import SerialException
import time
import random
import pyttsx

#Criação do objeto da AWS
engine = pyttsx.init()
polly = boto3.client('polly')
##########################
SpeakError = False
global ArduinoAcessToken
ArduinoAcessToken = None
global count
count = 0
base = {}
confg = {}
global volume1
global voice1
global voiceType1
global name1
volume1 = 0
name1 = ''
voiceType1 = False
voice1 = 0



def activeConfg():
        global volume1
        global voice1
        global voiceType1
        global name1
        volume1 = confg['volume']
        voice1 = confg['voice']
        voiceType1 = confg['voiceType']
        name1 = confg['name']


#Função de configuração
def configMenu():
        global confg
        # inicia o loop para alimentar o arquivo de configurações com uma nova confg
        while True:
                op = input('Operation: ')
                if op == 'config':
                        name = input('User Name: ')
                        if(name == 'exit'):
                                break
                        else:
                                print('1 for local voice and 2 for online voice')
                                voiceType = input('VoiceType: ')
                                if (voiceType == 'exit'):
                                        confg['name'] = name
                                        confg['ALLIEStatus'] = True
                                        with open (file_find('config.json', 'confg'), 'w') as ler:
                                                json.dump(confg,ler)
                                        break
                                else:
                                        if voiceType == '1':
                                                confg['voiceType'] = False
                                        else:
                                                confg['voiceType'] = True
                                                
                                        print('if voiceType is local report voiceID or voiceType online report voiceName')

                                        if(voiceType == '1'):
                                                while True:
                                                        try:
                                                               voice = (input('Voice: '))
                                                               if  (voice == 'exit'):
                                                                       confg['name'] = name
                                                                       confg['voiceType'] = voiceType
                                                                       with open (file_find('config.json', 'confg'), 'w') as ler:
                                                                               json.dump(confg,ler)
                                                                               break

                                                               voice = int(voice)
                                                               break
                                                        except ValueError:
                                                                print('Previous information does not look like an ID')
                                        else:
                                                while True:
                                                        try: 
                                                               voice = str(input('Voice: '))
                                                               if(int(voice) >= 0):
                                                                       aux = ''
                                                                       aux += 1
                                                        except TypeError:
                                                                print('Previous information does not look like a VoiceName')
                                                        except ValueError:
                                                               break
                                                
                                                
                                        if  (voice == 'exit'):
                                                confg['name'] = name
                                                confg['voiceType'] = voiceType
                                                with open (file_find('config.json', 'confg'), 'w') as ler:
                                                        json.dump(confg,ler)
                                                break
                                        else:
                                                volume = input('Volume: ')
                                                confg['name'] = name
                                                confg['voice'] = voice
                                                confg['ALLIEStatus'] = True
                                                confg['volume'] = int(volume)
                                                break
                        
                elif op == 'listVoices':
                        try:
                                if (confg['ALLIEStatus'] == True and confg['voiceType'] == True):
                                        print(polly.describe_voices())
                                        
                                elif (confg['voiceType'] == False):
                                        voices = engine.getProperty('voices')
                                        count = 0
                                        for voice in voices:
                                                print(count,voice.name.encode("utf-8"))
                                                count += 1
                        except UnicodeEncodeError:
                                pass

                elif op == 'configVoiceType':
                        print('1 for local voice and 2 for online voice')
                        aux = input('VoiceType: ')
                        if aux == '1':
                                confg['voiceType'] = False
                        else:
                                confg['voiceType'] = True
                        print('Success setup')
                        break

                elif op == 'configVolume':
                        vol = int(input('Volume: '))
                        confg['volume'] = vol
                        print('Success setup')
                        break

                elif op == 'configVoice':
                        print('if voiceType is local report voiceID or voiceType online report voiceName')
                        if confg['voiceType'] == False:
                                while True:
                                        try:
                                                voice = (input('Voice: '))
                                                if(voice == 'exit'):
                                                        break
                                                voice = int(voice)
                                                break
                                        except ValueError:
                                                print('Previous information does not look like an ID')
                                                
                        else:
                                while True:
                                        try:
                                                voice = str(input('Voice: '))
                                                if(voice == 'exit'):
                                                        break
                                                if(int(voice) >= 0):
                                                        aux = ''
                                                        aux += 1
                                        except TypeError:
                                                print('Previous information does not look like a VoiceName')
                                        except ValueError:
                                                break
                        confg['voice'] = voice
                        print('Success setup')
                        break

                elif op == 'help':
                        print('commands:')
                        print('config')
                        print('configVoiceType')
                        print('configVoice')
                        print('listVoices')
                        print('configVolume')
                        print('getConfig')
                        print('exit')

                elif op == 'getConfig':
                        print('UserName:', confg['name'], '\nVoice:', confg['voice'])
                        if confg['voiceType'] == False:
                                print('VoiceType: offline')
                        else:
                                print('VoiceType: online')

                elif op == 'exit':
                        break
                else:
                        print('The command is not valid')

        with open (file_find('config.json', 'confg'), 'w') as ler:
                json.dump(confg,ler)
                print('Successful all settings have been saved')
        with open (file_find('config.json', 'confg'), 'r') as ler:
                confg = json.load(ler)
        activeConfg()
                        
                                       

#Função responsavel por gerar um token de acesso aleatório
def GenerateArduinoToken():
        global ArduinoToken
        #Gera o token solicitado
        ArduinoToken = str(random.randint(234528765,986755489))
        temp = []
        #Ler o arquivo que contém os tokens e armazena em uma lista 
        with open(file_find('ArduinoToken.txt', 'ALLIEToken'), 'r') as output:
                ListaTemp = output.readlines()
        #Verifica se há algum token na lista se não ele escreve o token gerado
        if (len(ListaTemp) == 0):
                with open(file_find('ArduinoToken.txt', 'ALLIEToken'), "w") as output:
                        output.write(ArduinoToken)
        #Se houver mais de um token na lista ele escreve o novo token em uma nova linha
        else:
                for x in ListaTemp:
                        temp.append(x.strip())
                temp.append(ArduinoToken)
                
                with open(file_find('ArduinoToken.txt', 'ALLIEToken'), "w") as output:
                        for item in temp:
                                output.write("%s\n" % item)


        print('Generated Token:',ArduinoToken)
        return ArduinoToken
#Essa função conecta ALLIE a um dispositivo externo por intermédio de um Token de acesso
def ArduinoConect(token):
        global status
        global portas
        global StatusDeConexao
        global Arduinos
        
        #ler todos os tokens do arquino e armazena em "Tokens"
        with open(file_find('ArduinoToken.txt', 'ALLIEToken'), "r") as output:
                ListaTemp = output.readlines()
                Tokens = []
                for x in ListaTemp:
                        Tokens.append(x.strip())
        status = False
        #dicionário que guarda os arduino conectados 
        Arduinos = {}
        portas = []
        StatusDeConexao = False
        #Verifica quantos dispositivos estão conectados na máquina
        if (token in Tokens):
                for i in range(256):
                    try:
                        s = serial.Serial('COM'+str(i))
                        portas.append( (s.portstr))
                        s.close()
                    except serial.SerialException:
                        pass
                #Conecta o token ao arduino referente
                while (status == False and len(portas) != 0):
                        try:
                                for x in portas:
                                        #Envia o token para o dispositivo
                                        if(StatusDeConexao == False):
                                                LerPort = serial.Serial(x, 9600, timeout = 1)
                                                time.sleep(1.5)
                                                LerPort.write(token.encode())
                                        #Se o dispositivo responder um "ok" então o token pertence a ele
                                        if(LerPort.readline().decode().strip() == 'ok'):
                                                if(SpeakError == True):
                                                        player(file_find('ALLIEConexaoOk.mp3', 'ALLIE_Falas_Offline'))
                                                #Cria uma chave com o nome igual ao token e com o objeto da porta Serial
                                                Arduinos[token] = LerPort
                                                StatusDeConexao = True
                                                status = True

                        except SerialException:
                                if(SpeakError == True):
                                        player(file_find('ALLIErrorConect.mp3', 'ALLIE_Falas_Offline'))
                                        break
                                else:
                                        break
                                        return False
        else:
                return False
                
#Essa função ler tudo que um dispositivo externo esteja enviando, parâmetros necessários "Token do dispositivo" 
def ArduinoRead(token):       
        try:
                
                Arduinos[token].write(''.encode())
                return arduino.readline().decode().strip()
        except KeyError:
                return False
        except NameError:
                if(SpeakError == True):
                        player(file_find('ALLIERead.mp3', 'ALLIE_Falas_Offline'))
                else:
                        return False
#Esta função envia comandos para um dispositivo externo, parâmetros necessários "Token do dispositivo" e comando a ser enviado
def ArduinoCommand(token, command):
        temp = token
        temp += command
        Arduinos[token].write(temp.encode())


#Essa função treina o bot para responder perguntas sobre sua origem e também sobre A.I se arg = False ele trina só origens
def Aprender(arg = True):
        if (arg == True):
            conversa1 = open(file_find('origens.txt', 'conversas'), 'r').readlines()
            robot.train(conversa1)
            for arquivo in os.listdir(file_find('', 'conversas')):
                conversa = open(file_find('', 'conversas') +arquivo, 'r').readlines()
                robot.train(conversa)

        if(arg != True):
            conversa = open(file_find('', 'conversas') +arg, 'r').readlines()
            robot.train(conversa)

#Esta função identifica se o usuário que fazer uma busca sobre uma palavra chava, parâmentro frase
def Filtrar_Busca(txt):
        if (txt.startswith( 'O que é' ) == True):
            if (txt[8:].startswith( 'um' )):
                return txt[11:]
            elif (txt[8:].startswith( 'uma' )):
                return txt[12:]
            elif (txt[8:].startswith( 'a' )):
                return txt[10:]
            elif (txt[8:].startswith( 'o' )):
                return txt[10:]
            else:
                return txt[8:]
        if (txt.startswith( 'Quem é' ) == True):
            if (txt[7:].startswith( 'o' )):
               return txt[9:]
            elif (txt[7:].startswith( 'a' )):
               return txt[8:]
            else:
               return txt[6:]
        if (txt.startswith( 'O que significa' ) == True):
            if (txt[16:].startswith( 'o' )):
               return txt[18:]
            elif (txt[17:].startswith( 'a' )):
               return txt[8:]
            else:
               return txt[6:]
        if (txt.startswith( 'quem e' ) == True):
            return txt[7:]
        if (txt.startswith( 'O que e' ) == True):
            if (txt[8:].startswith( 'um' )):
                return txt[11:]
            elif (txt[8:].startswith( 'uma' )):
                return txt[12:]
            else:
                return txt[8:]
        if (txt.startswith( 'Pesquise por' ) == True):
            return txt[13:]
        if (txt.startswith( 'Busque por' ) == True):
            return txt[11:]
        if (txt.startswith( 'Me diga o que é' ) == True):
            return txt[16:]
        if (txt.startswith( 'Quem foi' ) == True):
            return txt[9:]
        if (txt.startswith( 'Pesquise' ) == True):
            return txt[9:]
        else:
            return False
#BETA esta função usar o microfone primário da máquina para converter voz em texto 
def Ouvir():
        with escuta.Microphone(1) as aux:                                                                       
            print("Fale:")
            ouvir.adjust_for_ambient_noise(aux)
            audio = ouvir.listen(aux)   
        try:
            print(ouvir.recognize_google(audio, language='pt-BR'))
            return (ouvir.recognize_google(audio, language='pt-BR'))
        except escuta.UnknownValueError:
            return False
        except escuta.RequestError as e:
            print("Could not request results; {0}".format(e))

#BETA função que converte palavras em voz multi idiomas usando a AWS ou idiomas nativos da máquina
def Falar(text,volume = 150, online = True, arq = True):
        if(voiceType1 == True):
            try:
                _ = requests.get('http://www.google.com/', timeout=5)
                texto = polly.synthesize_speech(Text= text, OutputFormat= 'mp3', VoiceId = voice1)
                with open(file_find('ALLIEspeak.mp3', ''), 'wb') as f:
                    f.write(texto['AudioStream'].read())
                    f.close()
                player(file_find('ALLIEspeak.mp3', ''))
            except requests.ConnectionError:
                player(file_find(file_find('Problema de rede.mp3', 'ALLIE_Falas_Offline')))
                
            if online != True and arq != True:
                player(file_find(file_find(arq, 'ALLIE_Falas_Offline')))
        else:
                engine.setProperty('voice', voice1)
                engine.say(text)
                engine.runAndWait()

#Esta função grava novas coisa aprendidas por ALLIE com buscas na internet    
def Gravar_dados (cod, descricao):
            base[cod] = descricao
            with open (file_find('base de dados.txt', ''), 'w') as ler:
                json.dump(base,ler)
#Este metódo busca o significado de termos na base de dados do wikipedia
def Buscar_Online(Busca):
    if (Busca in base):
            Falar(base[Busca])
    else:
        frase = 'Eu verifiquei no meu vocabulário, e não encontrei nada, sobre ' + Busca
        frase +=' , vou ver se consigo na internet, volto já !'
        Falar(frase)
        try:
            time.sleep(2)

            _ = requests.get('http://www.google.com/', timeout=5)
            try:
                sumario = wikipedia.summary(Busca, sentences=1)
                Falar(sumario)
                Gravar_dados(Busca, sumario)
            except wikipedia.exceptions.DisambiguationError as e:
                frase = "eu encontrei diversos resultados, para " + Busca
                frase += " , tente falar"
                Falar(frase)
                if (len(e.options) > 3):
                    for x in range(3):
                        Falar(e.options[x])
                   
            except wikipedia.exceptions.PageError:
                frase = "Desculpe, mais minha pesquisa não retornou resultados, para," + palavra
                Falar(frase)

        except requests.ConnectionError:
            Falar('offline', False, file_find('Problema de rede.mp3', 'ALLIE_Falas_Offline'))
#Esta função é usada para fazer o bot lebrar de suas origem sempre
def Atualizar_Memoria():
   global count
   count += 1
   if (count == 10):
      for x in range(4):
         robot.train(["como você se chama" , "one bote",
                      "qual é o seu nome", "me chamo one bote",
                      "quem te criou", "klinsman, considéro ele como um pai",
                      "você tem namorada","não fui programado para amar, sou apenas um sistema inteligênte, rodando em corpo robótico",
                      "quem te criou" , "klinsman","quem te fez" , "klinsman","qual é o nome do seu pai" , "klinsman"])
      count = 0
#Esse metódo recebe uma perguta e retorna uma resposta
def Dialogar(txt):
        if (Filtrar_Busca(txt) == False):
            print(robot.get_response(txt))    
            return robot.get_response(txt)
        else:
            return False

def file_find(filename, folder):
        directory = str(os.path.abspath(__file__))
        nwd = folder + '/' + filename
        newDirectory = directory.replace('allie.py', nwd)
        return newDirectory

def player(file):
    instance = vlc.Instance()
    media = instance.media_new(file)
    player = instance.media_player_new()
    player.set_media(media)
    player.play()
    playing = set([1,2,3,4])
    time.sleep(0.01)

    while True:
        state = player.get_state()
        if state not in playing:
            break
        

if os.path.exists(file_find('base de dados.txt', '')):
        with open (file_find('base de dados.txt', ''), 'r') as ler:
                leituraBD = json.load(ler)
                base = leituraBD

if os.path.exists(file_find('ArduinoToken.txt', 'ALLIEToken')):
        with open (file_find('ArduinoToken.txt', 'ALLIEToken'), 'r') as ler:
                leituraBD = ler.readlines()
                ArduinoAcessToken = leituraBD
else:
        with open (file_find('ArduinoToken.txt', 'ALLIEToken'), 'w') as ler:
                pass


# verifica se o arquivo de confg exite se sim todas as configurações são lidas
if os.path.exists(file_find('config.json', 'confg')):
        with open (file_find('config.json', 'confg'), 'r') as ler:
                confg = json.load(ler)
# se não é então criado um novo arquivo de con cofiguração com as configurções default
else:
        confg = {'voice': 0, 'volume': 100, 'ALLIEStatus':False, 'name':'', 'voiceType':False}
        player(file_find('ALLIEConfigNot.mp3', 'ALLIE_Falas_Offline'))
        configMenu()

if(confg['ALLIEStatus'] == False):
        player(file_find('ALLIEConfigNot.mp3', 'ALLIE_Falas_Offline'))
        configMenu()





estilo = []
pesquisa = []


activeConfg()
ouvir = escuta.Recognizer()
wikipedia.set_lang("Pt")
robot = ChatBot("one")
robot.set_trainer(ListTrainer)
#ArduinoConect('614209379')
#ArduinoCommand('614209379', 'teste')
#time.sleep(2)
#Arduinos['548800350'].write('bla'.encode())
#GenerateArduinoToken()
#ArduinoRead()
#configMenu()



#robot.train(["quem te criou" , "klinsman","quem te fez" , "klinsman","qual é o nome do seu pai" , "klinsman"])
'''
robot.train(
    "chatterbot.corpus.portuguese.greetings")

robot.train(
    "chatterbot.corpus.portuguese.conversations")
robot.train(
    "chatterbot.corpus.portuguese.linguistic_knowledge")
robot.train(
    "chatterbot.corpus.portuguese.proverbs")
robot.train("chatterbot.corpus.portuguese.suggestions")
'''

#Gravar_dados ('mercurio quimica', 'Mercúrio é um metal líquido à temperatura ambiente, conhecido desde os tempos da Grécia Antiga. Também é conhecido como hidrargírio, hidrargiro, azougue e prata-viva, entre outras denominações.')
'''
with open ('conversa.txt', 'r') as ler:
        leituraBD = ler.readlines()
        robot.train(leituraBD)

'''

   
