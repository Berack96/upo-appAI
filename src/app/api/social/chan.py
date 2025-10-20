'''
Usiamo le API di 4chan per ottenere un catalogo di threads dalla board /biz/
'''
import re
import html
import requests
from bs4 import BeautifulSoup
from app.api.core.social import *


class ChanWrapper(SocialWrapper):
    def __init__(self):
        super().__init__()

    def __time_str(self, timestamp: str) -> str:
        """Converte una stringa da MM/GG/AA di timestamp nel formato GG/MM/AA"""
        if len(timestamp) < 8: return ""

        month = timestamp[:2]
        day = timestamp[3:5]
        year = timestamp[6:8]
        return f"{day}/{month}/{year}"

    def __unformat_html_str(self, html_element: str) -> str:
        """Pulisce il commento rimuovendo HTML e formattazioni inutili"""
        if not html_element: return ""

        html_entities = html.unescape(html_element)
        soup = BeautifulSoup(html_entities, 'html.parser')
        html_element = soup.get_text(separator=" ")
        html_element = re.sub(r"[\\/]+", "/", html_element)
        html_element = re.sub(r"\s+", " ", html_element).strip()
        return html_element

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        url = 'https://a.4cdn.org/biz/catalog.json'
        response = requests.get(url)
        assert response.status_code == 200, f"Error in 4chan API request [{response.status_code}] {response.text}"

        social_posts: list[SocialPost] = []

        # Questa lista contiene un dizionario per ogni pagina della board di questo tipo {"page": page_number, "threads": [{thread_data}]}
        for page in response.json():
            for thread in page['threads']:

                # ci indica se il thread è stato fissato o meno, se non è presente vuol dire che non è stato fissato, i thread sticky possono essere ignorati
                if 'sticky' in thread:
                    continue

                # la data di creazione del thread tipo "MM/GG/AA(day)hh:mm:ss", ci interessa solo MM/GG/AA
                time = self.__time_str(thread.get('now', ''))

                # il nome dell'utente
                name: str = thread.get('name', 'Anonymous')

                # il nome del thread, può contenere anche elementi di formattazione html che saranno da ignorare, potrebbe non essere presente
                title = self.__unformat_html_str(thread.get('sub', ''))
                title = f"{name} posted: {title}"

                # il commento del thread, può contenere anche elementi di formattazione html che saranno da ignorare
                thread_description = self.__unformat_html_str(thread.get('com', ''))
                if not thread_description:
                    continue

                # una lista di dizionari conteneti le risposte al thread principale, sono strutturate similarmente al thread, di queste ci interessano i seguenti campi:
                # - "now": la data di creazione della risposta tipo "MM/GG/AA(day)hh:mm:ss", ci interessa solo MM/GG/AA
                # - "name": il nome dell'utente
                # - "com": il commento della risposta, possono contenere anche elementi di formattazione html che saranno da ignorare
                response_list = thread.get('last_replies', [])
                comments_list: list[SocialComment] = []

                for i, response in enumerate(response_list):
                    if i >= MAX_COMMENTS: break

                    time = self.__time_str(response['now'])

                    comment = self.__unformat_html_str(response.get('com', ''))
                    if not comment:
                        continue

                    social_comment = SocialComment(time=time, description=comment)
                    comments_list.append(social_comment)

                social_post: SocialPost = SocialPost(
                    time=time,
                    title=title,
                    description=thread_description,
                    comments=comments_list
                )
                social_posts.append(social_post)

        return social_posts[:limit]
