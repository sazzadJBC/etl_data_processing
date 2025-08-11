import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery, Rerank, Filter


class WeaviateClient:
    def __init__(
        self,
        collection_name="DemoCollection",
        properties=None,
        embedding_provider="jina",          # "jina" or "openai"
        embedding_model=None                # optional model name
    ):
        load_dotenv(override=True)
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider.lower()
        self.embedding_model = embedding_model
        self.properties_config = properties or [
            {"name": "text", "data_type": DataType.TEXT, "vectorize_property": True},
            {"name": "source", "data_type": DataType.TEXT, "vectorize_property": False}
        ]
        self.client = self._connect()
        self.collection = self._create_collection()

    def _connect(self):
        headers = {}
        if self.embedding_provider == "jina":
            headers["X-JinaAI-Api-Key"] = os.getenv("JINAAI_API_KEY")
        elif self.embedding_provider == "openai":
            headers["X-OpenAI-Api-Key"] = os.getenv("OPENAI_API_KEY")
        return weaviate.connect_to_local(headers=headers)

    def _vector_config(self):
        """Return vector_config based on embedding provider."""
        vectorize_props = [p["name"] for p in self.properties_config if p.get("vectorize_property")]

        if self.embedding_provider == "jina":
            return Configure.Vectors.text2vec_jinaai(
                name="text_vector",
                model=self.embedding_model or "jina-embeddings-v3",
                source_properties=vectorize_props
            )

        elif self.embedding_provider == "openai":
            return Configure.Vectors.text2vec_openai(
                name="text_vector",
                model=self.embedding_model or "text-embedding-3-small",
                source_properties=vectorize_props
            )

        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")

    def _create_collection(self):
        if self.collection_name in self.client.collections.list_all():
            print(f"Collection '{self.collection_name}' already exists. Using existing collection.")
            return self.client.collections.get(self.collection_name)

        print(f"Creating collection '{self.collection_name}'...")
        properties_list = [Property(**prop) for prop in self.properties_config]

        return self.client.collections.create(
            self.collection_name,
            vector_config=self._vector_config(),
            #reranker_config=Configure.Reranker.jinaai("jina-reranker-v2-base-multilingual"),
            properties=properties_list
        )

    def insert_data_from_lists(self, **kwargs):
        lengths = {len(v) for v in kwargs.values()}

        if len(lengths) != 1:
            raise ValueError("All property lists must have the same length.")
        data = [dict(zip(kwargs.keys(), vals)) for vals in zip(*kwargs.values())]
        print(f"📥 Inserting {len(data)} items...")
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
            return_properties=[prop["name"] for prop in self.properties_config]
        )
        for i, obj in enumerate(response.objects, start=1):
            print(f"Result #{i}:")
            for prop in self.properties_config:
                name = prop["name"]
                print(f"{name}:", obj.properties.get(name))
            print("Distance:", obj.metadata.distance)
            print("Rerank Score:", obj.metadata.rerank_score)
            print("---")

    def delete_by_source(self, file_source: str):
        print(f"🗑️ Attempting to delete objects with source: {file_source}")
        result = self.collection.data.delete_many(
            where=Filter.by_property("source").equal(file_source)
        )
        print(f"Successfully Deleted {result.matches} and failed {result.failed}")


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
    sources = [
        "file1.txt",
        "file2.txt",
        "file3.txt","file1.txt",
        "file2.txt",
        "file3.txt","file1.txt",
        "file2.txt",
        "file3.txt"
    ]

    props = [
    {"name": "text", "data_type": DataType.TEXT, "vectorize_property": True},
    {"name": "source", "data_type": DataType.TEXT, "vectorize_property": False},
    #{"name": "category", "data_type": DataType.TEXT, "vectorize_property": False}
    ]

    # With Jina embeddings
    client = WeaviateClient(
        collection_name="JinaCollection",
        embedding_provider="jina",
        embedding_model="jina-embeddings-v3",
        properties=props
    )
    client.insert_data_from_lists(text= texts,source= sources)
    client.query_data("ওইণ্ডিয়ান ফীল্ড")
    # client.delete_by_source("file1.txt")
    
