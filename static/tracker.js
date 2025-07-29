(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const endpoint = "https://painel-conversoes.onrender.com/conversao";

    let nomeCompleto = "";
    let email = "";
    let telefone = "";
    let consentimento = false;

    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function setCookie(name, value) {
      document.cookie = `${name}=${value}; path=/; max-age=31536000`;
    }

    if (getCookie('cmplz_banner-status') === 'dismissed') {
  setCookie('cookie_consent', 'true');
}
    function gerarIdUnico() {
      const chave = 'visitor_id';
      let id = getCookie(chave);
      if (!id) {
        id = crypto.randomUUID();
        setCookie(chave, id);
      }
      return id;
    }

    const visitorId = gerarIdUnico();

    const params = new URLSearchParams(window.location.search);
    ["gclid", "fbclid", "fbp", "fbc", "utm_campaign", "utm_source", "utm_medium"].forEach((chave) => {
      const valor = params.get(chave);
      if (valor) setCookie(chave, valor);
    });

    document.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", () => {
        const name = input.name?.toLowerCase() || input.id?.toLowerCase();

        if (name?.includes("nome")) {
          nomeCompleto = input.value;
          setCookie("nome_completo", nomeCompleto);
        }

        if (name?.includes("email")) {
          email = input.value;
          setCookie("email", email);
        }

        if (name?.includes("telefone") || name?.includes("cel")) {
          telefone = input.value;
          setCookie("telefone", telefone);
        }
      });
    });

    const urlAtual = window.location.href.toLowerCase();
    if (urlAtual.includes("/checkout") || urlAtual.includes("/pagamento")) {
      enviarEvento("initiate_checkout");
    }
    if (urlAtual.includes("/obrigado") || urlAtual.includes("/success")) {
      enviarEvento("purchase");
    }

    document.addEventListener("click", async function (event) {
      const target = event.target.closest("button, a");
      if (!target) return;

      let tipoEvento = "clique_generico";
      if (target.href?.includes("wa.me")) tipoEvento = "click_whatsapp";
      if (target.innerText?.toLowerCase().includes("enviar")) tipoEvento = "form_submit";
      if (target.className?.toLowerCase().includes("cta")) tipoEvento = "click_cta";

      const consent = getCookie("cookie_consent") === "true";
      if (!consent) return;

      const ip = await fetch("https://api.ipify.org?format=json")
        .then((res) => res.json())
        .then((data) => data.ip)
        .catch(() => null);

      let origem = "google";
      if (getCookie("fbclid") || getCookie("fbp") || getCookie("fbc")) origem = "meta";

      const nomeSplit = (nomeCompleto || getCookie("nome_completo") || "").trim().split(" ");
      const nome = nomeSplit[0] || null;
      const sobrenome = nomeSplit.slice(1).join(" ") || null;

      const payload = {
        nome,
        sobrenome,
        email: email || getCookie("email") || null,
        telefone: telefone || getCookie("telefone") || null,
        ip,
        user_agent: navigator.userAgent,
        url: window.location.href,
        referrer: document.referrer || null,
        pagina_destino: window.location.pathname,
        botao_clicado: tipoEvento,
        origem,
        evento: tipoEvento,
        visitor_id: visitorId,
        gclid: getCookie("gclid") || null,
        fbclid: getCookie("fbclid") || null,
        fbp: getCookie("fbp") || null,
        fbc: getCookie("fbc") || null,
        campanha: getCookie("utm_campaign") || null,
        consentimento: true
      };

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    });
  });
})();
