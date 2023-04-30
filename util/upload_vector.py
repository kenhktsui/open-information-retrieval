import json
from tqdm import tqdm
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models.models import VectorParams, Distance, OptimizersConfigDiff


collection_name = "wiki_collection"
upload_batch = 10000


qdrant_client = QdrantClient(host="localhost", port=6333, timeout=30)
existing_collections = qdrant_client.get_collections().collections
existing_collections = [i.name for i in existing_collections]
if collection_name not in existing_collections:
    # disable indexing
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=128, distance=Distance.DOT),
        optimizers_config=OptimizersConfigDiff(
            indexing_threshold=1000000000,
        ),
        shard_number=1
    )


def read_jsonl_stream(path):
    with open(path) as f:
        for l in f:
            yield json.loads(l)


record_generator = read_jsonl_stream("../realm_wiki_records.jsonl")


print('Loading vectors...')
vectors = np.load("../realm_wiki_embedding_128.npy")
print('Finished loading vectors')


def batching(iterable, n=1):
    total = len(iterable)
    for ndx in range(0, total, n):
        yield iterable[ndx:min(ndx + n, total)]


class GeneratorBatcher:
    def __init__(self, generator, batch_size):
        self.gen = generator
        self.batch_size = batch_size

    def __iter__(self):
        return self

    def __next__(self) -> list:
        data = []
        try:
            i = 0
            while i < self.batch_size:
                data.append(next(self.gen))
                i += 1
            return data
        except StopIteration:
            return data


record_batch_gen = GeneratorBatcher(record_generator, batch_size=upload_batch)
vector_gen = batching(vectors, n=upload_batch)

for i, (rec, vec) in tqdm(
        enumerate(
        zip(
            record_batch_gen,
            vector_gen
            )
        ),
        total=len(vectors)//upload_batch,
        desc='uploading vectors'
    ):
    idx_list = list(range(i * upload_batch, (i + 1) * upload_batch, 1))
    rec = [{"data": r} for r in rec]
    vec = [v.tolist() for v in vec]
    if i <= 1:
        print('='*30 + str(i) + '='*30)
        print(idx_list)
        print(rec[:2])
        print(vec[:2])
    qdrant_client.upload_collection(collection_name=collection_name,
                                    vectors=vec,
                                    payload=rec,
                                    ids=idx_list,
                                    batch_size=100,
                                    parallel=1)


# re-enable index
qdrant_client.update_collection(
        collection_name=collection_name,
        optimizer_config=OptimizersConfigDiff(
            indexing_threshold=20000,
        )
    )
