import os
from src.website_data_transformation.wordpress_content_cleaner import WordpressContentCleaner

class WordpressDataProcessor:
    """Coordinates fetching and cleaning of WordPress product data."""

    def __init__(self):
        db_url = os.getenv("SOURCE_DB_URL","http://localhost:8080")  # ✅ Ensure this is set in your .env file
        if not db_url:
            raise ValueError("DB_URL environment variable not set")
        self.cleaner = WordpressContentCleaner(db_url)
        
    def process(self):
        """Fetches and cleans WordPress product data."""
        debug=os.getenv("DEBUG", "False").lower() == "true"
        rows = self.cleaner.fetch_products()
        texts = []
        youtube_urls_list = []
        image_urls_list = []
        source_urls_list = []

        for row in rows:
            image_urls_str =""
            youtube_urls_str = ""
            cleaned_content, image_urls, youtube_urls = self.cleaner.clean_and_extract(row.post_content)

            if debug:
                print(f"Post Title: {row.post_title}")
                print(f"Cleaned Content: {cleaned_content}")
                print(f"Post Summary: {row.post_summary}")
                print(f"Post Sub URL: https://www.sevensix.co.jp/products/{row.post_sub_url}")
                
                if image_urls:
                    print("Image URLs found:")
                    for url in image_urls:
                        print(f"  - {url}")

                if youtube_urls:
                    print("YouTube URLs found:")
                    for url in youtube_urls:
                        print(f"  - {url}")

                print("-" * 20,"*"*10, "-" * 20)
            if image_urls:
                for url in image_urls:
                    image_urls_str += f"{url}\n "

            if youtube_urls:
                for url in youtube_urls:
                    youtube_urls_str += f"{url}\n "

            texts.append(row.post_title + cleaned_content + row.post_summary)
            source_urls_list.append(f"https://www.sevensix.co.jp/products/{row.post_sub_url}")
            image_urls_list. append(image_urls_str)
            youtube_urls_list.append(youtube_urls_str)
        return texts, source_urls_list, image_urls_list, youtube_urls_list

if __name__ == "__main__":
    processor = WordpressDataProcessor()
    processor.process()
