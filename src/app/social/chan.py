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
                    time: str = thread['now']
                    month: str = time[:2]
                    day: str = time[4:6]
                    year: str = time[7:9]
                    time: str = day + '/' + month + '/' + year
                    
                    name: str = thread['name']
                    try:
                        title: str = thread['sub']
                        html_entities = html.unescape(title)
                        soup = BeautifulSoup(html_entities, 'html.parser')
                        title = soup.get_text(separator=" ")
                        title = re.sub(r"[\\/]+", "/", title)
                        title = re.sub(r"\s+", " ", title).strip()
                        title = name + " posted: " + title
                    except:
                        title: str = name + " posted"

                    try: 
                        thread_description: str = thread['com']
                        html_entities = html.unescape(thread_description)
                        soup = BeautifulSoup(html_entities, 'html.parser')
                        thread_description = soup.get_text(separator=" ")
                        thread_description = re.sub(r"[\\/]+", "/", thread_description)
                        thread_description = re.sub(r"\s+", " ", thread_description).strip()
                    except:
                        thread_description = None
                    try:
                        response_list: list[dict] = thread['last_replies']
                    except:
                        response_list: list[dict] = []
                    comments_list: list[SocialComment] = []

                    # Otteniamo i primi 5 commenti
                    i = 0
                    for response in response_list:
                        time: str = response['now']
                        month: str = time[:2]
                        day: str = time[3:5]
                        year: str = time[6:8]
                        time: str = day + '/' + month + '/' + year

                        try: 
                            comment_description: str = response['com']
                            html_entities = html.unescape(comment_description)
                            soup = BeautifulSoup(html_entities, 'html.parser')
                            comment_description = soup.get_text(separator=" ")
                            comment_description = re.sub(r"[\\/]+", "/", comment_description)
                            comment_description = re.sub(r"\s+", " ", comment_description).strip()
                        except:
                            comment_description = None
                        if comment_description is None:
                            continue
                        else:
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
