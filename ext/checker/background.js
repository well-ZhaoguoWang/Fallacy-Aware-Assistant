/* ===== Context menus ===== */
chrome.runtime.onInstalled.addListener(function () {
  chrome.contextMenus.create({
    id: "sendToModerate",
    title: "🪄 Start checking for fallacies.",
    contexts: ["selection"]
  });
  chrome.contextMenus.create({
    id: "sendToModerateBatch",
    title: "📚 Batch Analyse (reddit only)",
    contexts: ["page", "selection", "link"]
  });
});

/* ===== Menu click routing ===== */
chrome.contextMenus.onClicked.addListener(function (info, tab) {
  if (!tab || !tab.id) return;
  if (info.menuItemId === "sendToModerate") {
    handleSingleModerateStreaming(info, tab); return;
  }
  if (info.menuItemId === "sendToModerateBatch") {
    handleBatchModerateStreaming(info, tab); return;
  }
});

/* ===== Streaming: single item ===== */
function handleSingleModerateStreaming(info, tab) {
  safeSend(tab.id, { type: "MODERATE_PENDING" });
  const body = JSON.stringify({
    news_text: (tab && tab.url) ? tab.url : "",
    comment_text: info.selectionText || "",
    language: "zh"
  });
  createStreamingConnection("http://localhost:5000/moderate_stream", body, tab.id, "single");
}

/* ===== Streaming: batch ===== */
function handleBatchModerateStreaming(info, tab) {
  safeSend(tab.id, { type: "MODERATE_PENDING_BATCH" });
  const body = JSON.stringify({ url: (tab && tab.url) ? tab.url : "" });
  createStreamingConnection("http://localhost:5000/detect_all_stream", body, tab.id, "batch");
}

/* ===== SSE connection and reader ===== */
function createStreamingConnection(url, body, tabId, type) {
  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/plain" },
    body
  })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      function readStream() {
        return reader.read().then(({ done, value }) => {
          if (done) { console.log('Stream finished'); return; }
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop();
          for (const line of lines) {
            if (line.trim().startsWith('data: ')) {
              try {
                const data = JSON.parse(line.trim().substring(6));
                handleStreamMessage(data, tabId, type);
              } catch (e) {
                console.error('Failed to parse stream data:', e);
              }
            }
          }
          return readStream();
        });
      }
      return readStream();
    })
    .catch(error => {
      console.error('Streaming error:', error);
      const errorPayload = { ok: false, msg: `Connection failed: ${error.message}` };
      const messageType = type === "single" ? "MODERATE_RESULT" : "MODERATE_BATCH_RESULT";
      safeSend(tabId, { type: messageType, payload: errorPayload });
    });
}

/* ===== Stream message handler ===== */
function handleStreamMessage(data, tabId, type) {
  if (data.status === "processing") {
    const messageType = type === "single" ? "MODERATE_PROGRESS" : "MODERATE_BATCH_PROGRESS";
    safeSend(tabId, {
      type: messageType,
      progress: {
        percentage: data.progress,
        message: data.message,
        step: Math.ceil(data.progress / 100 * 6),
        totalSteps: type === "single" ? 6 : 8,
        elapsedTime: Math.floor((data.progress / 100) * (type === "single" ? 8 : 25))
      }
    });
  } else if (data.status === "completed" || data.status === "error") {
    const messageType = type === "single" ? "MODERATE_RESULT" : "MODERATE_BATCH_RESULT";
    safeSend(tabId, { type: messageType, payload: data.result });
  }
}

/* ===== Fallback: single (non-streaming) ===== */
function handleSingleModerateFallback(info, tab) {
  safeSend(tab.id, { type: "MODERATE_PENDING" });
  const progressUpdater = new ProgressUpdater(tab.id, "single");
  progressUpdater.start();

  const body = JSON.stringify({
    news_text: (tab && tab.url) ? tab.url : "",
    comment_text: info.selectionText || "",
    language: "zh"
  });

  fetch("http://localhost:5000/moderate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body
  })
    .then(resp => resp.text().then(t => {
      let j; try { j = JSON.parse(t || "{}"); } catch (e) { j = {}; }
      if (!resp.ok) throw new Error(j.msg || resp.statusText);
      if (!j || typeof j !== "object") throw new Error("Backend did not return JSON");
      return j;
    }))
    .catch(err => ({ ok: false, msg: String(err) }))
    .then(payload => {
      progressUpdater.stop();
      safeSend(tab.id, { type: "MODERATE_RESULT", payload });
    });
}

/* ===== Fallback: batch  ===== */
function handleBatchModerateFallback(info, tab) {
  safeSend(tab.id, { type: "MODERATE_PENDING_BATCH" });
  const progressUpdater = new ProgressUpdater(tab.id, "batch");
  progressUpdater.start();

  const body = JSON.stringify({ url: (tab && tab.url) ? tab.url : "" });

  fetch("http://localhost:5000/detect_all", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body
  })
    .then(resp => resp.text().then(t => {
      let j; try { j = JSON.parse(t || "{}"); } catch (e) { j = {}; }
      if (!resp.ok) throw new Error(j.msg || resp.statusText);
      if (!j || typeof j !== "object") throw new Error("Backend did not return JSON");
      return j;
    }))
    .catch(err => ({ ok: false, msg: String(err) }))
    .then(payload => {
      progressUpdater.stop();
      safeSend(tab.id, { type: "MODERATE_BATCH_RESULT", payload });
    });
}

/* ===== Progress updater (fallback only) ===== */
class ProgressUpdater {
  constructor(tabId, type) {
    this.tabId = tabId;
    this.type = type;
    this.isRunning = false;
    this.progress = 0;
    this.intervalId = null;
    this.startTime = Date.now();
    this.config = {
      single: {
        steps: [
          { progress: 10, message: "🔍 Initializing analysis..." },
          { progress: 25, message: "📊 Processing comment text..." },
          { progress: 45, message: "🧠 Analyzing logical patterns..." },
          { progress: 65, message: "⚖️ Evaluating fallacy indicators..." },
          { progress: 80, message: "📝 Generating assessment..." },
          { progress: 95, message: "✨ Finalizing results..." }
        ],
        totalTime: 8000
      },
      batch: {
        steps: [
          { progress: 5, message: "🌐 Fetching Reddit content..." },
          { progress: 15, message: "📃 Parsing comments structure..." },
          { progress: 30, message: "🔍 Analyzing comment #1-5..." },
          { progress: 45, message: "🔍 Analyzing comment #6-10..." },
          { progress: 60, message: "🔍 Analyzing comment #11-15..." },
          { progress: 75, message: "🔍 Analyzing comment #16-20..." },
          { progress: 90, message: "📊 Aggregating analysis results..." },
          { progress: 95, message: "📋 Preparing summary report..." }
        ],
        totalTime: 25000
      }
    };
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.progress = 0;
    this.currentStepIndex = 0;
    const config = this.config[this.type];
    const updateInterval = config.totalTime / config.steps.length;
    this.sendProgress();
    this.intervalId = setInterval(() => this.updateProgress(), updateInterval);
  }

  stop() {
    this.isRunning = false;
    if (this.intervalId) { clearInterval(this.intervalId); this.intervalId = null; }
  }

  updateProgress() {
    if (!this.isRunning) return;
    const config = this.config[this.type];
    const elapsedTime = Date.now() - this.startTime;
    const timeProgress = Math.min(elapsedTime / config.totalTime, 0.95);
    let targetStep = config.steps.find(step => step.progress / 100 > timeProgress);
    if (!targetStep) targetStep = config.steps[config.steps.length - 1];
    this.currentStepIndex = config.steps.indexOf(targetStep);
    this.progress = Math.min(targetStep.progress, 95);
    this.sendProgress();
  }

  sendProgress() {
    const config = this.config[this.type];
    const currentStep = config.steps[this.currentStepIndex] || config.steps[0];
    const messageType = this.type === "single" ? "MODERATE_PROGRESS" : "MODERATE_BATCH_PROGRESS";
    safeSend(this.tabId, {
      type: messageType,
      progress: {
        percentage: this.progress,
        message: currentStep.message,
        step: this.currentStepIndex + 1,
        totalSteps: config.steps.length,
        elapsedTime: Math.floor((Date.now() - this.startTime) / 1000)
      }
    });
  }
}

/* ===== Safe message send (auto-inject content.js if missing) ===== */
function safeSend(tabId, messageObj) {
  chrome.tabs.sendMessage(tabId, messageObj, function () {
    if (chrome.runtime.lastError) {
      chrome.scripting.executeScript(
        { target: { tabId }, files: ["content.js"] },
        function () { chrome.tabs.sendMessage(tabId, messageObj); }
      );
    }
  });
}
