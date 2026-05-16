// ── DOM refs ───────────────────────────────────────────────────────
const editor        = document.getElementById('code-editor');
const highlight     = document.getElementById('code-highlight');
const lineNumbers   = document.getElementById('line-numbers');
const runBtn        = document.getElementById('run-btn');
const runStopBtn    = document.getElementById('run-stop-btn');
const clearBtn      = document.getElementById('clear-btn');
const clearOutputBtn= document.getElementById('clear-output-btn');
const output        = document.getElementById('output');
const copyOutputBtn = document.getElementById('copy-output-btn');
const togglePanelBtn= document.getElementById('toggle-panel-btn');
const tabFilename   = document.getElementById('tab-filename');
const titlebarFile  = document.getElementById('titlebar-filename');
const bcFilename    = document.getElementById('bc-filename');
const tabDot        = document.getElementById('tab-dot');
const cursorPos     = document.getElementById('cursor-pos');
const terminalPanel = document.getElementById('terminal-panel');
const editorPane    = document.getElementById('editor-pane');
const varsBody      = document.getElementById('vars-body');
const terminalTabs  = document.querySelectorAll('.terminal-tab');
const panelContents = document.querySelectorAll('.panel-content');
const debugBtn            = document.getElementById('debug-btn');
const explorerActivityBtn = document.getElementById('explorer-activity-btn');
const debugActivityBtn    = document.getElementById('debug-activity-btn');
const debugStepBtn      = document.getElementById('debug-step-btn');
const debugCmdStepBtn   = document.getElementById('debug-cmd-step-btn');
const debugContinueBtn  = document.getElementById('debug-continue-btn');
const debugStopBtn      = document.getElementById('debug-stop-btn');
const debugStatusText   = document.getElementById('debug-status-text');
const debugLineText     = document.getElementById('debug-line-text');
const debugStackView    = document.getElementById('debug-stack-view');
const debugBpList       = document.getElementById('debug-bp-list');
const debugLineOverlay  = document.getElementById('debug-line-overlay');
const debugVarsWrap     = document.getElementById('debug-vars-wrap');
const debugArraysWrap   = document.getElementById('debug-arrays-wrap');

// ── Examples ───────────────────────────────────────────────────────
const examples = {
  main: '',
  hello: `# "Hello World!"를 출력하는 코드
# H: 72
..........~야옹 .......~야옹
냐냐냐냐~야옹 냥~~야옹 냥~야옹 ..~야옹 냐냐~야옹 냥~~야옹
냥!!??야옹

# e: 101
..........~야옹 ..........~야옹
냐냐냐냐~야옹 냥냥~~야옹 냥냥~야옹 .~야옹 냐냐~야옹 냥냥~~야옹
냥냥!!??야옹

# l: 108
냥냥~야옹 .......~야옹
냐냐~야옹 냥냥냥~~야옹 냥냥냥~야옹
냥냥냥!!??야옹

# l: 108
냥냥~야옹 .......~야옹
냐냐~야옹 냥냥냥~~야옹 냥냥냥~야옹
냥냥냥!!??야옹

# o: 111
...~야옹 냐냐~야옹 냥냥냥냥~~야옹
냥냥냥냥!!???야옹

# W: 87
냥~야옹 ...............~야옹
냐냐~야옹 냥~~야옹 냥!!??야옹

# o: 111
냥냥냥냥!!??야옹

# r: 114
냥냥냥냥~야옹 ...~야옹 냐냐~야옹 냥냥냥냥냥~~야옹
냥냥냥냥냥!!??야옹

# l: 108
냥냥냥!!??야옹

# d: 100
냥냥~야옹 .~야옹 냐냐냐~야옹 냥냥~~야옹
냥냥!!??야옹

# !: 33
...~야옹 ...........~야옹 냐냐냐냐~야옹 냥~~야옹
냥!!??야옹`,

  loop: `냥.야옹 냥냥.....야옹
냥!?야옹 냥~야옹 .~야옹 냐냐~야옹 냥~~야옹
냥냥~야옹 ,~야옹 냐냐~야옹 냥냥~~야옹
냥냥?..야옹`,

  input: `냥??야옹 냥!?야옹`,

  gugudan: `# 구구단 (2단 ~ 9단)
# 변수1: i (단), 변수2: j, 변수3: i*j 결과, 변수4: 루프 조건

냥..야옹                                              # (1)  i = 2
냥냥.야옹                                             # (2)  j = 1  ← 내부 루프 시작
냥~야옹 냥냥~야옹 냐냐냐냐~야옹 냥냥냥~~야옹          # (3)  변수3 = i * j
냥냥냥!???야옹                                         # (4)  결과 출력 (공백 구분)
냥냥~야옹 .~야옹 냐냐~야옹 냥냥~~야옹                 # (5)  j = j + 1
냥냥~야옹 ..........~야옹 냐냐냐~야옹 냥냥냥냥~~야옹  # (6)  변수4 = j - 10
냥냥냥냥?...야옹                                       # (7)  변수4 ≠ 0 (j ≠ 10) 이면 line 3
..........!!??야옹                                     # (8)  줄바꿈 출력 (chr(10))
냥~야옹 .~야옹 냐냐~야옹 냥~~야옹                     # (9)  i = i + 1
냥~야옹 ..........~야옹 냐냐냐~야옹 냥냥냥냥~~야옹    # (10) 변수4 = i - 10
냥냥냥냥?..야옹                                        # (11) 변수4 ≠ 0 (i ≠ 10) 이면 line 2`,

  gugudan_input: `냥??야옹
냥냥.야옹

......~야옹 .......~야옹 냐냐냐냐~야옹 냥냥냥~~야옹
......~야옹 ..........~야옹 냐냐냐냐~야옹 냥냥냥냥~~야옹 냥냥냥냥~야옹 .~야옹 냐냐~야옹 냥냥냥냥~~야옹
냥~야옹 냥냥~야옹 냐냐냐냐~야옹 냥냥냥냥냥~~야옹
냥!???야옹 냥냥냥!!???야옹 냥냥!???야옹 냥냥냥냥!!???야옹 냥냥냥냥냥!?야옹
냥냥~야옹 .~야옹 냐냐~야옹 냥냥~~야옹 냥냥~야옹 ..........~야옹 냐냐냐~야옹 냥냥냥냥냥냥~~야옹
냥냥냥냥냥냥?....야옹`
};

// ── State ──────────────────────────────────────────────────────────
let currentErrorLine = null;
let ws = null;
let isDirty = false;

// ── Syntax Highlighting ────────────────────────────────────────────
function _esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function _hlCode(code) {
  let h = _esc(code);
  h = h.replace(/야옹/g,  '<span class="hl-yaong">야옹</span>');
  h = h.replace(/냥+/g,   m => `<span class="hl-nyang">${m}</span>`);
  h = h.replace(/냐+/g,   m => `<span class="hl-nya">${m}</span>`);
  h = h.replace(/[.,]+/g, m => `<span class="hl-num">${m}</span>`);
  h = h.replace(/[~!?]+/g,m => `<span class="hl-op">${m}</span>`);
  return h;
}

// 야옹 구분자로 cmdIdx번 명령어의 문자 범위 [start, end) 반환
function getCommandRange(code, cmdIdx) {
  const ends = [];
  let pos = 0;
  while (pos < code.length) {
    const found = code.indexOf('야옹', pos);
    if (found === -1) break;
    ends.push(found + 2);
    pos = found + 2;
  }
  if (cmdIdx >= ends.length) return null;
  return {
    start: cmdIdx === 0 ? 0 : ends[cmdIdx - 1],
    end: ends[cmdIdx],
  };
}

function highlightLine(rawLine, cmdHighlightIdx = -1) {
  const ci = rawLine.indexOf('#');
  const code    = ci === -1 ? rawLine : rawLine.slice(0, ci);
  const comment = ci === -1 ? '' : rawLine.slice(ci);
  const commentHtml = comment ? `<span class="hl-comment">${_esc(comment)}</span>` : '';

  if (cmdHighlightIdx >= 0) {
    const range = getCommandRange(code, cmdHighlightIdx);
    if (range) {
      const before = code.slice(0, range.start);
      const cmd    = code.slice(range.start, range.end);
      const after  = code.slice(range.end);
      return _hlCode(before)
        + `<span class="hl-cmd-active">${_hlCode(cmd)}</span>`
        + _hlCode(after)
        + commentHtml;
    }
  }
  return _hlCode(code) + commentHtml;
}

function highlightCode(text) {
  return text.split('\n').map(line => highlightLine(line)).join('\n');
}

function updateHighlight() {
  highlight.innerHTML   = highlightCode(editor.value);
  highlight.scrollTop   = editor.scrollTop;
  highlight.scrollLeft  = editor.scrollLeft;
}

// ── Line numbers ───────────────────────────────────────────────────
function updateLineNumbers(errorLine = null) {
  const text = editor.value || '';
  const lines = text.split('\n').length;
  let buf = '';
  for (let i = 1; i <= lines; i++) {
    const isBp = debugBreakpoints.has(i);
    const cls = i === errorLine ? 'ln-error' : (isBp ? 'ln-bp' : '');
    const marker = isBp ? '●' : i;
    if (cls) {
      buf += `<span class="${cls}" data-line="${i}">${marker}</span>\n`;
    } else {
      buf += `<span data-line="${i}">${i}</span>\n`;
    }
  }
  lineNumbers.innerHTML = buf;
  lineNumbers.style.transform = `translateY(${-editor.scrollTop}px)`;

  if (errorLine) {
    currentErrorLine = errorLine;
    const lh = 24;
    const targetScroll = Math.max(0, (errorLine - 1) * lh - editor.clientHeight / 3);
    editor.scrollTo({ top: targetScroll, behavior: 'smooth' });
    lineNumbers.style.transform = `translateY(${-targetScroll}px)`;
  }
}

// ── Dirty indicator ────────────────────────────────────────────────
function setDirty(val) {
  isDirty = val;
  tabDot.classList.toggle('dot-visible', val);
}

// ── Cursor position ────────────────────────────────────────────────
function updateCursorPos() {
  const pos = editor.selectionStart;
  const text = editor.value.substring(0, pos);
  const lines = text.split('\n');
  const ln = lines.length;
  const col = lines[lines.length - 1].length + 1;
  cursorPos.textContent = `Ln ${ln}, Col ${col}`;
}

// ── Debug state ────────────────────────────────────────────────────
let debugWs = null;
let debugMode = false;
let debugBreakpoints = new Set();
let debugCmdHighlight = null;  // { line, cmdIdx } | null
const LINE_HEIGHT = 24;

const debugCmdBox = document.getElementById('debug-cmd-box');

// canvas로 텍스트 픽셀 너비를 측정
let _measureCtx = null;
function measurePx(text) {
  if (!_measureCtx) {
    _measureCtx = document.createElement('canvas').getContext('2d');
    _measureCtx.font = '600 13px "JetBrains Mono", monospace';
  }
  return _measureCtx.measureText(text).width;
}

// 명령어 박스를 canvas 측정값 기반으로 픽셀 단위 배치
function updateCmdHighlightLayer() {
  if (!debugCmdBox) return;
  if (!debugCmdHighlight) {
    debugCmdBox.style.display = 'none';
    return;
  }
  const { line: targetLine, cmdIdx } = debugCmdHighlight;
  const lines = editor.value.split('\n');
  const rawLine = lines[targetLine - 1] ?? '';
  const ci = rawLine.indexOf('#');
  const code = ci === -1 ? rawLine : rawLine.slice(0, ci);
  const range = getCommandRange(code, cmdIdx);
  if (!range) { debugCmdBox.style.display = 'none'; return; }

  const before  = code.slice(0, range.start);
  const cmdText = code.slice(range.start, range.end);
  const editorPadLeft = 16;   // #code-highlight padding-left
  const editorPadTop  = 14;   // #code-highlight padding-top

  const x = editorPadLeft + measurePx(before) - editor.scrollLeft;
  const y = editorPadTop  + (targetLine - 1) * LINE_HEIGHT - editor.scrollTop + 1;
  const w = measurePx(cmdText);

  debugCmdBox.style.display = 'block';
  debugCmdBox.style.left    = x + 'px';
  debugCmdBox.style.top     = y + 'px';
  debugCmdBox.style.width   = w + 'px';
}

function switchToPanel(panelId) {
  terminalTabs.forEach(t => t.classList.remove('tt-active'));
  panelContents.forEach(p => p.classList.toggle('panel-active', p.id === panelId));
  const tab = document.querySelector(`[data-panel="${panelId}"]`);
  if (tab) tab.classList.add('tt-active');
}

function renderDebugVars(vars) {
  if (!vars || Object.keys(vars).length === 0) {
    debugVarsWrap.innerHTML = '<span class="dbg-empty">없음</span>';
    return;
  }
  let html = '<table class="dbg-var-table">';
  for (const [k, v] of Object.entries(vars)) {
    html += `<tr><td class="dv-name">변수${k}</td><td class="dv-val">${v}</td></tr>`;
  }
  html += '</table>';
  debugVarsWrap.innerHTML = html;
}

function renderDebugArrays(arrays) {
  if (!arrays || Object.keys(arrays).length === 0) {
    debugArraysWrap.innerHTML = '<span class="dbg-empty">없음</span>';
    return;
  }
  let html = '';
  for (const [k, arr] of Object.entries(arrays)) {
    const cells = arr.map((v, i) =>
      `<span class="dbg-cell" title="[${i}]">${v}</span>`
    ).join('');
    html += `<div class="dbg-array-row"><span class="dbg-arr-name">배열${k}</span><span class="dbg-arr-cells">${cells}</span></div>`;
  }
  debugArraysWrap.innerHTML = html;
}

function showSidebarDebug() {
  document.getElementById('sidebar-explorer-body').style.display = 'none';
  document.getElementById('debug-sidebar-body').style.display = 'flex';
  document.getElementById('sidebar-header').textContent = '실행 및 디버그';
  document.querySelectorAll('.activity-btn').forEach(b => b.classList.remove('ab-active'));
  debugActivityBtn.classList.add('ab-active');
}

function showSidebarExplorer() {
  document.getElementById('debug-sidebar-body').style.display = 'none';
  document.getElementById('sidebar-explorer-body').style.display = '';
  document.getElementById('sidebar-header').textContent = '탐색기';
  document.querySelectorAll('.activity-btn').forEach(b => b.classList.remove('ab-active'));
  explorerActivityBtn.classList.add('ab-active');
}

function setDebugActive(active) {
  debugMode = active;
  debugStepBtn.disabled = !active;
  debugCmdStepBtn.disabled = !active;
  debugContinueBtn.disabled = !active;
  debugStopBtn.disabled = !active;
  debugBtn.disabled = active;
  runBtn.disabled = active;
  if (active) {
    debugBtn.textContent = '🐞 디버깅 중…';
    showSidebarDebug();
  } else {
    debugBtn.textContent = '🐞 디버그';
    highlightDebugLine(null);
    debugStatusText.textContent = '종료됨';
    debugCmdHighlight = null;
    updateCmdHighlightLayer();
    renderDebugVars({});
    renderDebugArrays({});
    showSidebarExplorer();
  }
}

function highlightDebugLine(lineNo) {
  if (!lineNo) {
    debugLineOverlay.style.display = 'none';
    lineNumbers.querySelectorAll('.ln-debug').forEach(el => el.classList.remove('ln-debug'));
    return;
  }
  const top = 14 + (lineNo - 1) * LINE_HEIGHT;
  debugLineOverlay.style.top = top + 'px';
  debugLineOverlay.style.display = 'block';
  debugLineOverlay.style.transform = `translateY(${-editor.scrollTop}px)`;
}

function renderBreakpoints() {
  // 라인 번호 렌더링 시 브레이크포인트 마커 반영
  updateLineNumbers(currentErrorLine);
  // 브레이크포인트 목록 표시
  if (debugBreakpoints.size === 0) {
    debugBpList.textContent = '없음';
  } else {
    debugBpList.textContent = [...debugBreakpoints].sort((a,b)=>a-b).map(l => `${l}번 줄`).join(', ');
  }
}

function startDebug() {
  if (debugWs) { debugWs.close(); debugWs = null; }
  const code = editor.value.trim();
  if (!code) return;

  clearOutput();
  clearVariables();
  currentErrorLine = null;
  updateLineNumbers(null);
  setDebugActive(true);
  debugStatusText.textContent = '시작 중…';
  debugLineText.textContent = '-';
  debugStackView.textContent = '-';

  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  debugWs = new WebSocket(`${protocol}//${location.host}/ws/debug`);

  debugWs.onopen = () => {
    debugWs.send(JSON.stringify({
      code,
      breakpoints: [...debugBreakpoints],
    }));
  };

  debugWs.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === 'debug_paused') {
      const ln = msg.line;
      debugStatusText.textContent = `${ln}번 줄에서 일시정지`;
      debugLineText.textContent = ln;
      debugStackView.textContent = msg.stack.length
        ? msg.stack.slice().reverse().join('\n')
        : '(비어 있음)';
      renderVariables(msg.variables || {});
      renderDebugVars(msg.variables || {});
      renderDebugArrays(msg.arrays || {});
      highlightDebugLine(ln);
      debugCmdHighlight = null;
      updateCmdHighlightLayer();
      const targetScroll = Math.max(0, (ln - 1) * LINE_HEIGHT - editor.clientHeight / 3);
      editor.scrollTo({ top: targetScroll, behavior: 'smooth' });

    } else if (msg.type === 'debug_cmd_paused') {
      const ln = msg.line;
      const ci = msg.cmd_index + 1;
      debugStatusText.textContent = `${ln}번 줄의 ${ci}번째 명령어에서 일시정지`;
      debugLineText.textContent = `${ln} (명령어 ${ci})`;
      debugStackView.textContent = msg.stack.length
        ? msg.stack.slice().reverse().join('\n')
        : '(비어 있음)';
      renderVariables(msg.variables || {});
      renderDebugVars(msg.variables || {});
      renderDebugArrays(msg.arrays || {});
      highlightDebugLine(ln);
      debugCmdHighlight = { line: ln, cmdIdx: msg.cmd_index };
      updateCmdHighlightLayer();
      const targetScroll = Math.max(0, (ln - 1) * LINE_HEIGHT - editor.clientHeight / 3);
      editor.scrollTo({ top: targetScroll, behavior: 'smooth' });

    } else if (msg.type === 'output') {
      appendOutput(msg.data);

    } else if (msg.type === 'input_request') {
      showInputPrompt(msg.prompt);

    } else if (msg.type === 'debug_done') {
      setDebugActive(false);
      if (msg.status === 'error') {
        updateLineNumbers(msg.error_line || null);
        const lineInfo = msg.error_line ? ` (${msg.error_line}번 줄)` : '';
        appendOutput(`\n❌${lineInfo} ${msg.error_msg}\n`, true);
        debugStatusText.textContent = '오류 종료';
      } else {
        appendOutput('\n\n─── 디버깅 완료 ───\n', false);
        renderVariables(msg.variables || {});
        renderDebugVars(msg.variables || {});
        renderDebugArrays(msg.arrays || {});
        debugStatusText.textContent = '완료';
      }
      debugWs = null;
    }
  };

  debugWs.onerror = () => {
    appendOutput('❌ 디버그 연결 오류\n', true);
    setDebugActive(false);
    debugWs = null;
  };

  debugWs.onclose = () => {
    if (debugMode) setDebugActive(false);
    debugWs = null;
  };
}

// ── Panel tab switching ────────────────────────────────────────────
terminalTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    terminalTabs.forEach(t => t.classList.remove('tt-active'));
    tab.classList.add('tt-active');
    const target = tab.dataset.panel;
    panelContents.forEach(p => {
      p.classList.toggle('panel-active', p.id === target);
    });
  });
});

// ── Variables panel ────────────────────────────────────────────────
function renderVariables(vars) {
  if (!vars || Object.keys(vars).length === 0) {
    varsBody.innerHTML = '<tr class="vars-placeholder"><td colspan="2">실행 결과 변수가 없습니다.</td></tr>';
    return;
  }
  varsBody.innerHTML = Object.entries(vars)
    .map(([k, v]) => `<tr><td>변수 ${k}</td><td>${v}</td></tr>`)
    .join('');
}

function clearVariables() {
  varsBody.innerHTML = '<tr class="vars-placeholder"><td colspan="2">실행 후 변수 상태가 표시됩니다.</td></tr>';
}

// ── Output helpers ─────────────────────────────────────────────────
function clearOutput() {
  output.innerHTML = '';
}

function appendOutput(text, isError = false) {
  const span = document.createElement('span');
  span.textContent = text;
  if (isError) span.classList.add('out-error');
  output.appendChild(span);
  output.scrollTop = output.scrollHeight;
}

// ── Terminal input prompt ──────────────────────────────────────────
function showInputPrompt(prompt) {
  const line = document.createElement('span');
  line.className = 'terminal-input-line';

  const promptSpan = document.createElement('span');
  promptSpan.className = 'terminal-prompt';
  promptSpan.textContent = prompt;

  const inputEl = document.createElement('input');
  inputEl.type = 'text';
  inputEl.className = 'terminal-input';

  line.appendChild(promptSpan);
  line.appendChild(inputEl);
  output.appendChild(line);
  output.scrollTop = output.scrollHeight;
  setTimeout(() => inputEl.focus(), 0);

  inputEl.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    const value = inputEl.value;
    const staticSpan = document.createElement('span');
    staticSpan.textContent = prompt + value + '\n';
    line.replaceWith(staticSpan);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'input', value }));
    } else if (debugWs && debugWs.readyState === WebSocket.OPEN) {
      debugWs.send(JSON.stringify({ type: 'input', value }));
    }
  });
}

// ── Run ────────────────────────────────────────────────────────────
function resetRunBtn() {
  runBtn.disabled = false;
  runBtn.innerHTML = `<img src="/static/images/paw-btn-transparent.png" class="run-paw" aria-hidden="true" /> 실행`;
  runStopBtn.style.display = 'none';
}

function runCode() {
  const code = editor.value;
  if (!code.trim()) {
    clearOutput();
    appendOutput('⚠  코드가 비어 있습니다. 무언가를 작성해 주세요.\n', true);
    return;
  }

  if (ws) { ws.close(); ws = null; }

  clearOutput();
  clearVariables();
  currentErrorLine = null;
  updateLineNumbers(null);
  runBtn.disabled = true;
  runBtn.innerHTML = `<img src="/static/images/paw-btn-transparent.png" class="run-paw run-paw-spin" aria-hidden="true" /> 실행 중…`;
  runStopBtn.style.display = '';

  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${protocol}//${location.host}/ws/run`);

  ws.onopen = () => ws.send(JSON.stringify({ code }));

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'output') {
      appendOutput(msg.data);
    } else if (msg.type === 'input_request') {
      showInputPrompt(msg.prompt);
    } else if (msg.type === 'done') {
      resetRunBtn();
      if (msg.status === 'error') {
        updateLineNumbers(msg.error_line || null);
        const lineInfo = msg.error_line ? ` (${msg.error_line}번 줄)` : '';
        appendOutput(`\n❌${lineInfo} ${msg.error_msg}\n`, true);
      } else {
        appendOutput('\n\n─── 실행 완료 ───\n', false);
        renderVariables(msg.variables || {});
      }
    }
  };

  ws.onerror = () => {
    appendOutput('❌  연결 오류가 발생했습니다.\n', true);
    resetRunBtn();
  };

  ws.onclose = () => {
    if (runBtn.disabled) resetRunBtn();
  };
}

// ── Folder toggle ──────────────────────────────────────────────
const folderToggle   = document.getElementById('folder-toggle');
const folderArrow    = document.getElementById('folder-arrow');
const folderContents = document.getElementById('sidebar-files');
let folderOpen = true;

folderToggle.addEventListener('click', () => {
  folderOpen = !folderOpen;
  folderContents.classList.toggle('folder-collapsed', !folderOpen);
  folderArrow.textContent = folderOpen ? '▾' : '▸';
});

// ── Sidebar file click ─────────────────────────────────────────────
document.getElementById('sidebar-files').addEventListener('click', (e) => {
  const item = e.target.closest('.file-item');
  if (!item) return;

  document.querySelectorAll('.file-item').forEach(f => f.classList.remove('fi-active'));
  item.classList.add('fi-active');

  const fileKey  = item.dataset.file;
  const filename = item.dataset.name;

  tabFilename.textContent   = filename;
  titlebarFile.textContent  = filename;
  bcFilename.textContent    = filename;

  editor.value = examples[fileKey] || '';
  updateLineNumbers();
  updateHighlight();
  setDirty(false);
  clearOutput();
  updateCursorPos();
});

// ── Panel resize ───────────────────────────────────────────────────
const panelResizer = document.getElementById('panel-resizer');
let isResizingPanel = false;
let resizeStartY    = 0;
let resizeStartH    = 0;

panelResizer.addEventListener('mousedown', (e) => {
  isResizingPanel = true;
  resizeStartY    = e.clientY;
  resizeStartH    = terminalPanel.getBoundingClientRect().height;
  document.body.classList.add('resizing-v');
});

document.addEventListener('mousemove', (e) => {
  if (!isResizingPanel) return;
  const dy = resizeStartY - e.clientY;
  const newH = Math.max(60, Math.min(resizeStartH + dy, window.innerHeight * 0.75));
  terminalPanel.style.height = newH + 'px';
});

document.addEventListener('mouseup', () => {
  isResizingPanel = false;
  document.body.classList.remove('resizing-v');
});

// ── Sidebar resize ─────────────────────────────────────────────────
const sidebarResizer = document.getElementById('sidebar-resizer');
const sidebar        = document.getElementById('sidebar');
let isResizingSidebar = false;
let sbStartX  = 0;
let sbStartW  = 0;

sidebarResizer.addEventListener('mousedown', (e) => {
  isResizingSidebar = true;
  sbStartX = e.clientX;
  sbStartW = sidebar.getBoundingClientRect().width;
  document.body.classList.add('resizing-h');
});

document.addEventListener('mousemove', (e) => {
  if (!isResizingSidebar) return;
  const dx  = e.clientX - sbStartX;
  const newW = Math.max(120, Math.min(sbStartW + dx, 500));
  sidebar.style.width = newW + 'px';
});

document.addEventListener('mouseup', () => {
  isResizingSidebar = false;
  document.body.classList.remove('resizing-h');
});

// ── Toggle panel ───────────────────────────────────────────────────
let panelVisible = true;
togglePanelBtn.addEventListener('click', () => {
  panelVisible = !panelVisible;
  terminalPanel.style.display  = panelVisible ? '' : 'none';
  panelResizer.style.display   = panelVisible ? '' : 'none';
});

// ── Editor events ──────────────────────────────────────────────────
editor.addEventListener('input', () => {
  currentErrorLine = null; // Clear error on edit
  updateLineNumbers(null);
  updateHighlight();
  setDirty(true);
  updateCursorPos();
});

let _scrollRaf = null;
editor.addEventListener('scroll', () => {
  if (_scrollRaf) return;
  _scrollRaf = requestAnimationFrame(() => {
    _scrollRaf = null;
    const st = editor.scrollTop;
    const sl = editor.scrollLeft;
    lineNumbers.style.transform         = `translateY(${-st}px)`;
    highlight.scrollTop                 = st;
    highlight.scrollLeft                = sl;
    if (debugCmdHighlight) updateCmdHighlightLayer();
    if (debugLineOverlay.style.display !== 'none') {
      debugLineOverlay.style.transform  = `translateY(${-st}px)`;
    }
  });
});

editor.addEventListener('click', updateCursorPos);
editor.addEventListener('keyup', updateCursorPos);

editor.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    runCode();
  }
  // Tab key → insert 2 spaces
  if (e.key === 'Tab') {
    e.preventDefault();
    const start = editor.selectionStart;
    const end   = editor.selectionEnd;
    editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
    editor.selectionStart = editor.selectionEnd = start + 2;
    updateLineNumbers(null);
    updateHighlight();
  }
});

// ── Button events ──────────────────────────────────────────────────
runBtn.addEventListener('click', runCode);

runStopBtn.addEventListener('click', () => {
  if (ws) { ws.close(); ws = null; }
  appendOutput('\n⏹ 실행이 중단되었습니다.\n', true);
  resetRunBtn();
});

debugBtn.addEventListener('click', startDebug);

explorerActivityBtn.addEventListener('click', showSidebarExplorer);
debugActivityBtn.addEventListener('click', showSidebarDebug);

debugStepBtn.addEventListener('click', () => {
  if (debugWs) debugWs.send(JSON.stringify({ type: 'debug_step' }));
});

debugCmdStepBtn.addEventListener('click', () => {
  if (debugWs) debugWs.send(JSON.stringify({ type: 'debug_cmd_step' }));
});

debugContinueBtn.addEventListener('click', () => {
  if (debugWs) {
    highlightDebugLine(null);
    debugWs.send(JSON.stringify({ type: 'debug_continue' }));
    debugStatusText.textContent = '실행 중…';
  }
});

debugStopBtn.addEventListener('click', () => {
  if (debugWs) debugWs.send(JSON.stringify({ type: 'debug_stop' }));
});

// 라인 번호 클릭 → 브레이크포인트 토글
lineNumbers.addEventListener('click', (e) => {
  const el = e.target.closest('[data-line]');
  if (!el) return;
  const ln = parseInt(el.dataset.line);
  if (debugBreakpoints.has(ln)) debugBreakpoints.delete(ln);
  else debugBreakpoints.add(ln);
  renderBreakpoints();
  if (debugWs && debugMode) {
    debugWs.send(JSON.stringify({ type: 'debug_set_breakpoints', lines: [...debugBreakpoints] }));
  }
});

clearBtn.addEventListener('click', () => {
  if (ws) { ws.close(); ws = null; }
  if (debugWs) { debugWs.close(); debugWs = null; }
  if (debugMode) setDebugActive(false);
  editor.value = '';
  debugBreakpoints.clear();
  renderBreakpoints();
  updateLineNumbers(null);
  updateHighlight();
  setDirty(false);
  clearOutput();
  updateCursorPos();
});

clearOutputBtn.addEventListener('click', clearOutput);

copyOutputBtn.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(output.innerText || ''); }
  catch (err) { console.error(err); }
});

// ── Init ───────────────────────────────────────────────────────────
updateLineNumbers();
updateHighlight();
updateCursorPos();
