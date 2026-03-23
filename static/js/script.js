/* ===========================
   Scroll suave nos links internos (#)
=========================== */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const id = a.getAttribute('href');
    const el = document.querySelector(id);
    if (!el) return;
    e.preventDefault();
    el.scrollIntoView({ behavior: 'smooth' });
  });
});


/* ===========================
   Serviços: carrossel contínuo + hover pausa + card na frente + setas
=========================== */
(function () {
  const carousel = document.getElementById("servicesCarousel");
  const track = document.getElementById("servicesTrack");
  const left = document.getElementById("arrowLeft");
  const right = document.getElementById("arrowRight");

  if (!carousel || !track) return;

  // DUPLICA OS CARDS para o loop do CSS (to: -50%)
  const originals = Array.from(track.children);
  originals.forEach(card => track.appendChild(card.cloneNode(true)));

  function clearFront() {
    track.querySelectorAll(".service-card").forEach(c => c.classList.remove("is-front"));
  }

  // hover: pausa e traz pra frente
  track.querySelectorAll(".service-card").forEach(card => {
    card.addEventListener("mouseenter", () => {
      carousel.classList.add("is-paused");
      clearFront();
      card.classList.add("is-front");
    });

    card.addEventListener("mouseleave", () => {
      card.classList.remove("is-front");
      carousel.classList.remove("is-paused");
    });
  });

  // setas: move por 1 card
  function stepSize() {
    const card = track.querySelector(".service-card");
    if (!card) return 0;
    const gap = 24; // mesmo gap do CSS
    return card.getBoundingClientRect().width + gap;
  }

  let manualX = 0;

  function applyManualMove() {
    // ao usar seta, pausa a animação e move manualmente
    track.style.animation = "none";
    track.style.transition = "transform 450ms ease";
    track.style.transform = `translateX(${manualX}px)`;
    carousel.classList.add("is-paused");
  }

  right?.addEventListener("click", () => {
    manualX -= stepSize();
    applyManualMove();
  });

  left?.addEventListener("click", () => {
    manualX += stepSize();
    applyManualMove();
  });

  // Quando o mouse sai do carrossel todo, volta ao autoplay
  carousel.addEventListener("mouseleave", () => {
    manualX = 0;
    track.style.transition = "none";
    track.style.transform = "translateX(0px)";
    track.offsetHeight; // reflow
    track.style.transition = "";
    track.style.animation = ""; // volta pro CSS
    carousel.classList.remove("is-paused");
    clearFront();
  });
})();


/* ===========================
   Documentalizar: modal + câmera (getUserMedia) + localStorage
   (Funciona quando existir overlay/docs etc. na página)
=========================== */
(function () {
  const LS_KEY = "gestarbem_docs_local_v1";

  // elementos (se não for a página de documentalizar, só sai)
  const docsEl = document.getElementById("docs");
  const emptyEl = document.getElementById("empty");
  const searchEl = document.getElementById("search");
  const filterTypeEl = document.getElementById("filterType");

  const overlay = document.getElementById("overlay");
  const btnCamera = document.getElementById("btnCamera");
  const btnArquivo = document.getElementById("btnArquivo");
  const inputCamera = document.getElementById("inputCamera");
  const inputArquivo = document.getElementById("inputArquivo");

  const preview = document.getElementById("preview");
  const previewThumb = document.getElementById("previewThumb");
  const previewName = document.getElementById("previewName");
  const previewSub = document.getElementById("previewSub");

  const docType = document.getElementById("docType");
  const typeHint = document.getElementById("typeHint");

  const status = document.getElementById("status");
  const saveBtn = document.getElementById("saveBtn");

  const cameraBox = document.getElementById("cameraBox");
  const cameraVideo = document.getElementById("cameraVideo");
  const cameraCanvas = document.getElementById("cameraCanvas");
  const btnCapture = document.getElementById("btnCapture");
  const btnStopCamera = document.getElementById("btnStopCamera");

  // se não tiver o básico do documentalizar, não executa nada
  if (!docsEl || !overlay || !saveBtn) return;

  // estado
  let docs = JSON.parse(localStorage.getItem(LS_KEY) || "[]");
  let selectedFile = null;
  let selectedDataUrl = "";
  let selectedMime = "";
  let cameraStream = null;

  // expõe openModal/closeModal para os onclick do HTML
  window.openModal = openModal;
  window.closeModal = closeModal;

  function saveLS() {
    localStorage.setItem(LS_KEY, JSON.stringify(docs));
  }

  function escapeHtml(str) {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatBytes(bytes) {
    const n = Number(bytes || 0);
    if (!n) return "";
    const units = ["B", "KB", "MB", "GB"];
    let i = 0;
    let v = n;
    while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
    return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
  }

  function showStatus(msg) {
    if (!status) return;
    status.textContent = msg;
    status.classList.add("show");
  }

  function clearStatus() {
    if (!status) return;
    status.textContent = "";
    status.classList.remove("show");
  }

  function openModal() {
    overlay.classList.add("active");
    document.body.style.overflow = "hidden";
    resetModalKeepOpen();
  }

  function closeModal() {
    overlay.classList.remove("active");
    document.body.style.overflow = "";
    stopCamera();
    resetModal();
  }

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("active")) closeModal();
  });

  function resetModalKeepOpen() {
    selectedFile = null;
    selectedDataUrl = "";
    selectedMime = "";
    if (docType) docType.value = "";
    if (typeHint) typeHint.style.display = "none";
    clearStatus();
    saveBtn.disabled = false;

    if (preview) preview.classList.remove("show");
    if (previewThumb) previewThumb.innerHTML = `<div class="ico">📄</div>`;
    if (previewName) previewName.textContent = "Nenhum arquivo";
    if (previewSub) previewSub.textContent = "Selecione um arquivo para ver a prévia";

    if (cameraBox) cameraBox.style.display = "none";
  }

  function resetModal() {
    resetModalKeepOpen();
    if (inputCamera) inputCamera.value = "";
    if (inputArquivo) inputArquivo.value = "";
  }

  // escolher arquivo
  btnArquivo?.addEventListener("click", () => inputArquivo?.click());
  inputArquivo?.addEventListener("change", (e) => handleFile(e.target.files[0]));
  inputCamera?.addEventListener("change", (e) => handleFile(e.target.files[0]));

  // câmera
  btnCamera?.addEventListener("click", async () => {
    clearStatus();
    if (typeHint) typeHint.style.display = "none";
    await startCamera();
  });

  btnStopCamera?.addEventListener("click", stopCamera);

  async function startCamera() {
    if (!cameraBox || !cameraVideo) return;

    cameraBox.style.display = "grid";
    if (cameraStream) return;

    if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) {
      showStatus("Seu navegador não suporta câmera (getUserMedia).");
      cameraBox.style.display = "none";
      return;
    }

    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false
      });

      cameraVideo.srcObject = cameraStream;
      await cameraVideo.play();
    } catch (error) {
      console.error("Erro ao acessar a câmera:", error);
      showStatus("Não foi possível acessar a câmera: " + (error.message || error));
      cameraBox.style.display = "none";
      cameraStream = null;
    }
  }

  function stopCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(t => t.stop());
      cameraStream = null;
    }
    if (cameraVideo) cameraVideo.srcObject = null;
    if (cameraBox) cameraBox.style.display = "none";
  }

  btnCapture?.addEventListener("click", async () => {
    if (!cameraStream) {
      showStatus("Ative a câmera antes de capturar 💗");
      return;
    }
    if (!cameraVideo || !cameraCanvas) return;

    const w = cameraVideo.videoWidth || 640;
    const h = cameraVideo.videoHeight || 480;

    cameraCanvas.width = w;
    cameraCanvas.height = h;

    const ctx = cameraCanvas.getContext("2d");
    ctx.drawImage(cameraVideo, 0, 0, w, h);

    cameraCanvas.toBlob(async (blob) => {
      if (!blob) {
        showStatus("Não foi possível capturar a foto.");
        return;
      }

      const fileName = `foto_${Date.now()}.jpg`;
      const file = new File([blob], fileName, { type: "image/jpeg" });

      await handleFile(file);
      stopCamera();
    }, "image/jpeg", 0.9);
  });

  // preview/base64
  async function handleFile(file) {
    if (!file) return;
    selectedFile = file;
    selectedMime = file.type || "";

    preview?.classList.add("show");
    if (previewName) previewName.textContent = file.name || "Arquivo";
    if (previewSub) previewSub.textContent = `${selectedMime || "arquivo"}${file.size ? " • " + formatBytes(file.size) : ""}`;

    if (selectedMime.startsWith("image/")) {
      const { thumb, full } = await imageToThumbAndDataUrl(file);
      if (previewThumb) previewThumb.innerHTML = `<img src="${thumb}" alt="Prévia">`;
      selectedDataUrl = full;
      return;
    }

    if (selectedMime === "application/pdf") {
      if (previewThumb) previewThumb.innerHTML = `<div class="ico">📄</div>`;
      selectedDataUrl = "";
      return;
    }

    if (previewThumb) previewThumb.innerHTML = `<div class="ico">📎</div>`;
    selectedDataUrl = "";
  }

  function imageToThumbAndDataUrl(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => {
        const img = new Image();
        img.onload = () => {
          const full = reader.result;

          const size = 64;
          const canvas = document.createElement("canvas");
          canvas.width = size;
          canvas.height = size;

          const ctx = canvas.getContext("2d");
          const minSide = Math.min(img.width, img.height);
          const sx = (img.width - minSide) / 2;
          const sy = (img.height - minSide) / 2;

          ctx.drawImage(img, sx, sy, minSide, minSide, 0, 0, size, size);
          const thumb = canvas.toDataURL("image/jpeg", 0.8);

          resolve({ thumb, full });
        };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });
  }

  // salvar
  saveBtn.addEventListener("click", () => {
    const tipo = (docType?.value || "").trim();

    if (!selectedFile) {
      showStatus("Escolha um arquivo antes de salvar 💗");
      return;
    }

    if (!tipo) {
      if (typeHint) typeHint.style.display = "block";
      return;
    }

    if (typeHint) typeHint.style.display = "none";
    clearStatus();

    const now = Date.now();

    let thumb_data_url = "";
    const imgEl = previewThumb?.querySelector("img");
    if (imgEl && imgEl.src) thumb_data_url = imgEl.src;

    const doc = {
      id: "d_" + Math.random().toString(16).slice(2),
      tipo,
      nome_original: selectedFile.name || "Documento",
      mime_type: selectedMime || "",
      tamanho_bytes: selectedFile.size || 0,
      criado_em: now,
      data: new Date(now).toLocaleDateString("pt-BR"),
      data_url: selectedDataUrl || "",
      thumb_data_url
    };

    docs.unshift(doc);
    saveLS();
    render();
    closeModal();
  });

  // render
  function render() {
    const q = (searchEl?.value || "").trim().toLowerCase();
    const f = filterTypeEl?.value || "todos";

    const filtered = docs.filter(d => {
      const matchText =
        (d.nome_original || "").toLowerCase().includes(q) ||
        (d.tipo || "").toLowerCase().includes(q);

      const matchType = (f === "todos") ? true : (d.tipo === f);
      return matchText && matchType;
    });

    docsEl.innerHTML = "";
    if (emptyEl) emptyEl.style.display = docs.length ? "none" : "block";

    if (!filtered.length) {
      if (docs.length) {
        docsEl.innerHTML = `
          <div class="empty" style="display:block;">
            <p><strong>Nenhum documento encontrado.</strong></p>
            <p>Você pode ajustar a busca ou escolher outro tipo 💗</p>
          </div>`;
      }
      return;
    }

    filtered
      .sort((a, b) => (b.criado_em || 0) - (a.criado_em || 0))
      .forEach((d) => {
        const card = document.createElement("div");
        card.className = "doc-card";
        card.onclick = () => openDoc(d.id);

        let thumbHtml = `<div class="thumb"><div class="ico">📄</div></div>`;
        if ((d.mime_type || "").startsWith("image/") && d.thumb_data_url) {
          thumbHtml = `<div class="thumb"><img src="${d.thumb_data_url}" alt="Prévia"></div>`;
        } else if (d.mime_type === "application/pdf") {
          thumbHtml = `<div class="thumb"><div class="ico">📄</div></div>`;
        } else {
          thumbHtml = `<div class="thumb"><div class="ico">📎</div></div>`;
        }

        const size = d.tamanho_bytes ? formatBytes(d.tamanho_bytes) : "";

        card.innerHTML = `
          ${thumbHtml}
          <div class="doc-name">${escapeHtml(d.nome_original || "Documento")}</div>
          <div class="doc-meta">${escapeHtml(d.tipo || "Outros")} • ${escapeHtml(d.data || "")}${size ? " • " + escapeHtml(size) : ""}</div>
          <div class="badge">📌 ${escapeHtml(d.tipo || "Outros")}</div>
        `;
        docsEl.appendChild(card);
      });
  }

  function openDoc(id) {
    const d = docs.find(x => x.id === id);
    if (!d) return;

    const msg =
      `${d.nome_original}\n\n` +
      `Tipo: ${d.tipo}\n` +
      `Data: ${d.data}\n\n` +
      `OK = Ver • Cancelar = Excluir`;

    const ok = confirm(msg);

    if (ok) {
      if ((d.mime_type || "").startsWith("image/") && d.data_url) {
        const w = window.open();
        if (w) w.document.write(`<img src="${d.data_url}" style="max-width:100%;height:auto;">`);
      } else if (d.mime_type === "application/pdf") {
        alert("PDF salvo localmente só como referência (sem abrir), porque não usamos API 💗");
      } else {
        alert("Arquivo salvo só como referência (sem abrir), porque não usamos API 💗");
      }
    } else {
      const del = confirm("Tem certeza que deseja excluir? (Você pode adicionar de novo depois 💗)");
      if (!del) return;
      docs = docs.filter(x => x.id !== id);
      saveLS();
      render();
    }
  }

  searchEl?.addEventListener("input", render);
  filterTypeEl?.addEventListener("change", render);

  // init
  saveLS();
  render();
})();