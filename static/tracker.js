(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const endpoint = "https://api-conversoes.onrender.com/conversao";
    let geoInfo = {};

    function buscarGeolocalizacao(callback) {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async function (position) {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          try {
            const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
            const response = await fetch(url);
            const data = await response.json();
            geoInfo = {
              cidade: data.address.city || data.address.town || data.address.village || "",
              regiao: data.address.state || "",
              pais: data.address.country_code?.toUpperCase() || "",
              latitude: lat,
              longitude: lng
            };
          } catch (e) {
            geoInfo = {};
          }
          if (callback) callback();
        }, function () {
          geoInfo = {};
          if (callback) callback();
        });
      } else {
        geoInfo = {};
        if (callback) callback();
      }
    }

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

    const params = new URLSearchParams(window.location.search);
    ["gclid", "fbclid", "fbp", "fbc", "utm_campaign", "utm_source", "utm_medium"].forEach((chave) => {
      const valor = params.get(chave);
      if (valor) setCookie(chave, valor, { domain: ".casadosbolosandrade.com.br" });
    });

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

    async function enviarEvento(tipoEvento, extra = {}) {
      const consent = getCookie("cookie_consent") === "true";
      if (!consent) return;

      let ip = sessionStorage.getItem('tracker_ip');
      if (!ip) {
        ip = await fetch("https://api.ipify.org?format=json")
          .then((res) => res.json())
          .then((data) => data.ip)
          .catch(() => null);
        sessionStorage.setItem('tracker_ip', ip);
      }

      let origem = "google";
      if (getCookie("fbclid") || getCookie("fbp") || getCookie("fbc")) origem = "meta";

      const nomeSplit = (nomeCompleto || "").trim().split(" ");
      const nome = nomeSplit[0] || null;
      const sobrenome = nomeSplit.slice(1).join(" ") || null;

      let currency = "BRL";
      let valor = tipoEvento === "purchase" ? 100 : null;

      const payload = {
        ...geoInfo,
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
        evento: tipoEvento === "visitou_pagina" ? "page_view" : tipoEvento,
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
        currency: currency,
        valor: valor,
        ...extra
      };

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    function inicializaEventosComGeo() {
      enviarEvento("aceitou_cookies");
      enviarEvento("visitou_pagina");

      const urlAtual = window.location.href.toLowerCase();
      if (urlAtual.includes("/checkout") || urlAtual.includes("/pagamento")) {
        enviarEvento("initiate_checkout");
      }
      if (urlAtual.includes("/obrigado") || urlAtual.includes("/success")) {
        enviarEvento("purchase");
      }
    }

    document.addEventListener("click", function (event) {
      const target = event.target.closest("button, a");
      if (!target) return;

      let tipoEvento = "clique_generico";
      if (target.href?.includes("wa.me")) tipoEvento = "click_whatsapp";
      if (target.innerText?.toLowerCase().includes("enviar")) tipoEvento = "form_submit";
      if (target.className?.toLowerCase().includes("cta")) tipoEvento = "click_cta";

      enviarEvento(tipoEvento, { texto_botao: target.innerText });
    });

    window.addEventListener("popstate", () => enviarEvento("visitou_pagina"));
    window.addEventListener("pushstate", () => enviarEvento("visitou_pagina"));

    // Timeout fallback para geo, nunca perder evento!
    if (getCookie("cookie_consent") === "true") {
      let jaChamou = false;
      function chamaSeNaoChamou() {
        if (!jaChamou) {
          jaChamou = true;
          inicializaEventosComGeo();
        }
      }
      buscarGeolocalizacao(chamaSeNaoChamou);
      setTimeout(chamaSeNaoChamou, 2000);
    }
  });
})();
