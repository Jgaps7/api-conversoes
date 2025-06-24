// tracker.js
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const endpoint = "https://painel-conversoes.onrender.com/"; // Substituir pela URL da sua API

    // Variáveis para armazenar dados coletados do formulário
    let nome = "";
    let email = "";
    let telefone = "";
    let consentimento = false;

    // Função para ler cookies
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

     //  Função para salvar cookies primários (com 1 ano de validade)
    function setCookie(name, value) {
      document.cookie = `${name}=${value}; path=/; max-age=31536000`;
    }

    // Gera e mantém o visitor_id único por visitante
    function gerarIdUnico() {
      const chave = 'visitor_id';
      let id = getCookie(chave);
      if (!id) {
        id = crypto.randomUUID();
        document.cookie = `${chave}=${id}; path=/; max-age=31536000`; // 1 ano
      }
      return id;
    }

    const visitorId = gerarIdUnico();

     // Salva parâmetros de campanha da URL (gclid, fbclid, fbp, fbc)
    const params = new URLSearchParams(window.location.search);
    ["gclid", "fbclid", "fbp", "fbc"].forEach((chave) => {
      const valor = params.get(chave);
      if (valor) setCookie(chave, valor);
    });
    
    // Monitora preenchimento de inputs
    document.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", () => {
        const name = input.name?.toLowerCase() || input.id?.toLowerCase();
        if (name?.includes("nome")) {
          nome = input.value;
          setCookie("nome", nome);
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

    // Detecta cliques e classifica o tipo de evento
    document.addEventListener("click", async function (event) {
      const target = event.target.closest("button, a");
      if (!target) return;

      let tipoEvento = "clique_generico";

      if (target.href?.includes("wa.me")) tipoEvento = "click_whatsapp";
      if (target.innerText?.toLowerCase().includes("enviar")) tipoEvento = "form_submit";
      if (target.className?.toLowerCase().includes("cta")) tipoEvento = "click_cta";

      const userAgent = navigator.userAgent;
      const url = window.location.href;
      const consent = getCookie("cookie_consent") === "true";
      const ip = await fetch("https://api.ipify.org?format=json")
        .then((res) => res.json())
        .then((data) => data.ip)
        .catch(() => null);

      if (!consent) return; // Não envia dados se não tiver consentimento

      const payload = {
        nome: nome || getCookie("nome") || null,
        email: email || getCookie("email") || null,
        telefone: telefone || getCookie("telefone") || null,
        ip,
        user_agent: navigator.userAgent,
        url: window.location.href,
        origem: "google", // 🔁 Você pode detectar origem real se quiser
        evento: tipoEvento,
        visitor_id: visitorId,
        fbp: getCookie("fbp") || null,
        fbc: getCookie("fbc") || null,
        gclid: getCookie("gclid") || null,
        fbclid: getCookie("fbclid") || null
      };

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    });
  });
})();
