# devops-u4-cloudnative

![CI/CD](https://github.com/MATTOSCT/devops-u4-cloudnative/actions/workflows/deploy.yml/badge.svg)

Projeto de microsserviços cloud-native com Kubernetes, observabilidade (Prometheus + Jaeger) e simulação de edge computing.

## Estrutura

```
devops-u4-cloudnative/
├── servico-dados/          # Microsserviço Flask — expõe dados de consultas
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── servico-display/        # Microsserviço Flask — consome e formata dados
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── base/               # Manifests principais (namespace, deployments, services)
│   ├── prometheus/         # ConfigMap + Deployment do Prometheus
│   ├── jaeger/             # Deployment do Jaeger all-in-one
│   └── edge/               # Deployment edge + script de sincronização
└── .github/workflows/
    └── deploy.yml          # Pipeline CI/CD
```

## Endpoints

| Serviço | Endpoint | Descrição |
|---------|----------|-----------|
| servico-dados | `GET /consultas` | Retorna lista de consultas em JSON |
| servico-dados | `GET /health` | Health check |
| servico-dados | `GET /metrics` | Métricas Prometheus |
| servico-display | `GET /agenda` | Agenda formatada (consome servico-dados) |
| servico-display | `GET /health` | Health check |
| servico-display | `GET /metrics` | Métricas Prometheus |

## Deploy rápido

```bash
# Aplicar todos os recursos
kubectl apply -k k8s/base/
kubectl apply -f k8s/prometheus/prometheus.yaml
kubectl apply -f k8s/jaeger/jaeger.yaml
kubectl apply -f k8s/edge/edge-deployment.yaml

# Acessar serviços
kubectl port-forward svc/servico-display 5001:5001 -n cloudnative
kubectl port-forward svc/prometheus 9090:9090 -n cloudnative
kubectl port-forward svc/jaeger 16686:16686 -n cloudnative
```

## Secrets necessários no GitHub

| Secret | Descrição |
|--------|-----------|
| `DOCKER_USERNAME` | Usuário Docker Hub |
| `DOCKER_PASSWORD` | Token Docker Hub |
| `KUBECONFIG` | kubeconfig em base64 |

## Aluna

Thays Coitinho Mattos — Junho de 2026
# trigger
# workflow trigger
