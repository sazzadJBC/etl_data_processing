import weaviate
import os
from weaviate.classes.query import MetadataQuery
from weaviate.classes.query import Rerank
from dotenv import load_dotenv
load_dotenv(override=True  )
headers = {
    "X-JinaAI-Api-Key": os.getenv("JINAAI_API_KEY")
}
client = weaviate.connect_to_local(headers=headers)

print("Collection list: ",client.collections.list_all())

collection = client.collections.get("Business_data_collection")


response = collection.query.near_text(
    query="MechanicsPOM cove",
    limit=5,
    rerank=Rerank(
        prop="text",
    ),
    return_metadata=MetadataQuery(distance=True),
    return_properties=["text","source"],
)
for o in response.objects:
    print(o.properties)
    print(o.metadata.distance)
    print(o.metadata.rerank_score)