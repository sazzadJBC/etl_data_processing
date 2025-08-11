from src.website_data_transformation.wordpress_data_processor import WordpressDataProcessor
from dotenv import load_dotenv
load_dotenv()
from src.weaviate_utils import WeaviateClient
from weaviate.classes.config import DataType
property_config = [
    {"name": "text", "data_type": DataType.TEXT, "vectorize_property": True},
    {"name": "source", "data_type": DataType.TEXT, "vectorize_property": False},
    {"name": "image_urls", "data_type": DataType.TEXT, "vectorize_property": False},
    {"name": "youtube_urls", "data_type": DataType.TEXT, "vectorize_property": False}
]
weaviate_client = WeaviateClient(
    collection_name="Business_data_collection",
    embedding_provider="openai",
    properties=property_config
)

processor = WordpressDataProcessor()
texts, source_urls, image_urls, youtube_urls = processor.process()
print("texts len", len(texts))  # Print length of texts for verification
print("source_urls len", len(source_urls))  # Print length of source URLs for verification
print("image_urls len", len(image_urls))  # Print length of image URLs for verification
print("youtube_urls len", len(youtube_urls))  # Print length of YouTube URLs
print("Texts type", type(texts))  # Print first 2 texts for verification
print("Source URLs type", type(source_urls))  # Print first 2 source URLs for verification
print("Image URLs type", type(image_urls))  # Print first 2 image URLs for
print("Youtube URLs type", type(youtube_urls))  # Print first 2 YouTube URLs for verification

weaviate_client.insert_data_from_lists(
    text=texts,
    source=source_urls,
    image_urls=image_urls,
    youtube_urls=youtube_urls,
)
# processor.save_to_weaviate(weaviate_client)
