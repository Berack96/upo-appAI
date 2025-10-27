from dotenv import load_dotenv
from app.api.tools import SocialAPIsTool

def main():
    api = SocialAPIsTool()
    articles_aggregated = api.get_top_crypto_posts_aggregated(limit_per_wrapper=2)
    for provider, posts in articles_aggregated.items():
        print("===================================")
        print(f"Provider: {provider}")
        for post in posts:
            print(f"== [{post.time}] - {post.title} ==")
            print(f"   {post.description}")
            print(f"   {len(post.comments)}")

if __name__ == "__main__":
    load_dotenv()
    main()
