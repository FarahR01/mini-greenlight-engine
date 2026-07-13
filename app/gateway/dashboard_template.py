DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mini Greenlight Engine — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    margin: 0;
    padding: 32px;
  }
  h1 { font-size: 22px; margin-bottom: 4px; }
  .subtitle { color: #94a3b8; margin-bottom: 24px; font-size: 14px; }
  .card {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #334155;
  }
  .api-key-row {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
  }
  input {
    background: #0f172a;
    border: 1px solid #334155;
    color: #e2e8f0;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 14px;
    flex: 1;
  }
  button {
    background: #22c55e;
    color: #0f172a;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 14px;
  }
  button:hover { background: #16a34a; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; color: #94a3b8; padding: 8px; border-bottom: 1px solid #334155; }
  td { padding: 8px; border-bottom: 1px solid #1e293b; }
  .status-ok { color: #22c55e; }
  .status-bad { color: #ef4444; }
  #chart-container { height: 280px; }
  .empty { color: #64748b; text-align: center; padding: 40px; }
</style>
</head>
<body>

<h1>🛡️ Mini Greenlight Engine</h1>
<div class="subtitle">Scan history and compliance risk trends</div>

<div class="card api-key-row">
  <input id="apiKey" type="password" placeholder="Enter your X-API-Key" />
  <button onclick="loadData()">Load dashboard</button>
</div>

<div class="card">
  <div id="chart-container"><canvas id="riskChart"></canvas></div>
</div>

<div class="card">
  <table id="scansTable">
    <thead>
      <tr><th>Vendor</th><th>Risk Score</th><th>Date</th><th>Job ID</th></tr>
    </thead>
    <tbody id="scansBody">
      <tr><td colspan="4" class="empty">Enter your API key and click "Load dashboard"</td></tr>
    </tbody>
  </table>
</div>

<script>
let chart = null;

async function loadData() {
  const apiKey = document.getElementById('apiKey').value;
  if (!apiKey) { alert('Please enter your API key'); return; }

  try {
    const res = await fetch('/scans', { headers: { 'X-API-Key': apiKey } });
    if (!res.ok) { alert('Failed to load scans: ' + res.status); return; }
    const scans = await res.json();
    renderTable(scans);
    renderChart(scans);
  } catch (e) {
    alert('Error loading dashboard: ' + e.message);
  }
}

function renderTable(scans) {
  const body = document.getElementById('scansBody');
  if (!scans.length) {
    body.innerHTML = '<tr><td colspan="4" class="empty">No scans found yet.</td></tr>';
    return;
  }
  body.innerHTML = scans.map(s => `
    <tr>
      <td>${s.vendor_name}</td>
      <td class="${s.risk_score >= 60 ? 'status-ok' : 'status-bad'}">${s.risk_score}/100</td>
      <td>${new Date(s.created_at).toLocaleString()}</td>
      <td style="font-family: monospace; font-size: 11px;">${s.job_id.slice(0, 8)}...</td>
    </tr>
  `).join('');
}

function renderChart(scans) {
  const sorted = [...scans].reverse();
  const labels = sorted.map(s => new Date(s.created_at).toLocaleDateString());
  const scores = sorted.map(s => s.risk_score);

  const ctx = document.getElementById('riskChart').getContext('2d');
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Risk Score Over Time',
        data: scores,
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.3,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 100, ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } }
      },
      plugins: { legend: { labels: { color: '#e2e8f0' } } }
    }
  });
}
</script>
</body>
</html>
"""