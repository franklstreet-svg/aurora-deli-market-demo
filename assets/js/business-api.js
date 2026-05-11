(function () {
  function apiBase() {
    const meta = document.querySelector('meta[name="aurora-deli-api-base"]');
    const configured = window.AURORA_DELI_API_BASE || (meta && meta.content) || localStorage.getItem('auroraDeliApiBase') || '';
    return String(configured).replace(/\/+$/, '');
  }

  function apiURL(path) {
    if (/^https?:\/\//i.test(path)) return path;
    const base = apiBase();
    return base ? `${base}${path}` : path;
  }

  function money(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
  }

  async function getJSON(path) {
    const response = await fetch(apiURL(path));
    if (!response.ok) throw new Error('Request failed');
    return response.json();
  }

  async function hydrateReports() {
    const grid = document.querySelector('.report-summary-grid');
    if (!grid || !location.pathname.endsWith('/reports.html')) return;
    try {
      const data = await getJSON('/api/reports');
      const report = data.report;
      const cards = grid.querySelectorAll('article strong');
      if (cards[0]) cards[0].textContent = money(report.daily_sales);
      if (cards[1]) cards[1].textContent = String(report.order_volume);
      if (cards[2]) cards[2].textContent = money(report.catering_revenue);
      if (cards[3]) cards[3].textContent = String(report.inventory.low_stock_count);

      const conversion = document.querySelectorAll('.conversion-list article strong');
      if (conversion[0]) conversion[0].textContent = String(report.lead_conversion.lead_count);
      if (conversion[2]) conversion[2].textContent = String(report.lead_conversion.converted_count);
      if (conversion[3]) conversion[3].textContent = `${report.lead_conversion.conversion_rate}%`;
    } catch (error) {
      document.body.dataset.backend = 'offline';
    }
  }

  async function hydrateAdmin() {
    if (!location.pathname.endsWith('/admin.html')) return;
    try {
      const data = await getJSON('/api/system-status');
      const status = data.system_status;
      document.body.dataset.backend = status.status;
      const healthRows = document.querySelectorAll('.admin-health-table tbody tr');
      if (healthRows[3]) {
        const cells = healthRows[3].querySelectorAll('td');
        if (cells[2]) cells[2].textContent = 'Live';
        if (cells[3]) cells[3].textContent = `${status.stores.orders} orders, ${status.stores.customer_messages} messages, ${status.stores.audit_log} audit events.`;
      }
    } catch (error) {
      document.body.dataset.backend = 'offline';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    hydrateReports();
    hydrateAdmin();
  });

  window.AuroraDeliAPI = {
    url: apiURL,
    getJSON
  };
})();
