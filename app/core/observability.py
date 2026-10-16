import logging
import time
from prometheus_client import Counter, Histogram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enterprise_rag")

REQUESTS = Counter(
    "rag_requests_total",
    "Total RAG requests",
    ["status"],
)

LATENCY = Histogram(
    "rag_request_duration_seconds",
    "RAG request duration in seconds",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)


class RequestTimer:
    def __enter__(self):
        self.started_at = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        LATENCY.observe(time.perf_counter() - self.started_at)
        return False