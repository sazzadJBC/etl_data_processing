import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery, Rerank
from weaviate.classes.query import Filter



class WeaviateClient:
    def __init__(self, collection_name="DemoCollection"):
        load_dotenv(override=True)
        self.collection_name = collection_name
        self.client = self._connect()
        self.collection = self._create_collection()

    def _connect(self):
        headers = {
            "X-JinaAI-Api-Key": os.getenv("JINAAI_API_KEY")
        }
        return weaviate.connect_to_local(headers=headers)

    def _create_collection(self):
        if self.collection_name in self.client.collections.list_all():
            print(f"Collection '{self.collection_name}' already exists. Using existing collection.")
            return self.client.collections.get(self.collection_name)

        print(f"Creating collection '{self.collection_name}'...")
        return self.client.collections.create(
            self.collection_name,
            vector_config=Configure.Vectors.text2vec_jinaai(
                name="text_vector",
                model="jina-embeddings-v3",
                source_properties=["text"]
            ),
            reranker_config=Configure.Reranker.jinaai("jina-reranker-v2-base-multilingual"),
            properties=[
                Property(name="text", data_type=DataType.TEXT, vectorize_property=True),
                Property(name="path", data_type=DataType.TEXT, vectorize_property=False)
            ]
        )

    def insert_data_from_lists(self, texts, paths):
        if len(texts) != len(paths):
            raise ValueError("Length of texts and paths must be equal.")

        data = [{"text": t, "path": p} for t, p in zip(texts, paths)]
        print(f"📥 Inserting {len(data)} items with text and path...")
        response = self.collection.data.insert_many(data)
        if response.has_errors:
            print("❌ Insert Errors:")
            print(response.errors)
        else:
            print("✅ Insert complete.")

    def query_data(self, query_text, limit=5):
        print(f"\n🔍 Querying for: {query_text}\n")
        response = self.collection.query.near_text(
            query=query_text,
            limit=limit,
            rerank=Rerank(prop="text"),
            return_metadata=MetadataQuery(distance=True),
            return_properties=["text", "path"]
        )
        for i, obj in enumerate(response.objects, start=1):
            print(f"Result #{i}:")
            print("Text:", obj.properties.get("text"))
            print("Path:", obj.properties.get("path"))
            print("Distance:", obj.metadata.distance)
            print("Rerank Score:", obj.metadata.rerank_score)
            print("---")
    

    def delete_by_path(self, file_path: str):
        print(f"🗑️ Attempting to delete objects with path: {file_path}")
        
        # Build proper filter
        # where_filter = 

        result = self.collection.data.delete_many(
            where=Filter.by_property("path").equal(file_path)
        )
        print(f"Deletion result: {result}")
        # deleted_count = result.
        # .get('matches', 0)
        # if deleted_count > 0:
        #     print(f"✅ Deleted {deleted_count} object(s) with path '{file_path}'.")
        # else:
        #     print(f"⚠️ No objects found for path: {file_path}")


# ------------------------------
# ✅ Example usage
# ------------------------------
if __name__ == "__main__":
    texts = [
        "এই ডেটা বাংলায় লেখা হয়েছে।",
        "Indian field development is ongoing.",
        "ওইণ্ডিয়ান ফীল্ড একটি টার্গেট পয়েন্ট।",
        "এই ডেটা বাংলায় লেখা হয়েছে।",
        "Indian field development is ongoing.",
        "ওইণ্ডিয়ান ফীল্ড একটি টার্গেট পয়েন্ট।",
        "এই ডেটা বাংলায় লেখা হয়েছে।",
        "Indian field development is ongoing.",
        "ওইণ্ডিয়ান ফীল্ড একটি টার্গেট পয়েন্ট।"
    ]
    paths = [
        "file1.txt",
        "file2.txt",
        "file3.txt","file1.txt",
        "file2.txt",
        "file3.txt","file1.txt",
        "file2.txt",
        "file3.txt"
    ]

    client = WeaviateClient()
    client.insert_data_from_lists(texts, paths)
    # client.query_data("ওইণ্ডিয়ান ফীল্ড")
    # client.delete_by_path("file1.txt")
    
