import re
import html
import requests
import warnings
from bs4 import BeautifulSoup
from datetime import datetime
from app.api.core.social import *

# Ignora i warning di BeautifulSoup quando incontra HTML malformato o un link, mentre si aspetta un HTML completo
warnings.filterwarnings("ignore")


class ChanWrapper(SocialWrapper):
    """
    Wrapper per l'API di 4chan, in particolare per la board /biz/ (Business & Finance)
    Fonte API: https://a.4cdn.org/biz/catalog.json
    """
    def __init__(self):
        super().__init__()

    def __time_str(self, timestamp: str) -> int:
        """Converte una stringa da MM/GG/AA(DAY)HH:MM:SS di 4chan a millisecondi"""
        time = datetime.strptime(timestamp, "%m/%d/%y(%a)%H:%M:%S")
        return int(time.timestamp() * 1000)

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

                # una lista di dizionari conteneti le risposte al thread principale, sono strutturate similarmente al thread
                response_list = thread.get('last_replies', [])
                comments_list: list[SocialComment] = []

                for i, response in enumerate(response_list):
                    if i >= MAX_COMMENTS: break

                    # la data di creazione della risposta tipo "MM/GG/AA(day)hh:mm:ss", ci interessa solo MM/GG/AA
                    time = self.__time_str(response['now'])

                    # il commento della risposta, può contenere anche elementi di formattazione html che saranno da ignorare
                    comment = self.__unformat_html_str(response.get('com', ''))
                    if not comment:
                        continue

                    social_comment = SocialComment(description=comment)
                    social_comment.set_timestamp(timestamp_ms=time)
                    comments_list.append(social_comment)

                social_post: SocialPost = SocialPost(
                    title=title,
                    description=thread_description,
                    comments=comments_list
                )
                social_post.set_timestamp(timestamp_ms=time)
                social_posts.append(social_post)

        return social_posts[:limit]
