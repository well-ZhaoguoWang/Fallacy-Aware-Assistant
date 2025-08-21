// One-shot guard for content script
if (!window.__MOD_CONTENT_EXIST) {
  window.__MOD_CONTENT_EXIST = true;

  // UI state refs
  let bubbleEl = null;
  let hideTimer = null;
  let progressBar = null;
  let progressText = null;
  let progressDetails = null;

  /* ===== Runtime messages from background ===== */
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === "MODERATE_PENDING") {
      showPending("⏳ Initializing detection...");
    } else if (msg.type === "MODERATE_PENDING_BATCH") {
      showPending("⏳ Initializing batch analysis...");
    } else if (msg.type === "MODERATE_PROGRESS" || msg.type === "MODERATE_BATCH_PROGRESS") {
      updateProgress(msg.progress);
    } else if (msg.type === "MODERATE_RESULT" || msg.type === "MODERATE_BATCH_RESULT") {
      renderResult(msg.payload);
    }
  });

  /* ===== Pending state ===== */
  function showPending(text) {
    resetBubble("", "#fff");
    createProgressInterface(text);
    scheduleHide(60_000);
  }

  /* ===== Progress UI ===== */
  function createProgressInterface(initialText) {
    const container = document.createElement("div");
    container.style.cssText = `
      padding: 8px 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    progressText = document.createElement("div");
    progressText.textContent = initialText;
    progressText.style.cssText = `
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 12px;
      color: #ecf0f1;
      text-align: center;
    `;

    const progressContainer = document.createElement("div");
    progressContainer.style.cssText = `
      background: rgba(255,255,255,0.2);
      border-radius: 8px;
      height: 6px;
      margin-bottom: 8px;
      overflow: hidden;
      position: relative;
    `;

    progressBar = document.createElement("div");
    progressBar.style.cssText = `
      background: linear-gradient(90deg, #3498db, #2ecc71);
      height: 100%;
      width: 0%;
      border-radius: 8px;
      transition: width 0.5s ease-out;
      position: relative;
      overflow: hidden;
    `;

    const shimmer = document.createElement("div");
    shimmer.style.cssText = `
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
      animation: shimmer 2s infinite;
    `;

    const style = document.createElement("style");
    style.textContent = `
      @keyframes shimmer { 0% { left: -100%; } 100% { left: 100%; } }
    `;
    document.head.appendChild(style);

    progressBar.appendChild(shimmer);
    progressContainer.appendChild(progressBar);

    progressDetails = document.createElement("div");
    progressDetails.style.cssText = `
      font-size: 11px;
      color: #bdc3c7;
      text-align: center;
      line-height: 1.4;
    `;

    container.appendChild(progressText);
    container.appendChild(progressContainer);
    container.appendChild(progressDetails);
    bubbleEl.appendChild(container);
  }

  /* ===== Progress updates ===== */
  function updateProgress(progress) {
    if (!progressBar || !progressText || !progressDetails) return;

    progressBar.style.width = `${progress.percentage}%`;
    progressText.textContent = progress.message;

    const detailsText = `Step ${progress.step}/${progress.totalSteps} • ${progress.percentage}% • ${progress.elapsedTime}s elapsed`;
    progressDetails.textContent = detailsText;

    if (progress.percentage < 30) {
      progressBar.style.background = "linear-gradient(90deg, #3498db, #5dade2)";
    } else if (progress.percentage < 70) {
      progressBar.style.background = "linear-gradient(90deg, #f39c12, #f7dc6f)";
    } else {
      progressBar.style.background = "linear-gradient(90deg, #27ae60, #58d68d)";
    }

    clearTimeout(hideTimer);
    scheduleHide(60_000);
  }

  /* ===== Render result/error ===== */
  function renderResult(payload) {
    progressBar = null;
    progressText = null;
    progressDetails = null;

    if (payload.ok) {
      const htmlStr = typeof payload.data === "string"
        ? payload.data
        : `<pre>${escapeHtml(JSON.stringify(payload.data, null, 2))}</pre>`;

      resetBubble("", "#fff");

      const successIcon = document.createElement("div");
      successIcon.innerHTML = "✅";
      successIcon.style.cssText = `font-size: 20px; text-align: center; margin-bottom: 8px;`;
      bubbleEl.appendChild(successIcon);

      const container = document.createElement("div");
      container.innerHTML = sanitize(htmlStr);
      bubbleEl.appendChild(container);
    } else {
      resetBubble("", "#ff6b6b");

      const errorIcon = document.createElement("div");
      errorIcon.innerHTML = "❌";
      errorIcon.style.cssText = `font-size: 20px; text-align: center; margin-bottom: 8px;`;
      bubbleEl.appendChild(errorIcon);

      const errorText = document.createElement("div");
      errorText.textContent = payload.msg || "Unknown error";
      errorText.style.cssText = `text-align: center; font-weight: 500;`;
      bubbleEl.appendChild(errorText);
    }

    scheduleHide(20_000);
  }

  /* ===== Bubble lifecycle ===== */
  function resetBubble(text, color) {
    clearTimeout(hideTimer);
    bubbleEl?.remove();

    bubbleEl = document.createElement("div");
    bubbleEl.id = "__moderate_bubble";
    Object.assign(bubbleEl.style, {
      position: "fixed",
      zIndex: "2147483647",
      background: "rgba(52, 73, 94, 0.98)",
      color: color || "#fff",
      padding: "16px 20px",
      borderRadius: "12px",
      fontSize: "13px",
      lineHeight: "1.55",
      maxWidth: "380px",
      maxHeight: "60vh",
      overflowY: "auto",
      boxShadow: "0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1)",
      whiteSpace: "pre-wrap",
      wordBreak: "break-word",
      pointerEvents: "auto",
      transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      backdropFilter: "blur(10px)",
      border: "1px solid rgba(255,255,255,0.1)"
    });

    if (text) {
      const textDiv = document.createElement("div");
      textDiv.textContent = text;
      textDiv.style.textAlign = "center";
      bubbleEl.appendChild(textDiv);
    }

    // Close button
    const btn = document.createElement("span");
    btn.textContent = "×";
    btn.title = "Close";
    Object.assign(btn.style, {
      position: "absolute",
      top: "8px",
      right: "12px",
      fontSize: "18px",
      lineHeight: "18px",
      cursor: "pointer",
      color: "#bdc3c7",
      userSelect: "none",
      transition: "color 0.2s ease",
      fontWeight: "bold"
    });
    btn.onmouseenter = () => (btn.style.color = "#fff");
    btn.onmouseleave = () => (btn.style.color = "#bdc3c7");
    btn.onclick = (e) => { e.stopPropagation(); clearTimeout(hideTimer); fadeAndRemove(); };
    bubbleEl.appendChild(btn);

    document.body.appendChild(bubbleEl);

    // Entrance animation (keep translateX for centering)
    bubbleEl.style.opacity = "0";
    bubbleEl.style.transform = "translateX(-50%) translateY(-10px) scale(0.95)";
    requestAnimationFrame(() => {
      bubbleEl.style.opacity = "1";
      bubbleEl.style.transform = "translateX(-50%) translateY(0) scale(1)";
    });

    // Positioning
    const sel = window.getSelection();
    const rect = sel && sel.rangeCount ? sel.getRangeAt(0).getBoundingClientRect() : null;
    const topY = rect ? rect.top - 14 : 80;
    bubbleEl.style.top = `${Math.max(20, topY)}px`;
    bubbleEl.style.left = "50%";
    // NOTE: do not overwrite transform here (translateX already included above)
  }

  /* ===== Auto hide ===== */
  function scheduleHide(ms) {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(fadeAndRemove, ms);
  }

  function fadeAndRemove() {
    if (!bubbleEl) return;
    bubbleEl.style.opacity = "0";
    bubbleEl.style.transform = "translateX(-50%) translateY(-10px) scale(0.95)";
    setTimeout(() => {
      bubbleEl?.remove();
      bubbleEl = null;
      progressBar = null;
      progressText = null;
      progressDetails = null;
    }, 300);
  }

  /* ===== Sanitization utils ===== */
  function sanitize(html) {
    return html
      .replace(/<(script|iframe|object)[\s\S]*?<\/\1>/gi, "")
      .replace(/\son\w+="[^"]*"/gi, "")
      .replace(/\son\w+='[^']*'/gi, "")
      .replace(/javascript:/gi, "");
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
}
