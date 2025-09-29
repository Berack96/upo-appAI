#### FOR ALL FILES OUTSIDE src/ FOLDER ####
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
###########################################

from dotenv import load_dotenv
from app.news import NewsAPI

def main():
    api = NewsAPI()
    print("ok")

if __name__ == "__main__":
    load_dotenv()
    main()