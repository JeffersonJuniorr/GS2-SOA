"""
Painel Web Cidadão e Executivo (Frontend Integrado) servido na raiz `/` da API SOA.
Proporciona visualização acessível (alto contraste, letras legíveis) das estações,
status de elevadores PCD, simulador de telemetria ESP32 e predição de Machine Learning.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

dashboard_router = APIRouter()

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Deslocai — CitizenTech Mobilidade Acessível & Previsível</title>
  <style>
    :root {
      --bg: #0d1117;
      --card: #161b22;
      --border: #30363d;
      --text: #f0f6fc;
      --muted: #8b949e;
      --accent: #e91c5d;
      --ok: #2ea043;
      --warn: #d29922;
      --crit: #f85149;
      --blue: #58a6ff;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    header {
      max-width: 1260px;
      margin: 0 auto 24px auto;
      background: linear-gradient(135deg, #1b1f2a 0%, #2a1220 100%);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .brand h1 { font-size: 1.9rem; letter-spacing: -0.5px; }
    .brand h1 span { color: var(--accent); }
    .brand p { color: var(--muted); font-size: 0.96rem; margin-top: 4px; }
    .nav-links { display: flex; gap: 10px; flex-wrap: wrap; }
    .btn {
      background: var(--accent);
      color: #fff;
      text-decoration: none;
      padding: 10px 16px;
      border-radius: 8px;
      font-weight: 600;
      border: none;
      cursor: pointer;
      font-size: 0.92rem;
    }
    .btn-outline {
      background: transparent;
      border: 1px solid var(--blue);
      color: var(--blue);
    }
    .container { max-width: 1260px; margin: 0 auto; display: grid; gap: 24px; }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 16px;
    }
    .kpi-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
    }
    .kpi-card .label { color: var(--muted); font-size: 0.85rem; text-transform: uppercase; }
    .kpi-card .val { font-size: 1.8rem; font-weight: 700; margin-top: 6px; color: var(--blue); }
    .section-title { font-size: 1.25rem; margin-bottom: 12px; border-left: 4px solid var(--accent); padding-left: 10px; }
    .stations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 16px;
    }
    .station-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .badge {
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.78rem;
      font-weight: 700;
    }
    .badge-NORMAL { background: rgba(46, 160, 67, 0.2); color: #56d364; border: 1px solid #2ea043; }
    .badge-ATENCAO { background: rgba(210, 153, 34, 0.2); color: #e3b341; border: 1px solid #d29922; }
    .badge-CRITICO { background: rgba(248, 81, 73, 0.2); color: #ff7b72; border: 1px solid #f85149; }
    .metrics-row { display: flex; justify-content: space-between; font-size: 0.92rem; background: #0d1117; padding: 10px; border-radius: 8px; }
    .eq-list { font-size: 0.86rem; color: var(--muted); list-style: none; }
    .eq-list li { margin-top: 4px; }
    .two-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; }
    .panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
    label { font-size: 0.84rem; color: var(--muted); display: block; margin-bottom: 4px; }
    input, select {
      width: 100%;
      padding: 8px 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: #0d1117;
      color: var(--text);
    }
    .result-box {
      margin-top: 14px;
      padding: 12px;
      border-radius: 8px;
      background: #0d1117;
      border: 1px solid var(--border);
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>Desloc<span>ai</span> — Painel Cidadão & SOA</h1>
      <p>CitizenTech FIAP 2026 (3ES) · Monitoramento de Superlotação, Calor Extremo e Acessibilidade PCD em Tempo Real</p>
    </div>
    <div class="nav-links">
      <a class="btn" href="/docs" target="_blank">Abrir Swagger UI (/docs)</a>
      <a class="btn btn-outline" href="/redoc" target="_blank">ReDoc (/redoc)</a>
      <a class="btn btn-outline" href="/api/v1/system/migrations" target="_blank">Migrações DB</a>
    </div>
  </header>

  <div class="container">
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="label">Recall do Modelo ML (Teste)</div>
        <div class="val">93,86%</div>
        <small style="color:var(--muted)">ROC-AUC: 0.9741 (SP156 + INMET 2024)</small>
      </div>
      <div class="kpi-card">
        <div class="label">Redução Média de Espera</div>
        <div class="val">-11,4 min</div>
        <small style="color:var(--muted)">Em horários de pico com rota alternativa</small>
      </div>
      <div class="kpi-card">
        <div class="label">ODS Conectados (ONU)</div>
        <div class="val">9 · 10 · 11</div>
        <small style="color:var(--muted)">Inovação, Redução de Desigualdades e Cidades</small>
      </div>
      <div class="kpi-card">
        <div class="label">Status do Totem IoT ESP32</div>
        <div class="val" style="color:#56d364">ONLINE</div>
        <small style="color:var(--muted)">Sincronizado via POST /api/v1/telemetry</small>
      </div>
    </div>

    <div>
      <h2 class="section-title">Estações e Terminais Monitorados em Tempo Real</h2>
      <div id="stations-container" class="stations-grid">Carregando estações...</div>
    </div>

    <div class="two-cols">
      <div class="panel">
        <h2 class="section-title">Simulador de Envio IoT (ESP32 Wokwi -> API SOA)</h2>
        <p style="color:var(--muted);font-size:0.88rem">Envia um pacote JSON real para <code>POST /api/v1/telemetry</code> e atualiza a estação instantaneamente.</p>
        <div class="form-grid">
          <div>
            <label>Estação</label>
            <select id="iot-station">
              <option value="EST-SE-01">EST-SE-01 (Estação Sé)</option>
              <option value="EST-LUZ-02">EST-LUZ-02 (Estação da Luz)</option>
              <option value="EST-BFU-03">EST-BFU-03 (Barra Funda)</option>
              <option value="EST-TAT-04">EST-TAT-04 (Tatuapé)</option>
              <option value="EST-PIN-05">EST-PIN-05 (Pinheiros)</option>
            </select>
          </div>
          <div>
            <label>Ocupação da Plataforma (%)</label>
            <input type="number" id="iot-occ" value="94" min="0" max="100" />
          </div>
          <div>
            <label>Temperatura DHT22 (°C)</label>
            <input type="number" id="iot-temp" value="34.0" step="0.5" />
          </div>
          <div>
            <label>Umidade DHT22 (%)</label>
            <input type="number" id="iot-hum" value="68" min="10" max="100" />
          </div>
          <div>
            <label>Elevador PCD Operante?</label>
            <select id="iot-elev">
              <option value="false">INOPERANTE (Falha)</option>
              <option value="true">OPERANTE (Normal)</option>
            </select>
          </div>
          <div>
            <label>Botão SOS PCD Acionado?</label>
            <select id="iot-sos">
              <option value="true">SIM (Solicitar Agente)</option>
              <option value="false">NÃO</option>
            </select>
          </div>
        </div>
        <button class="btn" style="margin-top:14px;width:100%" onclick="sendTelemetry()">Transmitir Pacote IoT ESP32</button>
        <div id="iot-result" class="result-box">Aguardando transmissão...</div>
      </div>

      <div class="panel">
        <h2 class="section-title">Preditor de Risco ML (Random Forest — SP156 + INMET)</h2>
        <p style="color:var(--muted);font-size:0.88rem">Consulta o modelo real em <code>POST /api/v1/ml/predict-risk</code> para prever atraso crítico (>5 dias).</p>
        <div class="form-grid">
          <div>
            <label>Categoria Operacional</label>
            <select id="ml-cat">
              <option value="INFRA_ESTACAO_E_PONTO">Infraestrutura de Estação / Ponto</option>
              <option value="CIRCULACAO_E_VIAS">Circulação e Acessibilidade Viária</option>
              <option value="OPERACAO_EMBARQUE">Operação de Embarque / Conduta</option>
              <option value="ACESSIBILIDADE_PCD">Acessibilidade PCD (ATENDE+ / DeFis)</option>
              <option value="SUPERLOTACAO_E_INTERVALO">Superlotação e Intervalo Excessivo</option>
              <option value="BILHETE_UNICO_E_TARIFA">Bilhete Único e Tarifa</option>
            </select>
          </div>
          <div>
            <label>Órgão Responsável</label>
            <select id="ml-orgao">
              <option value="INTEGRACAO-SPTRANS">INTEGRACAO-SPTRANS</option>
              <option value="INTEGRACAO-CET">INTEGRACAO-CET</option>
              <option value="SMT-DSV-DAUT">SMT-DSV-DAUT</option>
            </select>
          </div>
          <div>
            <label>Temperatura Máxima do Dia (°C)</label>
            <input type="number" id="ml-temp" value="33.5" step="0.5" />
          </div>
          <div>
            <label>Precipitação do Dia (mm)</label>
            <input type="number" id="ml-rain" value="14.0" step="1.0" />
          </div>
        </div>
        <button class="btn" style="margin-top:14px;width:100%" onclick="runMlPrediction()">Executar Predição de Machine Learning</button>
        <div id="ml-result" class="result-box">Clique para consultar o modelo Random Forest...</div>
      </div>
    </div>
  </div>

  <script>
    async function loadStations() {
      const res = await fetch('/api/v1/stations');
      const stations = await res.json();
      const container = document.getElementById('stations-container');
      container.innerHTML = stations.map(st => `
        <div class="station-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <strong>${st.name}</strong> <small style="color:var(--muted)">(${st.code})</small>
              <div style="font-size:0.82rem;color:var(--muted)">${st.line_name}</div>
            </div>
            <span class="badge badge-${st.risk_level}">${st.risk_level}</span>
          </div>
          <div class="metrics-row">
            <div>Lotação: <strong>${st.current_occupancy_pct}%</strong> (${st.crowding_level})</div>
            <div>Clima: <strong>${st.current_temperature_c}°C</strong> (ST ${st.current_heat_index_c}°C)</div>
          </div>
          <div class="metrics-row">
            <div>Score PCD: <strong>${st.accessibility_score}/100</strong></div>
            <div>Espera est.: <strong>${st.estimated_wait_minutes} min</strong></div>
          </div>
          <ul class="eq-list">
            ${st.equipments.map(eq => `
              <li>• <strong>${eq.name}</strong>: <span style="color:${eq.status === 'OPERANTE' ? '#56d364' : '#ff7b72'}">${eq.status}</span></li>
            `).join('')}
          </ul>
        </div>
      `).join('');
    }

    async function sendTelemetry() {
      const payload = {
        node_id: "DESLOCAI-IOT-ESP32-SIM",
        station_code: document.getElementById('iot-station').value,
        temperature_c: parseFloat(document.getElementById('iot-temp').value),
        humidity_pct: parseFloat(document.getElementById('iot-hum').value),
        distance_cm: 35,
        occupancy_pct: parseInt(document.getElementById('iot-occ').value),
        elevator_operational: document.getElementById('iot-elev').value === 'true',
        escalator_operational: true,
        pcd_sos_active: document.getElementById('iot-sos').value === 'true'
      };
      const res = await fetch('/api/v1/telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      document.getElementById('iot-result').innerHTML =
        `<strong>Telemetria gravada (ID #${data.id}):</strong> Risco=${data.risk_level} | Lotação=${data.occupancy_pct}% | Sensação Térmica=${data.heat_index_c}°C`;
      await loadStations();
    }

    async function runMlPrediction() {
      const payload = {
        temp_max_c: parseFloat(document.getElementById('ml-temp').value),
        temp_min_c: 20.5,
        umidade_media_pct: 66.0,
        precipitacao_total_mm: parseFloat(document.getElementById('ml-rain').value),
        categoria_deslocai: document.getElementById('ml-cat').value,
        meio_comunicacao: "MOBILE",
        tema: "Trânsito e Transporte",
        orgao_agrupado: document.getElementById('ml-orgao').value,
        regiao_sp: "SE",
        volume_chamados_dia: 72
      };
      const res = await fetch('/api/v1/ml/predict-risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      document.getElementById('ml-result').innerHTML =
        `<strong>Probabilidade de Atraso Crítico (>5d): ${(data.probability_critical_delay * 100).toFixed(1)}% (${data.risk_classification})</strong><br/>` +
        `<span style="color:var(--muted)">${data.citizen_recommendation}</span>`;
    }

    loadStations();
  </script>
</body>
</html>
"""


@dashboard_router.get("/", response_class=HTMLResponse, include_in_schema=False)
def render_citizen_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)
