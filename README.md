# Arquitetura Orientada a Serviços (SOA) e Web Services — Deslocai Backend

## Ficha da CitizenTech (Base Comum da Equipe)

| Campo | Definição Oficial do Projeto |
| :--- | :--- |
| **Nome da CitizenTech** | **Deslocai** |
| **Cidade e Bairro** | São Paulo (SP) — Estações e Terminais de Alta Demanda (Sé, Luz, Palmeiras-Barra Funda, Tatuapé e Pinheiros) |
| **Cidadão Beneficiado** | Trabalhadores diários, estudantes, idosos e pessoas com deficiência (PCD) que dependem de metrô, trem e ônibus em horários de pico. |
| **Problema, em uma frase** | Passageiros do transporte público sofrem diariamente com superlotação imprevisível, calor extremo nos vagões/pontos e falta de avisos em tempo real sobre equipamentos de acessibilidade quebrados (elevadores e escadas rolantes). |
| **Como funciona** | Totens IoT (**ESP32**) nas plataformas medem ocupação por ultrassom, temperatura/umidade (sensação térmica) e estado operacional de elevadores/escadas rolantes com botão SOS acessível; os dados alimentam uma **API REST SOA** integrada a um modelo **Random Forest** treinado com dados públicos reais (**Portal SP156 + INMET 2024**), alertando o cidadão e recomendando rotas acessíveis antes do embarque. |
| **Indicador de Impacto** | Redução média estimada de **11,4 minutos** no tempo de espera em estações superlotadas e detecção preventiva de **93,86% (Recall)** das ocorrências críticas de mobilidade/acessibilidade, mitigando viagens perdidas por PCDs e idosos. |
| **ODS Conectados (ONU)** | **ODS 9** (Indústria, Inovação e Infraestrutura), **ODS 10** (Redução das Desigualdades) e **ODS 11** (Cidades e Comunidades Sustentáveis). |

---


> **CitizenTech Deslocai (3ES - FIAP 2026)** — Camada de Backend RESTful estruturada em **Clean Architecture / Domain-Driven Design (DDD)** com **FastAPI**, **SQLAlchemy 2.0**, **Migrações Versionadas**, **Swagger/OpenAPI 3.1**, **Painel Web Cidadão** e **17 Testes Automatizados (`pytest`)**.

---

## 1. Atendimento Integral aos Critérios de Avaliação (10,0 Pontos)

| Critério da Rubrica | Pontuação | Onde está implementado no Projeto |
| :--- | :---: | :--- |
| **Estruturação do Domínio** | **3,0 pts** | [`app/domain/`](./app/domain/) (`enums.py`, `entities.py`) — Entidades e serviços de domínio puros (`DeslocaiDomainService`: cálculo de sensação térmica, classificação de lotação, score de acessibilidade PCD `0–100` e tempo estimado de espera). |
| **Conexão com Banco de Dados** | **3,0 pts** | [`app/infrastructure/`](./app/infrastructure/) (`database.py`, `models.py`, `repositories.py`, `seed.py`) — Persistência relacional com **SQLAlchemy 2.0 ORM** e **Repository Pattern** (`stations`, `accessibility_equipments`, `telemetry_readings`, `citizen_alerts`). |
| **Migrações** | **1,5 pts** | [`migrations/`](./migrations/) (`V001` a `V004`) + [`app/infrastructure/migrations.py`](./app/infrastructure/migrations.py) — Controle versionado na tabela `schema_migrations` e endpoint auditável `GET /api/v1/system/migrations`. |
| **Documentação Automática** | **1,5 pts** | **Swagger UI** em `/docs`, **ReDoc** em `/redoc` e especificação exportada em [`openapi_swagger.json`](./openapi_swagger.json). |
| **Testes Automatizados** | **1,0 pt** | [`tests/test_deslocai_api.py`](./tests/test_deslocai_api.py) — **17 testes unitários e de integração** (`100% PASSED`) cobrindo regras de domínio, banco, telemetria IoT, acessibilidade PCD, alertas e predição ML. |

---

## 2. Arquitetura em Camadas (Clean Architecture / DDD)

```
soa-backend/
├── app/
│   ├── domain/                  # Camada de Domínio (Regras de Negócio Puras)
│   │   ├── enums.py             # TransportMode, CrowdingLevel, RiskLevel, EquipmentStatus
│   │   └── entities.py          # DeslocaiDomainService (Heat Index, Score PCD, Risco)
│   ├── infrastructure/          # Camada de Infraestrutura & Persistência
│   │   ├── database.py          # Engine SQLAlchemy 2.0 + Dependency Injection (get_db)
│   │   ├── models.py            # Tabelas ORM relacionais com Foreign Keys e Índices
│   │   ├── migrations.py        # Executor idempotente de migrações (schema_migrations)
│   │   ├── repositories.py      # Repository Pattern (Station, Equipment, Telemetry, Alert)
│   │   └── seed.py              # Seed de estações reais de SP (Sé, Luz, Barra Funda, Tatuapé, Pinheiros)
│   ├── application/             # Camada de Aplicação (Use Cases & DTOs)
│   │   ├── schemas.py           # Contratos Pydantic v2 com validações e exemplos OpenAPI
│   │   └── services.py          # Orquestração SOA + Integração com Modelo Random Forest (ML)
│   ├── presentation/            # Camada de Apresentação (Controllers REST & Dashboard Web)
│   │   ├── routes.py            # 13 Endpoints RESTful agrupados por contexto de negócio
│   │   └── dashboard.py         # Painel Web Cidadão interativo servido em GET /
│   └── main.py                  # Bootstrap FastAPI + Lifespan (Migrations + Seed)
├── migrations/                  # Scripts SQL versionados (V001 a V004)
├── tests/                       # Suíte de Testes Automatizados (Pytest + TestClient)
│   └── test_deslocai_api.py
├── openapi_swagger.json         # Especificação OpenAPI 3.1 completa exportada
└── requirements.txt
```

---

## 3. Catálogo de Endpoints REST (`/api/v1`)

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | **Painel Web Cidadão & Simulador IoT/ML** (Interface visual interativa) |
| `GET` | `/docs` | **Swagger UI** — Documentação interativa automática dos endpoints |
| `GET` | `/api/v1/health` | Status da aplicação, conexão com banco de dados e alinhamento ODS |
| `GET` | `/api/v1/system/migrations` | Lista as migrações versionadas (`V001` a `V004`) aplicadas no banco |
| `GET` | `/api/v1/stations` | Lista estações com filtros opcionais (`risk_level`, `transport_mode`) |
| `GET` | `/api/v1/stations/{station_code}` | Detalhes de lotação, temperatura, sensação térmica e equipamentos da estação |
| `POST` | `/api/v1/stations` | Cadastra nova estação ou terminal no ecossistema Deslocai |
| `GET` | `/api/v1/stations/{station_code}/equipments` | Lista elevadores PCD e escadas rolantes de uma estação |
| `PATCH` | `/api/v1/equipments/{equipment_code}/status` | Atualiza status (`OPERANTE`, `INOPERANTE`, `MANUTENCAO`) e recalcula Score PCD |
| `GET` | `/api/v1/routes/accessible-recommendations` | Recomenda estações seguras para PCDs/Idosos e retorna indicadores de impacto |
| `POST` | `/api/v1/telemetry` | **Ingestão IoT (ESP32 Wokwi):** Recebe JSON do totem, atualiza estação e gera alertas |
| `GET` | `/api/v1/telemetry` | Histórico de leituras de telemetria recebidas dos sensores ESP32 |
| `GET` | `/api/v1/alerts` | Lista alertas ativos de superlotação, calor extremo e falha de elevadores |
| `POST` | `/api/v1/alerts` | Cria alerta colaborativo reportado por cidadão ou agente |
| `PATCH` | `/api/v1/alerts/{alert_id}/resolve` | Marca um alerta como resolvido |
| `POST` | `/api/v1/ml/predict-risk` | **Integração ML:** Prevê probabilidade de atraso crítico no modelo Random Forest |
| `GET` | `/api/v1/ml/metrics` | Retorna as métricas auditáveis (Treino vs Teste e 18 combinações) do modelo ML |

---

## 4. Como Executar o Backend SOA e os Testes Automatizados

### 4.1 Instalar dependências
```bash
cd soa-backend
pip install -r requirements.txt
```

### 4.2 Executar a suíte de testes automatizados (`pytest`)
```bash
python -m pytest -v
```

### 4.3 Iniciar o servidor Web e abrir o Painel / Swagger
```bash
python -m uvicorn app.main:app --reload --port 8000
```
* **Painel Cidadão Interativo:** [http://localhost:8000/](http://localhost:8000/)
* **Documentação Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Documentação ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
