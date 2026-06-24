from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import requests, time, os

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# OpenTelemetry / Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

DADOS_URL = os.getenv("DADOS_SERVICE_URL", "http://servico-dados:5000")

REQUEST_COUNT = Counter("display_requests_total", "Total de requisicoes ao servico-display", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("display_request_latency_seconds", "Latencia das requisicoes", ["endpoint"])

@app.route("/agenda")
def get_agenda():
    with tracer.start_as_current_span("get-agenda"):
        start = time.time()
        REQUEST_COUNT.labels(method="GET", endpoint="/agenda").inc()
        try:
            resp = requests.get(f"{DADOS_URL}/consultas", timeout=5)
            dados = resp.json()
            consultas = dados.get("data", [])
            formatado = [
                f"📅 {c['data']} | {c['paciente']} com {c['medico']} [{c['status'].upper()}]"
                for c in consultas
            ]
            REQUEST_LATENCY.labels(endpoint="/agenda").observe(time.time() - start)
            return jsonify({"servico": "display", "agenda": formatado})
        except Exception as e:
            return jsonify({"erro": str(e), "status": "servico-dados indisponivel"}), 503

@app.route("/health")
def health():
    return jsonify({"status": "ok", "servico": "display"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
