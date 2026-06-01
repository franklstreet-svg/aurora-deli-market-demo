(function () {
  const storageKey = 'purblumBusinessSession';

  function getSession() {
    try {
      return JSON.parse(window.sessionStorage.getItem(storageKey) || 'null');
    } catch (error) {
      return null;
    }
  }

  function setSession(session) {
    window.sessionStorage.setItem(storageKey, JSON.stringify(session));
  }

  function clearSession() {
    window.sessionStorage.removeItem(storageKey);
  }

  function has(permission) {
    const session = getSession();
    return Boolean(session && Array.isArray(session.permissions) && session.permissions.includes(permission));
  }

  function headers(extra) {
    const session = getSession();
    return Object.assign(
      {},
      extra || {},
      session && session.token ? { Authorization: `Bearer ${session.token}` } : {}
    );
  }

  async function login(role, accessCode) {
    const url = window.AuroraDeliAPI ? window.AuroraDeliAPI.url('/api/business-login') : '/api/business-login';
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, access_code: accessCode })
    });
    if (!response.ok) throw new Error('Invalid business login');
    const data = await response.json();
    setSession(data.session);
    return data.session;
  }

  function requireAccess(permission, redirectPath) {
    if (has(permission)) return true;
    const main = document.querySelector('main');
    if (main) {
      main.innerHTML = `
        <section class="private-hero access-denied-panel">
          <p class="eyebrow">Private workspace</p>
          <h1>Business login required</h1>
          <p>This page is for authorized PurBlum team members.</p>
          <div class="hero-actions">
            <a class="btn primary" href="${redirectPath || 'contact.html'}">Business Login</a>
            <a class="btn secondary" href="../index.html">Return Home</a>
          </div>
        </section>`;
    }
    return false;
  }

  window.PurBlumBusinessAuth = {
    getSession,
    has,
    headers,
    login,
    logout: clearSession,
    requireAccess
  };
})();
