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

  async function getJSON(path) {
    const response = await fetch(apiURL(path));
    if (!response.ok) throw new Error('Request failed');
    return response.json();
  }

  window.AuroraDeliAPI = {
    url: apiURL,
    getJSON
  };
})();
