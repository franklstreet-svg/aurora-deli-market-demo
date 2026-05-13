/* Orbi corner chat widget — shared across all pages
 * Reads window.ORBY_CONFIG for page-specific settings.
 * Chat history survives navigation between pages but is wiped on browser refresh. */
(function () {
  'use strict';

  var CONF        = window.ORBY_CONFIG || {};
  var GREETING    = CONF.greeting !== undefined ? CONF.greeting : "Hi! I'm Orbi. Ask me anything about Orbi AI.";
  var AUTO_OPEN   = !!CONF.autoOpen;
  var AUTO_MSG    = CONF.autoMessage || null;
  var API_URL     = (CONF.apiUrl || '').replace(/\/$/, '');
  var QA_MODE     = !!CONF.qaMode || /(^|[?&])qa=1(&|$)/.test(String(window.location.search || '')) || /^(localhost|127\.0\.0\.1)$/.test(String(window.location.hostname || ''));
  var STAGE       = String(CONF.stage || 'sales').toLowerCase();
  var ONBOARD_URL = (CONF.onboardingUrl || '/onboarding/chat').replace(/\/$/, '');

  var LS_SESSION       = 'orbi_session_id';
  var LS_MESSAGES      = 'orbi_messages';
  var LS_NOTIFIED      = 'orbi_purchase_notified';
  var LS_CUSTOMER_INFO = 'orbi_customer_info';
  var LS_LEGAL_ID      = 'orbiLegalAcceptanceId';
  var LS_LEGAL_H       = 'orbiLegalAcceptanceHandoff';
  var LS_ONBOARD       = 'orbiOnboardingSessionId';
  var LS_POST_PAYMENT  = 'orbiPostPaymentHandoff';
  var LS_ONBOARD_TIER  = 'orbiOnboardingTier';
  var LS_ONBOARD_PROD  = 'orbiOnboardingProduct';
  var LS_KEYS = [LS_SESSION, LS_MESSAGES, LS_NOTIFIED, LS_CUSTOMER_INFO, LS_LEGAL_ID, LS_LEGAL_H, LS_ONBOARD, LS_POST_PAYMENT, LS_ONBOARD_TIER, LS_ONBOARD_PROD];

  // ── Clear all state on browser refresh (F5 / reload button) ──────────────
  // performance.navigation 'reload' fires on explicit refresh but NOT on normal
  // page-to-page navigation, so chat history still survives clicking between pages.
  (function () {
    try {
      var nav = window.performance && window.performance.getEntriesByType
        ? window.performance.getEntriesByType('navigation')
        : [];
      if (nav.length && nav[0].type === 'reload') {
        LS_KEYS.forEach(function (k) {
          try { localStorage.removeItem(k); } catch (e) {}
        });
      }
    } catch (e) {}
  })();

  // ── Persistent session ID ─────────────────────────────────────────────────
  var _session = (function () {
    try {
      var s = localStorage.getItem(LS_SESSION);
      if (s && /^[a-zA-Z0-9_\-]{1,64}$/.test(s)) return s;
    } catch (e) {}
    var id = 'session_' + Date.now();
    try { localStorage.setItem(LS_SESSION, id); } catch (e) {}
    return id;
  })();

  // ── Message storage ───────────────────────────────────────────────────────
  function _loadMsgs() {
    try { return JSON.parse(localStorage.getItem(LS_MESSAGES) || '[]'); } catch (e) { return []; }
  }
  function _saveMsgs(arr) {
    try { localStorage.setItem(LS_MESSAGES, JSON.stringify(arr.slice(-60))); } catch (e) {}
  }
  function _pushMsg(entry) {
    var arr = _loadMsgs();
    arr.push(entry);
    _saveMsgs(arr);
  }

  // ── Widget HTML (injected once) ───────────────────────────────────────────
  function _injectWidget() {
    var wrap = document.createElement('div');
    wrap.id = 'orby-widget';
    wrap.style.cssText = 'position:fixed;bottom:24px;right:24px;font-family:Arial,sans-serif;z-index:9999;';
    wrap.innerHTML =
      '<div id="orby-toggle" onclick="window._orbyToggle()" style="background:linear-gradient(90deg,#6A5CFF,#2EFFC4);color:white;padding:13px 22px;border-radius:999px;cursor:pointer;font-weight:800;font-size:15px;box-shadow:0 4px 24px rgba(106,92,255,0.4);">💬 Talk to Orbi</div>' +
      '<div id="orby-chat" style="display:none;width:340px;box-shadow:0 14px 40px rgba(0,0,0,.22);border-radius:16px;overflow:hidden;margin-bottom:10px;">' +
        '<div style="background:linear-gradient(90deg,#6A5CFF,#2EFFC4);color:white;padding:14px 16px;font-weight:800;display:flex;justify-content:space-between;align-items:center;">' +
          '<span>Orbi — Orbi AI</span>' +
          '<div style="display:flex;gap:8px;align-items:center;">' +
            (QA_MODE ? '<button id="orby-qa-reset-btn" onclick="window._orbyQaReset()" title="QA reset: clear active runtime state and restart from legal setup" style="background:rgba(255,255,255,0.18);border:none;color:white;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">QA Reset</button>' : '') +
            '<button id="orby-voice-btn" onclick="window._orbyToggleVoice()" style="background:rgba(255,255,255,0.25);border:none;color:white;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">🎤 Voice</button>' +
            '<button onclick="window._orbyReset()" title="Start a new conversation" style="background:rgba(255,255,255,0.25);border:none;color:white;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">↺ New Chat</button>' +
            '<button onclick="window._orbyToggle()" style="background:rgba(255,255,255,0.25);border:none;color:white;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:700;">✕</button>' +
          '</div>' +
        '</div>' +
        '<div id="orby-messages" style="color:#0B0F1A;background:#ffffff;border:1px solid #e8eef5;border-top:none;padding:14px;height:220px;max-height:220px;overflow-y:auto;"></div>' +
        '<div style="display:flex;border:1px solid #e8eef5;border-top:none;background:white;border-radius:0 0 16px 16px;overflow:hidden;">' +
          '<input id="orby-input" type="text" placeholder="Type your message..." style="flex:1;padding:11px 14px;border:none;outline:none;font-size:15px;" onkeydown="if(event.key===\'Enter\')window._orbySend()">' +
          '<button onclick="window._orbySend()" style="background:#6A5CFF;color:white;border:none;padding:11px 16px;cursor:pointer;font-weight:700;">Send</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(wrap);
  }

  // ── DOM render helpers (no storage side-effect) ───────────────────────────
  function _renderMsg(who, text) {
    var box = document.getElementById('orby-messages');
    if (!box) return;
    var p = document.createElement('p');
    p.style.margin = '0 0 8px';
    p.innerHTML = '<strong>' + who + ':</strong> ' + text;
    box.appendChild(p);
    box.scrollTop = box.scrollHeight;
  }
  function _isLegalPage(){ return /legal\.html$/i.test(String(window.location.pathname || '')); }

 function _renderBtn(url) {
 if (_isLegalPage()) return;
    var box = document.getElementById('orby-messages');
    if (!box) return;
    var div = document.createElement('div');
    div.style.cssText = 'margin:10px 0 4px;';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.style.cssText = 'display:inline-block;background:linear-gradient(135deg,#6A5CFF,#4A3ECC);color:#fff;padding:12px 22px;border-radius:24px;border:none;text-decoration:none;font-weight:700;font-size:15px;box-shadow:0 4px 14px rgba(106,92,255,0.4);cursor:pointer;';
    btn.textContent = 'Complete Purchase →';
    btn.addEventListener('click', function () {
      if (!url) return;
      window.open(url, '_blank', 'noopener,noreferrer');
    });
    div.appendChild(btn); box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }
  function _renderOnboardingBtn(url) {
 if (_isLegalPage()) return;
    var box = document.getElementById('orby-messages');
    if (!box) return;
    var div = document.createElement('div');
    div.style.cssText = 'margin:10px 0 4px;';
    var btn = document.createElement('button');
    btn.type = 'button';
    // Append ?start=1 so pricing.html auto-opens the onboarding picker
    var target = url + (url.indexOf('?') === -1 ? '?start=1' : '&start=1');
    btn.style.cssText = 'display:inline-block;background:linear-gradient(135deg,#2EFFC4,#1EC99A);color:#0B0F1A;padding:12px 22px;border-radius:24px;border:none;text-decoration:none;font-weight:700;font-size:15px;box-shadow:0 4px 14px rgba(46,255,196,0.35);cursor:pointer;';
    btn.textContent = 'Get Started →';
    btn.addEventListener('click', function () {
      window.location.href = target;
    });
    div.appendChild(btn); box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  function _loadJson(key) {
    try { return JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (e) { return {}; }
  }
  function _legalAcceptanceId() {
    try { return localStorage.getItem(LS_LEGAL_ID) || ''; } catch (e) { return ''; }
  }
  function _stageIsOnboarding() {
    return /onboarding/.test(STAGE);
  }
  function _textForCtaHints(text) {
    return String(text || '').toLowerCase().replace(/\s+/g, ' ').trim();
  }
  function _inferCtaKind(reply, data) {
    if (data && data.onboarding_url) return 'onboarding';
    if (data && data.checkout_url) return 'checkout';
    var text = _textForCtaHints(reply);
    if (!text) return '';
    if (/send my setup request|setup request|contact us|talk to us first|book a demo/.test(text)) return 'contact';
    if (/complete purchase|complete payment|payment verified|payment is verified|click the button below|button below|get started|start setup|continue setup|move forward with setup/.test(text)) {
      return _stageIsOnboarding() ? 'onboarding' : 'checkout';
    }
    return '';
  }
  function _renderFallbackCta(kind) {
    if (kind === 'onboarding') {
      _renderOnboardingBtn(ONBOARD_URL || '/onboarding/chat');
      return true;
    }
    if (kind === 'checkout') {
      _renderBtn('/legal.html?start=1');
      return true;
    }
    if (kind === 'contact') {
      var box = document.getElementById('orby-messages');
      if (!box) return false;
      var div = document.createElement('div');
      div.style.cssText = 'margin:10px 0 4px;';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.style.cssText = 'display:inline-block;background:linear-gradient(135deg,#6A5CFF,#4A3ECC);color:#fff;padding:12px 22px;border-radius:24px;border:none;text-decoration:none;font-weight:700;font-size:15px;box-shadow:0 4px 14px rgba(106,92,255,0.4);cursor:pointer;';
      btn.textContent = 'Contact Us →';
      btn.addEventListener('click', function () {
        window.location.href = 'contact.html';
      });
      div.appendChild(btn); box.appendChild(div);
      return true;
    }
    return false;
  }
  function _safeSessionId(value) {
    var sid = String(value || '').trim();
    return /^[a-zA-Z0-9_\-]{6,96}$/.test(sid) ? sid : '';
  }
  function _currentOnboardingSessionId() {
    try { return _safeSessionId(localStorage.getItem(LS_ONBOARD) || ''); } catch (e) { return ''; }
  }
  function _stagePayload(text) {
    if (!_stageIsOnboarding()) {
      return { text: text, session_id: _session, legal_acceptance_id: _legalAcceptanceId(), qa_mode: QA_MODE };
    }
    var legal = QA_MODE ? {} : _loadJson('orbiLegalAcceptanceHandoff');
    var post = QA_MODE ? {} : _loadJson('orbiPostPaymentHandoff');
    var ctx = {};
    Object.keys(legal).forEach(function(k){ ctx[k] = legal[k]; });
    Object.keys(post).forEach(function(k){ if (post[k] !== undefined && post[k] !== null && post[k] !== '') ctx[k] = post[k]; });
    return {
      session_id: _session,
      message: text,
      legal_acceptance_id: ctx.legal_acceptance_id || _legalAcceptanceId() || '',
      onboarding_session_id: ctx.onboarding_session_id || localStorage.getItem('orbiOnboardingSessionId') || '',
      owner_full_name: ctx.owner_full_name || ctx.name || '',
      business_name: ctx.business_name || '',
      owner_email: ctx.owner_email || ctx.email || '',
      phone: ctx.phone || '',
      business_website: ctx.business_website || ctx.website || '',
      selected_product_module: ctx.selected_product_module || ctx.selected_product || ctx.product || '',
      selected_product: ctx.selected_product || ctx.selected_product_module || ctx.product || '',
      product: ctx.product || ctx.selected_product_module || ctx.selected_product || '',
      tier: ctx.tier || localStorage.getItem('orbiOnboardingTier') || 'starter',
      qa_mode: QA_MODE
    };
  }
  async function _resolveEndpoint(payload) {
    if (!_stageIsOnboarding()) return (API_URL ? API_URL : '') + '/chat';
    var sid = _safeSessionId((payload && payload.onboarding_session_id) || _currentOnboardingSessionId());
    if (!sid) return (API_URL ? API_URL : '') + '/chat';
    try {
      var statusUrl = (API_URL ? API_URL : '') + '/api/onboarding-session/status?session_id=' + encodeURIComponent(sid);
      var resp = await fetch(statusUrl, { cache: 'no-store' });
      var status = {};
      try { status = await resp.json(); } catch (e) {}
      if (resp && resp.ok && status && status.valid) return ONBOARD_URL;
      if (window.console && console.warn) {
        console.warn('[Orbi] onboarding session invalid, falling back to /chat', {
          stage: STAGE,
          onboarding_session_id: sid,
          status: status
        });
      }
    } catch (e) {
      if (window.console && console.warn) {
        console.warn('[Orbi] onboarding session validation failed, falling back to /chat', e);
      }
    }
    return (API_URL ? API_URL : '') + '/chat';
  }
  function _recoveryReply() {
    return _stageIsOnboarding()
      ? 'I hit a setup issue, but I can keep helping here. If that onboarding session expired, use QA Reset or start again from the homepage.'
      : 'I could not continue that request. Please try again.';
  }
  async function _postMessage(text) {
    var payload = _stagePayload(text);
    var endpoint = await _resolveEndpoint(payload);
    if (window.console && console.debug) {
      console.debug('[Orbi] send', {
        stage: STAGE,
        endpoint: endpoint,
        onboarding_session_id: payload.onboarding_session_id || '',
        qa_mode: QA_MODE
      });
    }
    return fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  function _runtimeStatePayload(qaMode) {
    var legal = qaMode ? {} : _loadJson(LS_LEGAL_H);
    var post = qaMode ? {} : _loadJson(LS_POST_PAYMENT);
    return {
      session_id: _session,
      onboarding_session_id: localStorage.getItem(LS_ONBOARD) || legal.onboarding_session_id || post.onboarding_session_id || '',
      legal_acceptance_id: localStorage.getItem(LS_LEGAL_ID) || legal.legal_acceptance_id || post.legal_acceptance_id || '',
      customer_id: legal.customer_business_id || post.customer_business_id || post.customer_id || '',
      qa_mode: !!qaMode,
      had_onboarding_state: !!(localStorage.getItem(LS_LEGAL_ID) || localStorage.getItem(LS_LEGAL_H) || localStorage.getItem(LS_ONBOARD) || localStorage.getItem(LS_POST_PAYMENT) || /onboarding|legal|checkout-success|pricing/.test(String(window.location.pathname || '').toLowerCase()) || _stageIsOnboarding())
    };
  }

  function _clearRuntimeStorage() {
    try {
      LS_KEYS.forEach(function (k) { try { localStorage.removeItem(k); } catch (e) {} });
    } catch (e) {}
    try { if (window.sessionStorage) window.sessionStorage.clear(); } catch (e) {}
  }

  function _clearRememberedFields() {
    try {
      var forms = document.querySelectorAll('form');
      forms.forEach(function (form) {
        try { if (form && form.reset) form.reset(); } catch (e) {}
      });
    } catch (e) {}
    try {
      var fields = document.querySelectorAll('input, textarea, select');
      fields.forEach(function (field) {
        if (!field || field.disabled) return;
        var type = String(field.type || '').toLowerCase();
        if (type === 'button' || type === 'submit' || type === 'reset' || type === 'hidden') return;
        if (type === 'checkbox' || type === 'radio') field.checked = false;
        else if (field.tagName === 'SELECT') field.selectedIndex = 0;
        else field.value = '';
      });
    } catch (e) {}
  }

  function _clearQaCustomerMemory() {
    if (!QA_MODE) return;
    try { localStorage.removeItem(LS_CUSTOMER_INFO); } catch (e) {}
  }

  // ── Public addMessage / addPaymentButton (save + render) ──────────────────
  function addMessage(who, text) {
    _renderMsg(who, text);
    _pushMsg({ t: 'msg', w: who, x: text });
  }
  function addPaymentButton(url) {
    _renderBtn(url);
    _pushMsg({ t: 'btn', u: url });
  }

  function _renderReplyCta(reply, data) {
 if (_isLegalPage()) return;
    var kind = _inferCtaKind(reply, data);
    if (!kind) return;
    if (data && data.onboarding_url && kind === 'onboarding') return;
    if (data && data.checkout_url && kind === 'checkout') return;
    _renderFallbackCta(kind);
  }

  // ── Restore history on page load ──────────────────────────────────────────
  function _restore() {
    var box = document.getElementById('orby-messages');
    if (!box) return;
    var msgs = _loadMsgs();
    if (msgs.length === 0) {
      // First ever visit — seed with the page greeting
      if (GREETING) {
        _renderMsg('Orbi', GREETING);
        _saveMsgs([{ t: 'msg', w: 'Orbi', x: GREETING }]);
      }
    } else {
      box.innerHTML = '';
      msgs.forEach(function (m) {
        if (m.t === 'msg') _renderMsg(m.w, m.x);
        else if (m.t === 'btn' && !_isLegalPage()) _renderBtn(m.u);
      });
    }
  }

  // ── Widget open / close ───────────────────────────────────────────────────
  var _open = false;
  window._orbyToggle = function () {
    _open = !_open;
    var chat   = document.getElementById('orby-chat');
    var toggle = document.getElementById('orby-toggle');
    if (chat)   chat.style.display   = _open ? 'block' : 'none';
    if (toggle) toggle.style.display = _open ? 'none'  : 'block';
    if (_open) {
      setTimeout(function () {
        var inp = document.getElementById('orby-input');
        if (inp) inp.focus();
      }, 50);
    }
  };
  // Alias for any page CTAs that call openWidget()
  window.openWidget = function () { if (!_open) window._orbyToggle(); };

  // ── New Chat / Reset ──────────────────────────────────────────────────────
  async function _resetRuntime(qaMode) {
    var payload = _runtimeStatePayload(qaMode);
    var resetUrl = (API_URL ? API_URL : '') + '/api/runtime-reset';

    try {
      var resp = await fetch(resetUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true
      });
      if (!resp || !resp.ok) {
        throw new Error('runtime reset failed');
      }
    } catch (e) {}

    // Clear all Orbi-owned runtime state
    _clearRuntimeStorage();
    _clearQaCustomerMemory();
    if (qaMode) _clearRememberedFields();

    // Generate a fresh session ID for this tab
    _session = 'session_' + Date.now();
    try { localStorage.setItem(LS_SESSION, _session); } catch (e) {}

    // Stop any active voice / TTS
    _voiceOn = false; _speaking = false; _stopRec();
    _releaseMic();
    if (_synth) _synth.cancel();
    var vBtn = document.getElementById('orby-voice-btn');
    if (vBtn) { vBtn.innerHTML = '🎤 Voice'; vBtn.style.background = 'rgba(255,255,255,0.25)'; }

    // Clear message box and show fresh greeting
    var box = document.getElementById('orby-messages');
    if (box) box.innerHTML = '';
    if (GREETING) {
      _renderMsg('Orbi', GREETING);
      _saveMsgs([{ t: 'msg', w: 'Orbi', x: GREETING }]);
    }

    // Focus input so visitor can type immediately
    setTimeout(function () {
      var inp = document.getElementById('orby-input');
      if (inp) inp.focus();
    }, 50);

    if (qaMode || payload.had_onboarding_state) {
      setTimeout(function () {
        window.location.replace('index.html?qa=1');
      }, 100);
    }
  };

  window._orbyReset = function () {
    return _resetRuntime(false);
  };

  window._orbyQaReset = function () {
    return _resetRuntime(true);
  };

  // ── Voice / TTS ───────────────────────────────────────────────────────────
  var _synth      = window.speechSynthesis;
  var _voices     = [];
  var _rec        = null;
  var _voiceOn    = false;
  var _speaking   = false;
  var _chatPending = false;
  var _recGen     = 0;
  var _recActive  = false;
  var _recStarting = false;
  var _restartTimer = null;
  var _ttsResumeTimer = null;
  var _lastVoiceText = '';
  var _lastVoiceAt = 0;
  var _interimVoiceText = '';
  var _finalizeVoiceTimer = null;
  var _micStream = null;
  var _audioCtx = null;
  var _micAnalyser = null;
  var _micSource = null;
  var _micLevelData = null;
  var _micVadTimer = null;
  var _micNoiseFloor = 0.018;
  var _micSpeaking = false;
  var _lastRecEndAt = 0;
  var _lastSpokenText = '';
  var _lastSpokenAt = 0;
  var _ttsCooldownMs = 900;

  function _loadVoices() { if (_synth) _voices = _synth.getVoices(); }
  if (_synth && _synth.onvoiceschanged !== undefined) _synth.onvoiceschanged = _loadVoices;
  _loadVoices();
  setTimeout(_loadVoices, 500);
  setTimeout(_loadVoices, 1000);

  function _pickFemale() {
    var pref = ["Google UK English Female","Google US English Female","Microsoft Zira Desktop","Samantha","Karen","Moira","Fiona","Victoria","Allison","Ava"];
    for (var i = 0; i < pref.length; i++)
      for (var j = 0; j < _voices.length; j++)
        if (_voices[j].name === pref[i]) return _voices[j];
    for (var j = 0; j < _voices.length; j++)
      if (_voices[j].name.toLowerCase().indexOf('female') > -1) return _voices[j];
    return null;
  }

  function _clearFinalizeTimer() {
    if (_finalizeVoiceTimer) { clearTimeout(_finalizeVoiceTimer); _finalizeVoiceTimer = null; }
  }

  function _primeMic() {
    if (_micStream || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
    navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        autoGainControl: true,
        noiseSuppression: false
      }
    }).then(function (stream) {
      _micStream = stream;
      _startMicMonitor();
    }).catch(function () {
      _micStream = null;
    });
  }

  function _setVoiceIndicator(state) {
    var btn = document.getElementById('orby-voice-btn');
    if (!btn) return;
    if (!_voiceOn) {
      btn.innerHTML = '🎤 Voice';
      btn.style.background = 'rgba(255,255,255,0.25)';
      btn.title = '';
    } else if (state === 'hearing') {
      btn.innerHTML = '🎤 Hearing';
      btn.style.background = 'rgba(46,255,196,0.45)';
      btn.title = 'Orbi is receiving your voice';
    } else if (state === 'speaking') {
      btn.innerHTML = '🎤 Paused';
      btn.style.background = 'rgba(255,255,255,0.22)';
      btn.title = 'Orbi is speaking';
    } else {
      btn.innerHTML = '🎤 On';
      btn.style.background = 'rgba(0,255,100,0.3)';
      btn.title = 'Orbi is listening';
    }
  }

  function _speechText(text) {
    return String(text || '')
      .replace(/(^|\n)\s*#{1,6}\s*/g, '$1')
      .replace(/(^|\n)\s*[*•-]\s+/g, '$1')
      .replace(/[*_`~]/g, '')
      .replace(/\bO\.?\s*R\.?\s*B\.?\s*I\b/gi, 'OR-bee')
      .replace(/\bOrbi\b/gi, 'OR-bee')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function _normalizeTranscript(text) {
    return _speechText(text)
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function _looksLikeEcho(transcript, spokenText) {
    var heard = _normalizeTranscript(transcript);
    var spoken = _normalizeTranscript(spokenText);
    if (!heard || !spoken) return false;
    if (heard === spoken) return true;
    if (heard.indexOf(spoken) > -1 || spoken.indexOf(heard) > -1) return true;

    var heardParts = heard.split(' ').filter(Boolean);
    var spokenParts = spoken.split(' ').filter(Boolean);
    if (!heardParts.length || !spokenParts.length) return false;

    var spokenSet = {};
    spokenParts.forEach(function (w) { spokenSet[w] = true; });
    var overlap = 0;
    heardParts.forEach(function (w) { if (spokenSet[w]) overlap += 1; });
    var total = Math.max(heardParts.length, spokenParts.length);
    return total > 0 && overlap / total >= 0.82;
  }

  function _startMicMonitor() {
    if (!_micStream || _micVadTimer || !(window.AudioContext || window.webkitAudioContext)) return;
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      _audioCtx = _audioCtx || new AC();
      if (_audioCtx.state === 'suspended' && _audioCtx.resume) _audioCtx.resume();
      _micAnalyser = _audioCtx.createAnalyser();
      _micAnalyser.fftSize = 1024;
      _micAnalyser.smoothingTimeConstant = 0.75;
      _micSource = _audioCtx.createMediaStreamSource(_micStream);
      _micSource.connect(_micAnalyser);
      _micLevelData = new Uint8Array(_micAnalyser.fftSize);
    } catch (e) {
      _stopMicMonitor();
      return;
    }
    _micVadTimer = setInterval(function () {
      if (!_voiceOn || !_micAnalyser || !_micLevelData) return;
      if (_speaking) {
        _micSpeaking = false;
        _setVoiceIndicator('speaking');
        return;
      }
      _micAnalyser.getByteTimeDomainData(_micLevelData);
      var sum = 0;
      for (var i = 0; i < _micLevelData.length; i++) {
        var v = (_micLevelData[i] - 128) / 128;
        sum += v * v;
      }
      var rms = Math.sqrt(sum / _micLevelData.length);
      if (!_speaking && !_chatPending) {
        _micNoiseFloor = (_micNoiseFloor * 0.96) + (Math.min(rms, 0.08) * 0.04);
      }
      var threshold = Math.max(0.026, _micNoiseFloor * 2.2);
      var hearing = rms > threshold;
      if (hearing !== _micSpeaking) {
        _micSpeaking = hearing;
        _setVoiceIndicator(hearing ? 'hearing' : (_speaking ? 'speaking' : 'listening'));
      } else if (!_micSpeaking && _speaking) {
        _setVoiceIndicator('speaking');
      }
    }, 120);
  }

  function _stopMicMonitor() {
    if (_micVadTimer) { clearInterval(_micVadTimer); _micVadTimer = null; }
    try { if (_micSource) _micSource.disconnect(); } catch (e) {}
    try { if (_micAnalyser) _micAnalyser.disconnect(); } catch (e) {}
    _micSource = null;
    _micAnalyser = null;
    _micLevelData = null;
    _micSpeaking = false;
  }

  function _releaseMic() {
    _stopMicMonitor();
    if (!_micStream) return;
    try {
      _micStream.getTracks().forEach(function (track) { track.stop(); });
    } catch (e) {}
    _micStream = null;
  }

  function _submitVoiceText(text) {
    var t = (text || '').replace(/\s+/g, ' ').trim();
    if (!t || _speaking || _chatPending) return;
    if (_lastSpokenText && Date.now() - _lastSpokenAt < 2500 && _looksLikeEcho(t, _lastSpokenText)) return;
    var now = Date.now();
    if (t === _lastVoiceText && now - _lastVoiceAt < 1400) return;
    _lastVoiceText = t;
    _lastVoiceAt = now;
    _interimVoiceText = '';
    _clearFinalizeTimer();
    var input = document.getElementById('orby-input');
    if (input) input.value = t;
    _pauseRec(false);
    window._orbySend();
  }

  function _buildRec() {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return null;
    var gen = _recGen; // freeze generation for this instance's callbacks
    var r = new SR();
    r.continuous = true; r.interimResults = true; r.maxAlternatives = 3; r.lang = 'en-US';
    r.onstart = function () {
      if (gen !== _recGen) return;
      _recActive = true;
      _recStarting = false;
    };
    r.onresult = function (e) {
      if (gen !== _recGen || _speaking || _chatPending) return; // stale, TTS active, or reply in flight
      var finalText = '';
      var interimText = '';
      for (var i = e.resultIndex; i < e.results.length; i++) {
        var result = e.results[i];
        if (result && result[0] && result[0].transcript) {
          if (result.isFinal) finalText += result[0].transcript + ' ';
          else interimText += result[0].transcript + ' ';
        }
      }
      finalText = finalText.trim();
      interimText = interimText.trim();
      if (interimText) {
        _interimVoiceText = interimText;
        var interimInput = document.getElementById('orby-input');
        if (interimInput && !interimInput.value) interimInput.value = interimText;
      }
      if (finalText) {
        _submitVoiceText(finalText);
      } else if (interimText && interimText.split(/\s+/).length >= 3) {
        _clearFinalizeTimer();
        _finalizeVoiceTimer = setTimeout(function () {
          if (_voiceOn && !_speaking && !_chatPending) _submitVoiceText(_interimVoiceText);
        }, 1700);
      }
    };
    r.onerror = function (e) {
      if (gen !== _recGen) return; // stale — ignore
      _recActive = false;
      _recStarting = false;
      // Permission denied: turn voice mode off rather than looping forever
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
        _voiceOn = false;
        _setVoiceIndicator('off');
      }
      // All other errors (no-speech, network, aborted): onend fires next and
      // handles the restart — nothing to do here.
    };
    r.onend = function () {
      if (gen !== _recGen) return; // superseded by _stopRec — do not restart
      _recActive = false;
      _recStarting = false;
      if (_rec === r) _rec = null;
      _lastRecEndAt = Date.now();
      // Give the browser audio stack time to settle before reacquiring the mic.
      if (_voiceOn && !document.hidden && !_speaking && !_chatPending) _scheduleRecStart(250);
    };
    return r;
  }
  function _scheduleRecStart(delay) {
    if (_restartTimer) clearTimeout(_restartTimer);
    _restartTimer = setTimeout(function () {
      _restartTimer = null;
      _startRec();
    }, delay || 180);
  }
  function _startRec() {
    if (!_voiceOn || _speaking || _chatPending || _recActive || _recStarting) return;
    if (_lastRecEndAt && Date.now() - _lastRecEndAt < 120) {
      _scheduleRecStart(120);
      return;
    }
    if (_rec) _pauseRec(true);
    _rec = _buildRec();
    if (_rec) {
      _recStarting = true;
      try {
        _rec.start();
      } catch (e) {
        _recStarting = false;
        _recActive = false;
        _rec = null;
        if (_voiceOn && !document.hidden && !_speaking && !_chatPending) _scheduleRecStart(450);
      }
    }
  }
  function _pauseRec(useAbort) {
    if (_restartTimer) { clearTimeout(_restartTimer); _restartTimer = null; }
    _clearFinalizeTimer();
    _recGen++;
    var r = _rec;
    _rec = null;
    _recActive = false;
    _recStarting = false;
    if (!r) return;
    try {
      useAbort ? r.abort() : r.stop();
    } catch (e) {
      try { r.abort(); } catch (ignore) {}
    }
  }
  function _stopRec() {
    if (_restartTimer) { clearTimeout(_restartTimer); _restartTimer = null; }
    if (_ttsResumeTimer) { clearTimeout(_ttsResumeTimer); _ttsResumeTimer = null; }
    _clearFinalizeTimer();
    _pauseRec(true);
  }

 
document.addEventListener('visibilitychange', function () {
if (document.hidden) {
_voiceOn = false;
_speaking = false;
_chatPending = false;
_stopRec();
_releaseMic();
if (_synth) _synth.cancel();
_setVoiceIndicator('off');
}
});

 window._orbyToggleVoice = function () {
    var btn = document.getElementById('orby-voice-btn');
    if (_voiceOn) {
      _voiceOn = false; _speaking = false; _chatPending = false; _stopRec();
      _releaseMic();
      if (_synth) _synth.cancel();
      _setVoiceIndicator('off');
      return;
    }
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert('Voice not supported in this browser.'); return; }
    _voiceOn = true; _speaking = false; _chatPending = false;
    _primeMic();
    _setVoiceIndicator('listening');
    _scheduleRecStart(120);
  };

  function _speak(text) {
    if (!_synth) { if (_voiceOn && !_chatPending) _scheduleRecStart(350); return; }
    _speaking = true; _pauseRec(true); _synth.cancel();
    if (_voiceOn) _setVoiceIndicator('speaking');
    var spokenText = _speechText(text);
    _lastSpokenText = spokenText;
    _lastSpokenAt = Date.now();
    var u = new SpeechSynthesisUtterance(spokenText);
    var fv = _pickFemale();
    if (fv) { u.voice = fv; u.pitch = 1.1; u.rate = 0.92; } else { u.pitch = 1.1; u.rate = 0.92; }
    function resumeAfterTts() {
      if (_ttsResumeTimer) clearTimeout(_ttsResumeTimer);
      _ttsResumeTimer = setTimeout(function () {
        _ttsResumeTimer = null;
        _speaking = false;
        if (_voiceOn) _setVoiceIndicator('listening');
        if (_voiceOn && !_chatPending) _scheduleRecStart(_ttsCooldownMs);
      }, 650);
    }
    u.onend  = resumeAfterTts;
    u.onerror = resumeAfterTts;
    _synth.speak(u);
  }

  // ── Send message ──────────────────────────────────────────────────────────
  window._orbySend = function () {
    var inp = document.getElementById('orby-input');
    var text = inp.value.trim();
    if (!text) return;
    _chatPending = true;
    if (_voiceOn) _pauseRec(false);
    addMessage('You', text);
    inp.value = '';
    _postMessage(text)
    .then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        return { ok: !!(r && r.ok), data: d || {} };
      });
    })
      .then(function (res) {
        var d = res.data || {};
        if (!res.ok) {
          throw new Error(d.error || d.message || _recoveryReply());
        }
        var reply = d.reply || d.message || _recoveryReply();
 if (_isLegalPage()) {
reply = reply
.replace(/after you click get started/ig, 'after you click the Accept and Continue button')
.replace(/click the get started button below/ig, 'use the Accept and Continue button at the bottom of this legal page')
.replace(/click the button below/ig, 'use the Accept and Continue button at the bottom of this legal page')
.replace(/get started button below/ig, 'Accept and Continue button at the bottom of this legal page')
.replace(/usually the same day/ig, 'within 48 hours');
}
        addMessage('Orbi', reply);
        _chatPending = false;
        _speak(reply);
        if (d.customer_info && (d.customer_info.name || d.customer_info.email || d.customer_info.business || d.customer_info.website || d.customer_info.product)) {
          try { localStorage.setItem(LS_CUSTOMER_INFO, JSON.stringify(d.customer_info)); } catch (e) {}
        }
        if (!_isLegalPage() && d.onboarding_url) {
          _renderOnboardingBtn(d.onboarding_url);
        }
        if (!_isLegalPage() && d.checkout_url) {
          addPaymentButton(d.checkout_url);
        }
        _renderReplyCta(reply, d);
      })
    .catch(function (err) {
      _chatPending = false;
      addMessage('Orbi', _recoveryReply());
      if (_voiceOn && !document.hidden && !_speaking) _scheduleRecStart(_ttsCooldownMs);
    });
  };

  // ── Enrich auto-message with stored customer info ────────────────────────
  function _buildAutoMsg(base) {
    if (QA_MODE) return base;
    var info = {};
    try { info = JSON.parse(localStorage.getItem(LS_CUSTOMER_INFO) || '{}'); } catch (e) {}
    var parts = [];
    if (info.name)     parts.push('My name is ' + info.name);
    if (info.business) parts.push('my business is ' + info.business);
    if (info.email)    parts.push('my email is ' + info.email);
    if (info.website)  parts.push('my website is ' + info.website);
    if (info.product)  parts.push('I purchased the ' + info.product);
    return parts.length ? base + ' ' + parts.join(', ') + '.' : base;
  }

  // ── Auto-message (checkout-success only) ─────────────────────────────────
  function _sendAutoMsg(text) {
    addMessage('You', text);
    _postMessage(text)
    .then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        return { ok: !!(r && r.ok), data: d || {} };
      });
    })
    .then(function (res) {
      var d = res.data || {};
      var reply = res.ok ? (d.reply || d.message || "Welcome! I'm ready to help you get set up.") : (d.error || d.message || _recoveryReply());
      addMessage('Orbi', reply);
      _speak(reply);
    })
    .catch(function () {
      addMessage('Orbi', _recoveryReply());
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  _injectWidget();
  _restore();

  if (AUTO_OPEN) {
    setTimeout(function () {
      if (!_open) window._orbyToggle();
      if (AUTO_MSG) {
        var notified = false;
        try { notified = localStorage.getItem(LS_NOTIFIED) === '1'; } catch (e) {}
        if (!notified) {
          try { localStorage.setItem(LS_NOTIFIED, '1'); } catch (e) {}
          _sendAutoMsg(_buildAutoMsg(AUTO_MSG));
        }
      }
    }, 1500);
  }

})();
