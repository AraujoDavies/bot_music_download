link_playlist_ytb = 'https://www.youtube.com/playlist?list=PL5YuyGlpvBaQUZhiEXLasPMOS56KNTmyr'

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import os
import json
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Sessão de variaveis
path_to_downloads = "C:\\Users\\MrRobot\\Downloads\\music_download\\"
path_to_musics = "C:\\Users\\MrRobot\\Music\\"
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36' # se tiver "headless" no user_agent o site bloqueia o acesso
options.add_argument('user-agent={0}'.format(user_agent))
nao_rodar_em_headless = True
#options.add_argument('--headless')
#options.add_argument('--no-sandbox')
#options.add_argument('--mute-audio')
# options.add_argument("user-data-dir=C:\\Users\\MrRobot\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 4") #Path to your chrome profile
prefs = {"download.default_directory" : path_to_downloads}
options.add_experimental_option("prefs",prefs)
c = webdriver.Chrome(service=service)
wdw = WebDriverWait(c, 60, 10)

def new_url_ytb(url):
    """ Encurta o tamanho da URL do Ytb"""
    a = url.split('&')
    return a[0]
    
def pegando_urls_no_ytb(link):
    """crawl da playlist do youtube e retorna ela em DICT"""
    try:
        c.get(link)

        sleep(20)
        videos = c.find_elements(By.XPATH, "//a[@id = 'video-title']")
    
        urls = []
        for hrefs in videos:
            dict = {}
            dict['title'] = hrefs.get_attribute("innerHTML").replace('\n          ', '').replace('\n        ', '')
            dict['url'] = new_url_ytb(hrefs.get_attribute("href"))
            urls.append(dict)

        print(f'total de URLs: {len(urls)}')
        return urls
    except:
        return "ERRO ao pegar URLS da playlist no Youtube."

def espera_download():
    """ Pergunta: Tem algum item em processo de download ou o diretório está vázio ? """
    sleep(3)
    mb = os.listdir(path_to_downloads)

    for item in mb:
        if item == 'desktop.ini':
            mb.remove('desktop.ini')
        if ".crdownload" in item:
            # Se tiver item em download 
            # print(item)
            return True

    if len(mb) == 0: #se diretório está vazio
        return True

    print(mb)
    return False

def mover_arquivos():
    """mover os arquivos do diretório de downloads para music"""

    mb = os.listdir(path_to_downloads)

    for i in mb:
        if i == 'desktop.ini':
            mb.remove('desktop.ini')
        os.replace(path_to_downloads+i, f'{path_to_musics}{i}')

# Defs do onlymp3.to
def automacao_only_mp3(url_msc):
        """Recebe uma url de um video e Faz as ações dentro do site de download"""
        site = "https://pt.onlymp3.to"
        c.get(site)

        search_bar = c.find_element(By.ID, "txtUrl")
        search_bar.send_keys(url_msc)
        
        sleep(1)
        convert_btn = c.find_element(By.CLASS_NAME, "start-btn")
        convert_btn.click()
        print('Click p conversão realizado')
        try:
            wdw.until(lambda c: c.find_element(By.XPATH, "//button[@class='btn']"), "Esperando btn de download")

            sleep(1)
            download_btn = c.find_element(By.XPATH, "//button[@class='btn']")
            download_btn.click()
            if bool(download_btn):
                print('Click p Download realizado')
                if download_404_onlymp3to():
                    return False # false se o download nao foi realizado por 404
                return True # se o download foi realizado
            else:
                return False # false se o download nao foi realizado
        except:
            print('Erro - nao encontrou botão de Download')
            return False # false se o download nao foi realizado

def renomear_arquivos_onlymp3to():
    """Renomeia os arquivos no diretório de downloads"""
    mb = os.listdir(path_to_downloads)

    for i in mb:
        if i == 'desktop.ini':
            mb.remove('desktop.ini')
        new_i = i.replace('onlymp3.to - ', '')
        os.replace(path_to_downloads+i, f'{path_to_downloads}{new_i[:-35]}.mp3')

def download_404_onlymp3to():
    """
        Pergunta: ao clicar em download foi redirecionado para uma página de 404 ?
    """
    try:
        pagina_404 = c.find_element(By.XPATH, '//body[@id = "t"]')
        if bool(pagina_404):
            return True
    except:
        return False


# PROCESSO DE EXECUÇÃO

if 'urls_ytb' in globals(): # se a variavel já foi declarada...
    if len(urls_ytb) > 0:
        print(f'Não precisará fazer scrapy no ytb... Qt de Urls: {len(urls_ytb)}')
    elif len(urls_ytb) == 0:
        print('Não há itens para ser baixado na definição das urls')
    else: # senão tem itens na lista...
        urls_ytb = pegando_urls_no_ytb(link_playlist_ytb)
else: # senão foi declarada a variavel
    urls_ytb = pegando_urls_no_ytb(link_playlist_ytb)

c.quit()

if nao_rodar_em_headless:
    c = webdriver.Chrome(service=service)
    wdw = WebDriverWait(c, 60, 2)
else:
    c = webdriver.Chrome(service=service, options=options)
    wdw = WebDriverWait(c, 60, 2)

qt_mscs_baixadas = 0 # quantas musicas foram baixadas ?
contador = 0 # qt de tentativas de download
tentativas_download_while = 1 # qt de tentativas dentro do while
tomaram_timeout = []
erro_execucao = []
response_404 = []
while tentativas_download_while < 4: # vai tentar 3x enquanto ter item na lista
    if bool(urls_ytb):
        print(f'iniciando a {tentativas_download_while}° Tentativa')
        tentativas_download_while += 1 
        for msc in urls_ytb:
            contador += 1
            try:
                sucesso_no_download = False
                print(f'Inicio da música {msc["title"]}...')
                if automacao_only_mp3(msc['url']):
                    print('esperando download...')
                    # Enquanto espera download... 
                    timeout = 0
                    while espera_download():
                        timeout += 1
                        sucesso_no_download = True
                        # print('Esperando o download terminar...') #ajuda a debugar :D
                        sleep(2) # vezes a quantidade timeout = 60 segundos
                        if timeout > 10:
                            # Vai dar timeout se nao fizer o download em X segundos
                            print(f'TIMEOUT na música {msc["title"]}')
                            sucesso_no_download = False
                            tomaram_timeout.append(msc)
                            urls_ytb.remove(msc)
                            break

                    if sucesso_no_download:
                        print(f"Download concluído: {msc['title']}")
                        urls_ytb.remove(msc)
                        renomear_arquivos_onlymp3to()
                        mover_arquivos()                    
                        qt_mscs_baixadas += 1
                else:
                    """

                    Plano: adicionar segundo site de download


                    """
                    if download_404_onlymp3to():
                        print(f'server 404 para a música {msc["title"]}')
                        response_404.append(msc)                        
                        urls_ytb.remove(msc)
                    else:
                        erro_execucao.append(msc)
                        urls_ytb.remove(msc)
                        print(f'Falha no Download de {msc["title"]}')
                print(f'Fim da música {msc["title"]}')                            
            except:
                print(f'Erro na música: {msc["title"]}')
                erro_execucao.append(msc)
                urls_ytb.remove(msc)

            # Reiniciar browser quando quantidade de tentativas for divisor de 10
            dez_msc = contador % 10
            if dez_msc == 0 and contador != 0:
                print('reiniciando browser...')
                c.quit()
                if nao_rodar_em_headless:
                    c = webdriver.Chrome(service=service)
                    wdw = WebDriverWait(c, 60, 2)
                else:
                    c = webdriver.Chrome(service=service, options=options)
                    wdw = WebDriverWait(c, 60, 2)

            print(f'Tentativa: {contador}. Número de itens restantes: {len(urls_ytb)}')
            print('Músicas baixadas até agora = {}'.format(qt_mscs_baixadas))
    else:    
        print('Não há itens para ser baixado dentro do while')

print('urls do youtube: {}'.format(urls_ytb))
print('Erro na execução do código: {}'.format(erro_execucao))
print('timeout: {}'.format(tomaram_timeout))
print('servidor 404: {}'.format(response_404))

urls_ytb2 = urls_ytb.copy()
urls_ytb = urls_ytb2 + erro_execucao + tomaram_timeout + response_404
numero_de_urls = str(len(urls_ytb))

print('Quantidade de músicas baixadas: {}'.format(qt_mscs_baixadas))
print('Quantidade de URLs que não foram baixadas: {}'.format(len(urls_ytb)))

if bool(urls_ytb):
    print('há itens para ser baixado')
    c.quit()
else:
    print('processo finalizado com sucesso!')
    c.quit()