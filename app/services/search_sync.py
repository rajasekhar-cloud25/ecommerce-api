"""
OpenSearch integration for product search.
Falls back gracefully when OpenSearch is unavailable.
"""
from app.config import settings

_client = None


def get_opensearch_client():
    """Lazy-initialize OpenSearch client. Returns None if disabled or unreachable."""
    global _client

    if not settings.opensearch_enabled:
        return None

    if _client is None:
        try:
            from opensearchpy import OpenSearch
            _client = OpenSearch(
                hosts=[settings.opensearch_url],
                http_compress=True,
                use_ssl=False,
                verify_certs=False,
                ssl_show_warn=False,
            )
        except Exception as e:
            print(f"OpenSearch client init failed: {e}")
            return None

    return _client


def index_product(product):
    """Index a single product into OpenSearch. Silently fails if OS unavailable."""
    client = get_opensearch_client()
    if not client:
        return

    try:
        client.index(
            index=settings.opensearch_index_products,
            id=product.id,
            body={
                "id": product.id,
                "title": product.title,
                "brand": product.brand or "",
                "description": product.description,
                "price": product.price,
                "category_id": product.category_id,
                "stock": product.stock,
                "is_published": product.is_published,
            },
        )
    except Exception as e:
        print(f"OpenSearch index failed for product {product.id}: {e}")


def delete_product_from_index(product_id: int):
    """Remove a product from the OpenSearch index."""
    client = get_opensearch_client()
    if not client:
        return

    try:
        client.delete(index=settings.opensearch_index_products, id=product_id)
    except Exception as e:
        print(f"OpenSearch delete failed for product {product_id}: {e}")


def search_products_in_opensearch(query: str, limit: int = 50):
    """
    Search products via OpenSearch.
    Returns list of product IDs sorted by relevance, or None if unavailable.
    """
    client = get_opensearch_client()
    if not client:
        return None

    try:
        result = client.search(
            index=settings.opensearch_index_products,
            body={
                "size": limit,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "brand^2", "description"],
                        "fuzziness": "AUTO",
                    }
                },
            },
        )
        return [int(hit["_id"]) for hit in result["hits"]["hits"]]
    except Exception as e:
        print(f"OpenSearch search failed: {e}")
        return None


def reindex_all_products(db):
    """Bulk reindex all products. Run on startup or via CronJob."""
    client = get_opensearch_client()
    if not client:
        print("⏭️  OpenSearch disabled, skipping reindex")
        return

    from app.models.product import Product
    products = db.query(Product).all()

    # Ensure index exists
    try:
        if not client.indices.exists(index=settings.opensearch_index_products):
            client.indices.create(
                index=settings.opensearch_index_products,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "brand": {"type": "text"},
                            "description": {"type": "text"},
                            "price": {"type": "float"},
                            "category_id": {"type": "integer"},
                            "stock": {"type": "integer"},
                        }
                    }
                },
            )
    except Exception as e:
        print(f"⚠️  Could not create OpenSearch index: {e}")
        return

    indexed = 0
    for product in products:
        index_product(product)
        indexed += 1

    print(f"✅ Reindexed {indexed} products to OpenSearch")