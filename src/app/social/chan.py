'''
Usiamo le API di 4chan per ottenere un catalogo di threads dalla board /biz/
'''
import requests
import re
import html
from bs4 import BeautifulSoup

from .base import SocialWrapper, SocialPost, SocialComment
class ChanWrapper(SocialWrapper):
    def __init__(self):
        super().__init__()

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        # Url dell'API della board /biz/
        json_url = 'https://a.4cdn.org/biz/catalog.json'
        json = requests.get(json_url)

        if json.status_code == 200:
            page_list: list[dict] = json.json() # Questa lista contiene un dizionario per ogni pagina della board di questo tipo {"page": page_number, "threads": [{thread_data}]}
        else:
            print("Error:", json.status_code)

        # Lista dei post
        social_posts: list[SocialPost] = []

        for page in page_list:
            thread_list: list[dict] = page['threads']
            '''
            Per ogni thread ci interessano i seguenti campi:
            - "sticky": ci indica se il thread è stato fissato o meno, se non è presente vuol dire che non è stato fissato, i thread sticky possono essere ignorati
            - "now": la data di creazione del thread tipo "MM/GG/AA(day)hh:mm:ss", ci interessa solo MM/GG/AA
            - "name": il nome dell'utente
            - "sub": il nome del thread, può contenere anche elementi di formattazione html che saranno da ignorare, potrebbe non essere presente
            - "com": il commento del thread, può contenere anche elementi di formattazione html che saranno da ignorare
            - "last_replies": una lista di dizionari conteneti le risposte al thread principale, sono strutturate similarmente al thread, di queste ci interessano i seguenti campi:
                - "now": la data di creazione della risposta tipo "MM/GG/AA(day)hh:mm:ss", ci interessa solo MM/GG/AA
                - "name": il nome dell'utente
                - "com": il commento della risposta, possono contenere anche elementi di formattazione html che saranno da ignorare
            '''
            for thread in thread_list:
                # Ignoriamo i dizionari dei thread nei quali è presente la key "sticky"
                if 'sticky' in thread:
                    continue
                else:
                    # print(thread)
                    # Otteniamo la data 
                    time: str = thread['now']
                    # Otteniamo dalla data il mese (primi 2 caratteri)
                    month: str = time[:2]
                    # Otteniamo dalla data il giorno (caratteri 4 e 5)
                    day: str = time[4:6]
                    # Otteniamo dalla data l'anno (caratteri 7 e 8)
                    year: str = time[7:9]
                    # Ricreiamo la data completa come dd/mm/yy
                    time: str = day + '/' + month + '/' + year
                    
                    # Otteniamo il nome dell'utente
                    name: str = thread['name']
                    # Proviamo a recuperare il titolo
                    try:
                        # Otteniamo il titolo del thread contenuto nella key "sub"
                        title: str = thread['sub']
                        # Ripuliamo la stringa
                        # Decodifichiamo caratteri ed entità HTML
                        html_entities = html.unescape(title)
                        # Rimuoviamo caratteri HTML
                        soup = BeautifulSoup(html_entities, 'html.parser')
                        title = soup.get_text(separator=" ")
                        # Rimuoviamo backlash e doppi slash
                        title = re.sub(r"[\\/]+", "/", title)
                        # Rimuoviamo spazi in piú
                        title = re.sub(r"\s+", " ", title).strip()
                        # Aggiungiamo il nome dell'utente al titolo
                        title = name + " posted: " + title
                    except:
                        title: str = name + " posted"

                    try: 
                        # Otteniamo il commento del thread contenuto nella key "com"
                        thread_description: str = thread['com']
                        # Ripuliamo la stringa
                        # Decodifichiamo caratteri ed entità HTML
                        html_entities = html.unescape(thread_description)
                        # Rimuoviamo caratteri HTML
                        soup = BeautifulSoup(html_entities, 'html.parser')
                        thread_description = soup.get_text(separator=" ")
                        # Rimuoviamo backlash e doppi slash
                        thread_description = re.sub(r"[\\/]+", "/", thread_description)
                        # Rimuoviamo spazi in piú
                        thread_description = re.sub(r"\s+", " ", thread_description).strip()
                    except:
                        thread_description = None
                    # Creiamo la lista delle risposte al thread
                    try:
                        response_list: list[dict] = thread['last_replies']
                    except:
                        response_list: list[dict] = []
                    # Creiamo la lista che conterrà i commenti
                    comments_list: list[SocialComment] = []

                    # Otteniamo i primi 5 commenti
                    i = 0
                    for response in response_list:
                        # Otteniamo la data 
                        time: str = response['now']
                        # print(time)
                        # Otteniamo dalla data il mese (primi 2 caratteri)
                        month: str = time[:2]
                        # Otteniamo dalla data il giorno (caratteri 4 e 5)
                        day: str = time[3:5]
                        # Otteniamo dalla data l'anno (caratteri 7 e 8)
                        year: str = time[6:8]
                        # Ricreiamo la data completa come dd/mm/yy
                        time: str = day + '/' + month + '/' + year

                        try: 
                            # Otteniamo il commento della risposta contenuto nella key "com"
                            comment_description: str = response['com']
                            # Ripuliamo la stringa
                            # Decodifichiamo caratteri ed entità HTML
                            html_entities = html.unescape(comment_description)
                            # Rimuoviamo caratteri HTML
                            soup = BeautifulSoup(html_entities, 'html.parser')
                            comment_description = soup.get_text(separator=" ")
                            # Rimuoviamo backlash e doppi slash
                            comment_description = re.sub(r"[\\/]+", "/", comment_description)
                            # Rimuoviamo spazi in piú
                            comment_description = re.sub(r"\s+", " ", comment_description).strip()
                        except:
                            comment_description = None
                        # Se la descrizione del commento non esiste, passiamo al commento successivo
                        if comment_description is None:
                            continue
                        else:
                            # Creiamo il SocialComment
                            social_comment: SocialComment = SocialComment(
                                time=time,
                                description=comment_description
                            )
                            comments_list.append(social_comment)
                        i += 1
                        if i >= 5:
                            break
                    if thread_description is None:
                        continue
                    else:
                        # Creiamo il SocialPost
                        social_post: SocialPost = SocialPost(
                            time=time,
                            title=title,
                            description=thread_description,
                            comments=comments_list
                        )
                        social_posts.append(social_post)
        
        return social_posts[:limit]           
# Stampiamo i post
# chan_wrapper = ChanWrapper()
# social_posts = chan_wrapper.get_top_crypto_posts()
# print(len(social_posts))
