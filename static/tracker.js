// tracker.js
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const endpoint = "https://painel-conversoes.onrender.com/"; // Substituir pela URL da sua API

    let nome = "";
    let email = "";
    let telefone = "";
    let consentimento = false;

    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

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

    // Monitora preenchimento de inputs
    document.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", () => {
        const name = input.name?.toLowerCase() || input.id?.toLowerCase();

        if (name?.includes("nome")) nome = input.value;
        if (name?.includes("email")) email = input.value;
        if (name?.includes("telefone") || name?.includes("cel")) telefone = input.value;
      });
    });

    // Escuta cliques e identifica o tipo de evento
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
        nome,
        email,
        telefone,
        ip,
        user_agent: userAgent,
        url,
        origem: "google",
        evento: tipoEvento,
        visitor_id: visitorId
      };

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    });
  });
})();
