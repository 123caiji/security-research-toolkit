const STORAGE_KEY = "card_workflow_tool_loop_v3";

const lanes = [
  { id: "queued", title: "待分类" },
  { id: "classified", title: "已分类" },
  { id: "executing", title: "执行中" },
  { id: "review", title: "待审核" },
  { id: "approved", title: "审核通过" }
];

const priorities = ["P0", "P1", "P2", "P3"];
const stages = lanes.map(lane => lane.id);
const reviewStatuses = ["待分类", "待执行", "执行中", "待审核", "已通过", "需复核", "执行失败", "已阻断"];
const riskLabels = { high: "高复核", medium: "中复核", low: "低复核" };

let state = loadState();
let editingId = null;
let loopTimer = null;
let toolInventory = [];

const els = {
  board: document.querySelector("#board"),
  searchInput: document.querySelector("#searchInput"),
  categoryFilter: document.querySelector("#categoryFilter"),
  typeFilter: document.querySelector("#typeFilter"),
  sortMode: document.querySelector("#sortMode"),
  metricTotal: document.querySelector("#metricTotal"),
  metricRisk: document.querySelector("#metricRisk"),
  metricAuto: document.querySelector("#metricAuto"),
  toolPool: document.querySelector("#toolPool"),
  scheduleList: document.querySelector("#scheduleList"),
  commandList: document.querySelector("#commandList"),
  logList: document.querySelector("#logList"),
  dialog: document.querySelector("#cardDialog"),
  form: document.querySelector("#cardForm"),
  fileImport: document.querySelector("#fileImport"),
  btnToggleLoop: document.querySelector("#btnToggleLoop")
};

init();

async function init() {
  fillSelect(els.categoryFilter, ["全部分类"]);
  fillSelect(els.typeFilter, ["全部类型"]);
  fillFormOptions();
  bindEvents();
  await syncTools(false);
  autoClassifyAll("system_boot");
  render();
}

function bindEvents() {
  document.querySelectorAll(".nav-tab").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });
  document.querySelector("#btnSyncTools").addEventListener("click", () => syncTools(true));
  document.querySelector("#btnStepLoop").addEventListener("click", async () => {
    await runLoopStep("manual_step");
    saveState();
    render();
  });
  els.btnToggleLoop.addEventListener("click", toggleLoop);
  document.querySelector("#btnImport").addEventListener("click", () => els.fileImport.click());
  document.querySelector("#btnExport").addEventListener("click", exportData);
  els.fileImport.addEventListener("change", importData);
  [els.searchInput, els.categoryFilter, els.typeFilter, els.sortMode].forEach(el => {
    el.addEventListener("input", render);
  });
  els.form.addEventListener("submit", saveCardFromDialog);
  document.querySelector("#btnDeleteCard").addEventListener("click", deleteEditingCard);
}

async function syncTools(withLog) {
  toolInventory = await loadToolInventory();
  updateFilters();
  if (!state.cards.length && toolInventory.length) {
    state.cards = toolInventory.slice(0, 60).map(toolToCard);
    addLog(`同步工程工具：已生成 ${state.cards.length} 张工具调用卡片。`);
  } else if (withLog) {
    const known = new Set(state.cards.map(card => card.toolName));
    const additions = toolInventory.filter(tool => !known.has(tool.name)).slice(0, 60).map(toolToCard);
    state.cards = [...state.cards, ...additions];
    addLog(`同步工程工具：新增 ${additions.length} 张工具调用卡片，库存 ${toolInventory.length} 个工具。`);
  }
  autoClassifyAll("tool_sync");
  saveState();
  render();
}

async function loadToolInventory() {
  try {
    const res = await fetch("/api/tools", { cache: "no-store" });
    if (res.ok) return normalizeTools(await res.json());
  } catch {}
  return normalizeTools(fallbackTools());
}

function normalizeTools(raw) {
  const arr = Array.isArray(raw) ? raw : raw.tools || [];
  return arr.map((tool, index) => ({
    id: tool.id || `tool_${index}`,
    name: String(tool.name || tool.title || `工具${index + 1}`),
    category: String(tool.category || "未分类"),
    type: String(tool.type || "未知类型"),
    description: String(tool.description || ""),
    path: String(tool.path || ""),
    url: String(tool.url || ""),
    params: String(tool.params || ""),
    tags: Array.isArray(tool.tags) ? tool.tags : []
  })).filter(tool => tool.name);
}

function toolToCard(tool) {
  return autoClassify({
    id: crypto.randomUUID(),
    toolId: tool.id,
    toolName: tool.name,
    category: tool.category,
    toolType: tool.type,
    target: tool.url || tool.path || "",
    intent: tool.description || inferIntent(tool),
    params: tool.params || "",
    tags: tool.tags || [],
    priority: "",
    stage: "queued",
    reviewStatus: "待分类",
    riskLevel: "",
    aiScore: 0,
    context: { scope: "local_project", mode: "real_execute_via_allowlist" },
    executionTrace: [],
    lastExecution: null,
    updatedAt: new Date().toISOString()
  });
}

function render() {
  const cards = filteredCards().map(enrichCard);
  renderMetrics();
  renderToolPool();
  renderBoard(cards);
  renderPlanner();
  renderLogs();
}

function renderBoard(cards) {
  els.board.innerHTML = "";
  lanes.forEach(lane => {
    const column = document.createElement("section");
    column.className = "lane";
    column.dataset.lane = lane.id;
    column.innerHTML = `
      <header>
        <h3>${lane.title}</h3>
        <span class="lane-count">${cards.filter(c => c.stage === lane.id).length}</span>
      </header>
      <div class="lane-body" data-lane-body="${lane.id}"></div>
    `;
    column.querySelector(".lane-body").addEventListener("dragover", e => e.preventDefault());
    column.querySelector(".lane-body").addEventListener("drop", onDrop);
    els.board.appendChild(column);
  });

  cards.forEach(card => {
    const body = els.board.querySelector(`[data-lane-body="${card.stage}"]`) || els.board.querySelector(`[data-lane-body="queued"]`);
    body.appendChild(cardElement(card));
  });
}

function cardElement(card) {
  const el = document.createElement("article");
  el.className = `card priority-${card.priority} risk-${card.riskLevel}`;
  el.draggable = true;
  el.dataset.id = card.id;
  const primaryAction = card.stage === "classified" || card.stage === "executing" ? "执行" : "推进";
  el.innerHTML = `
    <div class="card-title">
      <strong>${escapeHtml(card.toolName)}</strong>
      <span class="badge">${card.priority}</span>
    </div>
    <p>${escapeHtml(card.intent || "本工程工具调用").slice(0, 96)}</p>
    <div class="card-meta">
      <span>分类：${escapeHtml(card.category)}</span>
      <span>类型：${escapeHtml(card.toolType)}</span>
      <span>阶段：${laneTitle(card.stage)}</span>
      <span>审核：${card.reviewStatus}</span>
      <span>复核：${riskLabels[card.riskLevel]}</span>
      <span>权重：${card.aiScore}</span>
    </div>
    <div class="card-actions">
      <button data-action="step">${primaryAction}</button>
      <button data-action="approve">通过</button>
      <button data-action="edit">编辑</button>
    </div>
  `;
  el.addEventListener("dragstart", e => e.dataTransfer.setData("text/plain", card.id));
  el.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", async e => {
      e.stopPropagation();
      await handleCardAction(card.id, btn.dataset.action);
    });
  });
  el.addEventListener("dblclick", () => openDialog(card.id));
  return el;
}

function renderMetrics() {
  const enriched = state.cards.map(enrichCard);
  const risk = enriched.filter(card => card.riskLevel === "high" || card.reviewStatus === "需复核").length;
  const approved = enriched.filter(card => card.stage === "approved").length;
  els.metricTotal.textContent = enriched.length;
  els.metricRisk.textContent = risk;
  els.metricAuto.textContent = enriched.length ? `${Math.round(approved / enriched.length * 100)}%` : "0%";
}

function renderToolPool() {
  const counts = toolInventory.reduce((acc, tool) => {
    acc[tool.category] = (acc[tool.category] || 0) + 1;
    return acc;
  }, {});
  els.toolPool.innerHTML = Object.entries(counts).slice(0, 12).map(([category, count]) => `
    <div class="tool-pool-item">
      <b>${escapeHtml(category)}</b>
      <span>${count}</span>
    </div>
  `).join("") || `<div class="tool-pool-item"><b>等待同步</b><span>0</span></div>`;
}

function renderPlanner() {
  const cards = state.cards.map(enrichCard).sort((a, b) => b.aiScore - a.aiScore);
  els.scheduleList.innerHTML = cards.map((card, index) => `
    <div class="schedule-item">
      <strong>${index + 1}. ${escapeHtml(card.toolName)}</strong>
      <small>${card.priority} · ${card.category} · ${laneTitle(card.stage)} · ${card.reviewStatus}</small>
    </div>
  `).join("");
  els.commandList.innerHTML = cards.map(card => `
    <div class="command-item">
      <strong>${escapeHtml(card.toolName)}</strong>
      <small>${flowCommand(card)}</small>
    </div>
  `).join("");
}

function renderLogs() {
  els.logList.innerHTML = state.logs.slice(0, 120).map(log => `
    <div class="log-item">
      <small>${new Date(log.time).toLocaleString()}</small>
      <div>${escapeHtml(log.message)}</div>
    </div>
  `).join("");
}

function filteredCards() {
  const q = els.searchInput.value.trim().toLowerCase();
  let cards = state.cards.filter(card => {
    const text = [card.toolName, card.intent, card.category, card.toolType, card.reviewStatus, card.target].join(" ").toLowerCase();
    return (!q || text.includes(q))
      && (els.categoryFilter.value === "全部分类" || card.category === els.categoryFilter.value)
      && (els.typeFilter.value === "全部类型" || card.toolType === els.typeFilter.value);
  });
  const mode = els.sortMode.value;
  cards.sort((a, b) => {
    const ea = enrichCard(a);
    const eb = enrichCard(b);
    if (mode === "stage") return stageScore(a.stage) - stageScore(b.stage);
    if (mode === "risk") return riskScore(b.riskLevel) - riskScore(a.riskLevel);
    if (mode === "updated") return new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0);
    return eb.aiScore - ea.aiScore;
  });
  return cards;
}

function autoClassifyAll(source) {
  state.cards = state.cards.map(autoClassify);
  addLog(`AI 自动分类：${source}，已按工具类型、调用风险和循环阶段重新规整。`);
}

function autoClassify(card) {
  const next = { ...card };
  next.category = next.category || "未分类";
  next.toolType = next.toolType || "未知类型";
  next.intent = next.intent || inferIntent(next);
  next.riskLevel = inferRisk(next);
  next.priority = next.priority || inferPriority(next);
  next.stage = next.stage || "queued";
  next.reviewStatus = normalizeReviewStatus(next);
  next.aiScore = computeAiScore(next);
  next.updatedAt = next.updatedAt || new Date().toISOString();
  return next;
}

async function runLoopStep(source) {
  const candidates = state.cards
    .filter(card => card.stage !== "approved" && card.reviewStatus !== "已阻断")
    .map(enrichCard)
    .sort((a, b) => b.aiScore - a.aiScore)
    .slice(0, 4);

  if (!candidates.length) {
    addLog(`循环空转：${source}，当前没有待推进工具调用卡片。`);
    return;
  }

  for (const candidate of candidates) {
    const index = state.cards.findIndex(card => card.id === candidate.id);
    if (index >= 0) state.cards[index] = await advanceCard(state.cards[index], source);
  }
}

async function advanceCard(card, source) {
  const next = { ...card, updatedAt: new Date().toISOString() };
  if (next.stage === "queued") {
    next.stage = "classified";
    next.reviewStatus = "待执行";
    trace(next, "完成工具语义分类与风险标记");
  } else if (next.stage === "classified") {
    next.stage = "executing";
    next.reviewStatus = "执行中";
    trace(next, "进入本地工具调用执行队列");
    return await executeCard(next, source);
  } else if (next.stage === "executing") {
    return await executeCard(next, source);
  } else if (next.stage === "review") {
    next.stage = "approved";
    next.reviewStatus = "已通过";
    trace(next, "审核通过，循环闭环完成");
  }
  addLog(`循环推进：${source}，${next.toolName} -> ${laneTitle(next.stage)} / ${next.reviewStatus}`);
  return autoClassify(next);
}

async function executeCard(card, source) {
  const next = { ...card, stage: "executing", reviewStatus: "执行中", updatedAt: new Date().toISOString() };
  trace(next, "开始调用后端执行接口 /api/execute");
  render();

  try {
    const res = await fetch("/api/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        toolName: next.toolName,
        target: next.target,
        category: next.category,
        toolType: next.toolType
      })
    });
    const data = await res.json();
    next.lastExecution = data;
    if (!res.ok || !data.ok) {
      next.stage = "review";
      next.reviewStatus = "执行失败";
      trace(next, `执行失败：${data.error || data.message || res.status}`);
      addLog(`执行失败：${next.toolName}，${data.error || data.message || res.status}`);
      return autoClassify(next);
    }
    next.stage = "review";
    next.reviewStatus = next.riskLevel === "high" ? "需复核" : "待审核";
    trace(next, `执行已启动：${data.message}`);
    addLog(`执行成功：${source}，${next.toolName} 已启动并提交审核。`);
    return autoClassify(next);
  } catch (err) {
    next.stage = "review";
    next.reviewStatus = "执行失败";
    next.lastExecution = { ok: false, error: String(err) };
    trace(next, `执行接口异常：${err}`);
    addLog(`执行接口异常：${next.toolName}，${err}`);
    return autoClassify(next);
  }
}

function toggleLoop() {
  if (loopTimer) {
    clearInterval(loopTimer);
    loopTimer = null;
    els.btnToggleLoop.textContent = "开始循环";
    addLog("自动循环已停止。");
    render();
    return;
  }
  loopTimer = setInterval(async () => {
    await runLoopStep("auto_loop");
    saveState();
    render();
  }, 2600);
  els.btnToggleLoop.textContent = "停止循环";
  addLog("自动循环已启动：系统将持续分类、执行、提交审核并流转到审核通过。");
  render();
}

async function handleCardAction(id, action) {
  if (action === "edit") return openDialog(id);
  const index = state.cards.findIndex(card => card.id === id);
  if (index < 0) return;
  const card = state.cards[index];
  if (action === "approve") {
    const next = { ...card, stage: "approved", reviewStatus: "已通过", updatedAt: new Date().toISOString() };
    trace(next, "人工审核通过");
    addLog(`审核通过：${next.toolName} 已进入通过分栏。`);
    state.cards[index] = autoClassify(next);
  }
  if (action === "step") {
    state.cards[index] = await advanceCard(card, "single_card");
  }
  saveState();
  render();
}

function onDrop(event) {
  const id = event.dataTransfer.getData("text/plain");
  const targetStage = event.currentTarget.dataset.laneBody;
  state.cards = state.cards.map(card => card.id === id ? autoClassify({
    ...card,
    stage: targetStage,
    reviewStatus: statusForStage(targetStage, card.riskLevel),
    updatedAt: new Date().toISOString()
  }) : card);
  addLog(`人工调整：工具调用卡片 ${id.slice(0, 8)} 调整到 ${laneTitle(targetStage)}。`);
  saveState();
  render();
}

function openDialog(id) {
  editingId = id || null;
  const card = state.cards.find(c => c.id === id) || {};
  document.querySelector("#dialogTitle").textContent = id ? "编辑工具调用卡片" : "新增工具调用卡片";
  document.querySelector("#btnDeleteCard").style.visibility = id ? "visible" : "hidden";
  for (const field of new FormData(els.form).keys()) {
    const input = els.form.elements[field];
    if (!input) continue;
    if (field === "context") input.value = card.context ? JSON.stringify(card.context, null, 2) : "";
    else input.value = card[field] || "";
  }
  els.dialog.showModal();
}

function saveCardFromDialog(event) {
  if (event.submitter?.value === "cancel") return;
  event.preventDefault();
  const data = Object.fromEntries(new FormData(els.form).entries());
  let context = {};
  try {
    context = data.context.trim() ? JSON.parse(data.context) : {};
  } catch {
    alert("执行上下文 JSON 格式不正确");
    return;
  }
  const card = autoClassify({
    id: editingId || crypto.randomUUID(),
    toolName: data.toolName.trim(),
    category: data.category.trim() || "未分类",
    toolType: data.toolType.trim() || "未知类型",
    target: data.target.trim(),
    intent: data.intent.trim(),
    priority: data.priority,
    stage: data.stage,
    reviewStatus: data.reviewStatus,
    context,
    executionTrace: [],
    lastExecution: null,
    updatedAt: new Date().toISOString()
  });
  state.cards = editingId ? state.cards.map(c => c.id === editingId ? { ...c, ...card } : c) : [card, ...state.cards];
  addLog(`${editingId ? "更新" : "创建"}工具调用卡片：${card.toolName}，AI 已重新分类并写入循环队列。`);
  els.dialog.close();
  saveState();
  render();
}

function deleteEditingCard() {
  if (!editingId) return;
  const card = state.cards.find(c => c.id === editingId);
  state.cards = state.cards.filter(c => c.id !== editingId);
  addLog(`删除工具调用卡片：${card?.toolName || editingId}`);
  els.dialog.close();
  saveState();
  render();
}

function inferIntent(tool) {
  const text = `${tool.name || tool.toolName || ""} ${tool.category || ""} ${tool.description || ""}`;
  if (/scan|扫描|探测|finger|dir|目录|收集/.test(text)) return "本地信息收集与识别调用";
  if (/report|报告|generate|导出|分析/.test(text)) return "本地结果分析与报告生成调用";
  if (/web|页面|demo|serve|前端/.test(text)) return "本地 Web 页面或前端分析调用";
  if (/java|jar|gui|图形/.test(text)) return "本地 GUI 工具启动调用";
  return "本工程工具调用";
}

function inferRisk(card) {
  const text = `${card.toolName} ${card.category} ${card.toolType} ${card.intent} ${card.target}`.toLowerCase();
  if (/webshell|后渗透|爆破|exploit|payload|shell|bypass|远控|漏洞/.test(text)) return "high";
  if (/scan|扫描|探测|收集|代理|抓包|mirror|download/.test(text)) return "medium";
  return "low";
}

function inferPriority(card) {
  if (card.riskLevel === "high") return "P0";
  if (card.riskLevel === "medium") return "P1";
  if (/报告|分析|生成|workflow|card/i.test(`${card.toolName} ${card.intent}`)) return "P2";
  return "P3";
}

function normalizeReviewStatus(card) {
  if (card.reviewStatus === "执行失败") return "执行失败";
  if (card.stage === "approved") return "已通过";
  if (card.stage === "review" && card.riskLevel === "high") return card.reviewStatus === "已通过" ? "已通过" : "需复核";
  if (card.reviewStatus && reviewStatuses.includes(card.reviewStatus)) return card.reviewStatus;
  return statusForStage(card.stage, card.riskLevel);
}

function statusForStage(stage, riskLevel) {
  if (stage === "queued") return "待分类";
  if (stage === "classified") return "待执行";
  if (stage === "executing") return "执行中";
  if (stage === "review") return riskLevel === "high" ? "需复核" : "待审核";
  if (stage === "approved") return "已通过";
  return "待分类";
}

function enrichCard(card) {
  const next = autoClassify(card);
  next.aiScore = computeAiScore(next);
  return next;
}

function computeAiScore(card) {
  return priorityScore(card.priority) * 1000
    + riskScore(card.riskLevel) * 180
    + (5 - stageScore(card.stage)) * 90
    + (card.reviewStatus === "需复核" ? 360 : 0)
    + (card.reviewStatus === "执行失败" ? 420 : 0);
}

function flowCommand(card) {
  if (card.reviewStatus === "执行失败") return "流转指令：执行失败，查看日志后修正工具路径、运行环境或参数。";
  if (card.stage === "queued") return "流转指令：读取工具字段，按分类、类型、路径和用途自动归类。";
  if (card.stage === "classified") return "流转指令：点击执行或进入循环，后端将按 config/tools.json allowlist 启动工具。";
  if (card.stage === "executing") return "流转指令：正在调用本地执行接口，完成后提交审核。";
  if (card.stage === "review" && card.riskLevel === "high") return "流转指令：高风险工具调用需要复核，复核后通过闭环。";
  if (card.stage === "review") return "流转指令：低中风险调用可审核通过。";
  return "流转指令：已审核通过，工具调用卡片闭环归档。";
}

function updateFilters() {
  fillSelect(els.categoryFilter, ["全部分类", ...unique(toolInventory.map(tool => tool.category))]);
  fillSelect(els.typeFilter, ["全部类型", ...unique(toolInventory.map(tool => tool.type))]);
}

function fillFormOptions() {
  fillSelect(els.form.elements.priority, priorities);
  fillSelect(els.form.elements.stage, stages);
  fillSelect(els.form.elements.reviewStatus, reviewStatuses);
}

function fillSelect(select, values) {
  select.innerHTML = values.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
}

function exportData() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `tool-call-loop-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function importData(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      state = {
        cards: Array.isArray(data.cards) ? data.cards : [],
        logs: Array.isArray(data.logs) ? data.logs : [],
        loopRuns: Number(data.loopRuns || 0)
      };
      autoClassifyAll("json_import");
      saveState();
      render();
    } catch {
      alert("导入失败：JSON 文件无法解析");
    }
  };
  reader.readAsText(file, "utf-8");
  event.target.value = "";
}

function switchView(view) {
  document.querySelectorAll(".nav-tab").forEach(btn => btn.classList.toggle("active", btn.dataset.view === view));
  document.querySelectorAll(".view").forEach(section => section.classList.remove("active"));
  document.querySelector(`#${view}View`).classList.add("active");
}

function trace(card, message) {
  card.executionTrace = Array.isArray(card.executionTrace) ? card.executionTrace : [];
  card.executionTrace.push({ time: new Date().toISOString(), message });
}

function addLog(message) {
  state.logs.unshift({ time: new Date().toISOString(), message });
  state.logs = state.logs.slice(0, 260);
}

function loadState() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (stored && Array.isArray(stored.cards)) return stored;
  } catch {}
  return {
    cards: [],
    logs: [{ time: new Date().toISOString(), message: "系统初始化：等待同步本工程工具并生成工具调用卡片。" }],
    loopRuns: 0
  };
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function laneTitle(id) {
  return lanes.find(lane => lane.id === id)?.title || id;
}

function stageScore(stage) {
  return { queued: 0, classified: 1, executing: 2, review: 3, approved: 4 }[stage] ?? 0;
}

function priorityScore(priority) {
  return { P0: 4, P1: 3, P2: 2, P3: 1 }[priority] || 1;
}

function riskScore(risk) {
  return { high: 3, medium: 2, low: 1 }[risk] || 1;
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b), "zh-CN"));
}

function fallbackTools() {
  return [
    { name: "本地 Web 演示服务", category: "网页工具", type: "Python", description: "启动本地静态页面服务", path: "scripts/serve_local_web_demo.py" },
    { name: "六阶段模拟工作流", category: "本地模拟", type: "Python", description: "执行本地六阶段模拟并生成结果", path: "scripts/teach_six_phase_simulation_run.py" },
    { name: "自动报告生成", category: "报告工具", type: "Python", description: "汇总本地结果并生成报告", path: "scripts/auto_report_generate.py" }
  ];
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[ch]);
}
