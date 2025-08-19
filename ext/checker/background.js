/* ---------- Create context menu ---------- */
chrome.runtime.onInstalled.addListener(function () {
  // Single-item analysis (existing)
  chrome.contextMenus.create({
    id:       "sendToModerate",
    title:    "🪄 Start checking for fallacies.",
    contexts: ["selection"]
  });

  // Batch analysis — selection not required; operate on whole page / current URL
  chrome.contextMenus.create({
    id:       "sendToModerateBatch",
    title:    "📚 Batch Analyse (reddit only)", // batch analysis
    contexts: ["page", "selection", "link"] // more contexts = easier to use
  });
});

/* ---------- Listen for clicks ---------- */
chrome.contextMenus.onClicked.addListener(function (info, tab) {
  if (!tab || !tab.id) return;

  if (info.menuItemId === "sendToModerate") {
    handleSingleModerateStreaming(info, tab);
    return;
  }

  if (info.menuItemId === "sendToModerateBatch") {
    handleBatchModerateStreaming(info, tab);
    return;
  }
});

/* ---------- Streaming single-item detection handler ---------- */
function handleSingleModerateStreaming(info, tab) {
  // 1) Tell the frontend we've started
  safeSend(tab.id, { type: "MODERATE_PENDING" });

  // 2) Prepare request body
  const body = JSON.stringify({
    news_text:    (tab && tab.url) ? tab.url : "",
    comment_text: info.selectionText || "",
    language:     "zh"
  });

  // 3) Create streaming connection
  createStreamingConnection("http://localhost:5000/moderate_stream", body, tab.id, "single");
}

/* ---------- Streaming batch detection handler ---------- */
function handleBatchModerateStreaming(info, tab) {
  // 1) Tell the frontend batch process has started
  safeSend(tab.id, { type: "MODERATE_PENDING_BATCH" });

  // 2) Prepare request body
  const body = JSON.stringify({
    url: (tab && tab.url) ? tab.url : ""
  });

  // 3) Create streaming connection
  createStreamingConnection("http://localhost:5000/detect_all_stream", body, tab.id, "batch");
}

/* ---------- Create a streaming connection ---------- */
function createStreamingConnection(url, body, tabId, type) {
  // Use fetch API to create a streaming connection
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "text/plain"
    },
    body: body
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    // Recursively read stream data
    function readStream() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          console.log('Stream finished');
          return;
        }

        // Decode chunk
        buffer += decoder.decode(value, { stream: true });
        
        // Handle complete messages
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep the incomplete line

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

        // Continue reading
        return readStream();
      });
    }

    return readStream();
  })
  .catch(error => {
    console.error('Streaming error:', error);
    // Send error to frontend
    const errorPayload = {
      ok: false,
      msg: `Connection failed: ${error.message}`
    };
    
    const messageType = type === "single" ? "MODERATE_RESULT" : "MODERATE_BATCH_RESULT";
    safeSend(tabId, { type: messageType, payload: errorPayload });
  });
}

/* ---------- Handle stream messages ---------- */
function handleStreamMessage(data, tabId, type) {
  if (data.status === "processing") {
    // Send progress update
    const messageType = type === "single" ? "MODERATE_PROGRESS" : "MODERATE_BATCH_PROGRESS";
    safeSend(tabId, {
      type: messageType,
      progress: {
        percentage: data.progress,
        message: data.message,
        step: Math.ceil(data.progress / 100 * 6), // estimate step
        totalSteps: type === "single" ? 6 : 8,
        elapsedTime: Math.floor((data.progress / 100) * (type === "single" ? 8 : 25))
      }
    });
  } else if (data.status === "completed" || data.status === "error") {
    // Send final result
    const messageType = type === "single" ? "MODERATE_RESULT" : "MODERATE_BATCH_RESULT";
    safeSend(tabId, { type: messageType, payload: data.result });
  }
}

/* ---------- Fallback to non-streaming (compatibility) ---------- */
function handleSingleModerateFallback(info, tab) {
  // 1) Tell the frontend we've started
  safeSend(tab.id, { type: "MODERATE_PENDING" });

  // 2) Start progress updates
  const progressUpdater = new ProgressUpdater(tab.id, "single");
  progressUpdater.start();

  // 3) Request backend (single)
  const body = JSON.stringify({
    news_text:    (tab && tab.url) ? tab.url : "",
    comment_text: info.selectionText || "",
    language:     "zh"
  });

  fetch("http://localhost:5000/moderate", {
    method : "POST",
    headers: { "Content-Type": "application/json" },
    body   : body
  })
    .then(function (resp) {
      return resp.text().then(function (t) {
        let j;
        try { j = JSON.parse(t || "{}"); } catch (e) { j = {}; }
        if (!resp.ok) throw new Error(j.msg || resp.statusText);
        if (!j || typeof j !== "object") throw new Error("Backend did not return JSON");
        return j;
      });
    })
    .catch(function (err) {
      return { ok: false, msg: String(err) };
    })
    .then(function (payload) {
      // 4) Stop progress and send final result
      progressUpdater.stop();
      safeSend(tab.id, { type: "MODERATE_RESULT", payload: payload });
    });
}

function handleBatchModerateFallback(info, tab) {
  // 1) Tell the frontend batch process has started
  safeSend(tab.id, { type: "MODERATE_PENDING_BATCH" });

  // 2) Start progress updates
  const progressUpdater = new ProgressUpdater(tab.id, "batch");
  progressUpdater.start();

  // 3) Request backend (batch)
  const body = JSON.stringify({
    url: (tab && tab.url) ? tab.url : ""
  });

  fetch("http://localhost:5000/detect_all", {
    method : "POST",
    headers: { "Content-Type": "application/json" },
    body   : body
  })
    .then(function (resp) {
      return resp.text().then(function (t) {
        let j;
        try { j = JSON.parse(t || "{}"); } catch (e) { j = {}; }
        if (!resp.ok) throw new Error(j.msg || resp.statusText);
        if (!j || typeof j !== "object") throw new Error("Backend did not return JSON");
        return j;
      });
    })
    .catch(function (err) {
      return { ok: false, msg: String(err) };
    })
    .then(function (payload) {
      // 4) Stop progress and send back to frontend
      progressUpdater.stop();
      safeSend(tab.id, { type: "MODERATE_BATCH_RESULT", payload: payload });
    });
}

/* ---------- Progress updater class (fallback) ---------- */
class ProgressUpdater {
  constructor(tabId, type) {
    this.tabId = tabId;
    this.type = type; // "single" or "batch"
    this.isRunning = false;
    this.progress = 0;
    this.intervalId = null;
    this.startTime = Date.now();
    
    // Progress configs by type
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
        totalTime: 8000 // estimated 8s
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
        totalTime: 25000 // estimated 25s
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
    
    // Send first progress immediately
    this.sendProgress();
    
    // Set scheduled updates
    this.intervalId = setInterval(() => {
      this.updateProgress();
    }, updateInterval);
  }

  stop() {
    this.isRunning = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  updateProgress() {
    if (!this.isRunning) return;
    
    const config = this.config[this.type];
    const elapsedTime = Date.now() - this.startTime;
    
    // Compute which step based on elapsed time
    const timeProgress = Math.min(elapsedTime / config.totalTime, 0.95); // cap at 95%
    
    // Find the step to display now
    let targetStep = config.steps.find(step => step.progress / 100 > timeProgress);
    if (!targetStep) {
      targetStep = config.steps[config.steps.length - 1];
    }
    
    this.currentStepIndex = config.steps.indexOf(targetStep);
    this.progress = Math.min(targetStep.progress, 95); // leave 5% for the final result
    
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

/* ---------- Safe send: if content.js isn't on the page, inject dynamically ---------- */
function safeSend(tabId, messageObj) {
  chrome.tabs.sendMessage(tabId, messageObj, function () {
    if (chrome.runtime.lastError) {
      // First attempt failed → inject script
      chrome.scripting.executeScript(
        { target: { tabId: tabId }, files: ["content.js"] },
        function () {
          // After injection, send again
          chrome.tabs.sendMessage(tabId, messageObj);
        }
      );
    }
  });
}
