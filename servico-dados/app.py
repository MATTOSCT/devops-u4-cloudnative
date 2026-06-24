from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import time, random

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# OpenTelemetry / Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter("dados_requests_total", "Total de requisicoes ao servico-dados", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("dados_request_latency_seconds", "Latencia das requisicoes", ["endpoint"])

CONSULTAS = [
    {"id": 1, "paciente": "Ana Lima",    "medico": "Dr. Carlos",  "data": "2026-06-20", "status": "confirmada"},
    {"id": 2, "paciente": "João Souza",  "medico": "Dra. Beatriz", "data": "2026-06-21", "status": "pendente"},
    {"id": 3, "paciente": "Maria Silva", "medico": "Dr. Fernando", "data": "2026-06-22", "status": "confirmada"},
]

@app.route("/consultas")
def get_consultas():
    with tracer.start_as_current_span("get-consultas"):
        start = time.time()
        REQUEST_COUNT.labels(method="GET", endpoint="/consultas").inc()
        time.sleep(random.uniform(0.01, 0.05))  # simula latência real
        REQUEST_LATENCY.labels(endpoint="/consultas").observe(time.time() - start)
        return jsonify({"servico": "dados", "data": CONSULTAS})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "servico": "dados"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
