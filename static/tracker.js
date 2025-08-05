(function () {
  document.addEventListener("DOMContentLoaded", function () {
    // Endpoint direto da API
    const endpoint = "https://api-conversoes.onrender.com/conversao";
    // ⚠️ Defina sua API Key aqui para eventos avançados (lead/purchase), caso necessário!
    const API_KEY = "rMIQapPK6NyjM9iPriMiJU6_mGySWnp1w3ZqVla02c"; 

    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function setCookie(name, value, opts = {}) {
      let cookieStr = `${name}=${value}; path=/; max-age=31536000`;
      if (opts.domain) cookieStr += `; domain=${opts.domain}`;
      document.cookie = cookieStr;
    }

    // Cookie consent tracker
    if (getCookie('cmplz_banner-status') === 'dismissed') {
      setCookie('cookie_consent', 'true', { domain: ".casadosbolosandrade.com.br" });
    }

    function gerarIdUnico() {
      const chave = 'visitor_id';
      let id = getCookie(chave);
      if (!id) {
        id = crypto.randomUUID();
        setCookie(chave, id, { domain: ".casadosbolosandrade.com.br" });
      }
      return id;
    }
    const visitorId = gerarIdUnico();

    function getGA() {
      return getCookie('_ga') || null;
    }
    const ga_id = getGA();

    function gerarEventId() {
      return crypto.randomUUID();
    }

    // Salva parâmetros UTM e cookies
    const params = new URLSearchParams(window.location.search);
    ["gclid", "fbclid", "fbp", "fbc", "utm_campaign", "utm_source", "utm_medium"].forEach((chave) => {
      const valor = params.get(chave);
      if (valor) setCookie(chave, valor, { domain: ".casadosbolosandrade.com.br" });
    });

    // Detecta campos do formulário
    let nomeCompleto = getCookie("nome_completo") || "";
    let email = getCookie("email") || "";
    let telefone = getCookie("telefone") || "";

    document.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", () => {
        const name = input.name?.toLowerCase() || input.id?.toLowerCase();
        if (name?.includes("nome")) {
          nomeCompleto = input.value;
          setCookie("nome_completo", nomeCompleto, { domain: ".casadosbolosandrade.com.br" });
        }
        if (name?.includes("email")) {
          email = input.value;
          setCookie("email", email, { domain: ".casadosbolosandrade.com.br" });
        }
        if (name?.includes("telefone") || name?.includes("cel")) {
          telefone = input.value;
          setCookie("telefone", telefone, { domain: ".casadosbolosandrade.com.br" });
        }
      });
    });

    // Função universal para enviar eventos
    async function enviarEvento(tipoEvento, extra = {}, opts = {}) {
      const consent = getCookie("cookie_consent") === "true";
      if (!consent) return;

      // Busca IP (apenas para Analytics avançado)
      let ip = sessionStorage.getItem('tracker_ip');
      if (!ip) {
        ip = await fetch("https://api.ipify.org?format=json")
          .then((res) => res.json())
          .then((data) => data.ip)
          .catch(() => null);
        sessionStorage.setItem('tracker_ip', ip);
      }

      // Origem: só use "google"/"meta" em eventos com api-key
      let origem = "site"; // padrão anônimo
      if (opts.forceMeta) origem = "meta";
      if (opts.forceGoogle) origem = "google";
      if (extra.origem) origem = extra.origem; // permite override explícito

      const nomeSplit = (nomeCompleto || "").trim().split(" ");
      const nome = nomeSplit[0] || null;
      const sobrenome = nomeSplit.slice(1).join(" ") || null;

      let currency = "BRL";
      let valor = tipoEvento === "purchase" ? 100 : null;

      const payload = {
        nome,
        sobrenome,
        email: email || null,
        telefone: telefone || null,
        ip,
        user_agent: navigator.userAgent,
        url: window.location.href,
        url_origem: window.location.href,
        referrer: document.referrer || null,
        pagina_destino: window.location.pathname,
        botao_clicado: tipoEvento,
        origem,
        evento: tipoEvento === "visitou_pagina" ? "PageView" : tipoEvento,
        visitor_id: visitorId,
        ga_id: ga_id,
        user_id: ga_id || visitorId,
        event_id: gerarEventId(),
        gclid: getCookie("gclid") || null,
        fbclid: getCookie("fbclid") || null,
        fbp: getCookie("fbp") || null,
        fbc: getCookie("fbc") || null,
        campanha: getCookie("utm_campaign") || null,
        utm_source: getCookie("utm_source") || null,
        utm_medium: getCookie("utm_medium") || null,
        consentimento: true,
        idioma: navigator.language || null,
        plataforma: navigator.platform || null,
        largura_tela: window.screen.width,
        altura_tela: window.screen.height,
        timezone_offset: (new Date()).getTimezoneOffset(),
        device_memory: navigator.deviceMemory || null,
        is_mobile: /Mobi|Android/i.test(navigator.userAgent),
        data_evento: Date.now(),
        currency,
        valor,
        ...extra
      };

      // Só manda x-api-key para eventos de lead/conversão (não anônimos)
      const headers = { "Content-Type": "application/json" };
      if (opts.apiKey) headers["x-api-key"] = opts.apiKey;

      fetch(endpoint, {
        method: "POST",
        headers,
        body: JSON.stringify(payload)
      });
    }

    // ⬇️ Eventos anônimos, não requerem api-key, nem headers extras!
    if (getCookie("cookie_consent") === "true") {
      enviarEvento("aceitou_cookies", { origem: "cookies" });
    }
    enviarEvento("visitou_pagina", { origem: "site" });

    // ⬇️ Exemplo: só envie para meta/google (com x-api-key) em eventos que você controla (lead/purchase)
    // Lógica pode ser disparada num submit de formulário ou evento de conversão real:
    window.enviarLeadGoogle = function () {
      enviarEvento("lead", { /* qualquer dado extra */ }, { apiKey: API_KEY, forceGoogle: true });
    };
    window.enviarLeadMeta = function () {
      enviarEvento("lead", { /* qualquer dado extra */ }, { apiKey: API_KEY, forceMeta: true });
    };

    // Checkout e compra (exemplo: você pode customizar com api-key do cliente!)
    const urlAtual = window.location.href.toLowerCase();
    if (urlAtual.includes("/checkout") || urlAtual.includes("/pagamento")) {
      // Se quiser rastrear conversão Google, use forceGoogle e apiKey
      // enviarEvento("initiate_checkout", {}, { apiKey: API_KEY, forceGoogle: true });
    }
    if (urlAtual.includes("/obrigado") || urlAtual.includes("/success")) {
      // enviarEvento("purchase", {}, { apiKey: API_KEY, forceGoogle: true });
    }

    // Clique em botões/links
    document.addEventListener("click", function (event) {
      const target = event.target.closest("button, a");
      if (!target) return;

      let tipoEvento = "clique_generico";
      if (target.href?.includes("wa.me")) tipoEvento = "click_whatsapp";
      if (target.innerText?.toLowerCase().includes("enviar")) tipoEvento = "form_submit";
      if (target.className?.toLowerCase().includes("cta")) tipoEvento = "click_cta";

      enviarEvento(tipoEvento, { texto_botao: target.innerText });
    });

    // SPA navigation
    window.addEventListener("popstate", () => enviarEvento("visitou_pagina", { origem: "site" }));
    window.addEventListener("pushstate", () => enviarEvento("visitou_pagina", { origem: "site" }));
  });
})();
