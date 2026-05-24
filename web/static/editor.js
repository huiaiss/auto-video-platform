/* ═══════════════════════════════════════════════════════
   Auto Video Platform — Visual Editor Application
   ═══════════════════════════════════════════════════════ */

// ── State ──────────────────────────────────────────
const state = {
  projectId: null,
  assets: [],
  report: null,
  script: null,
  tts: null,
  previewHtml: null,
  audioUrl: null,
  totalDuration: 0,
  playing: false,
  currentTime: 0,
};

// ── DOM refs ───────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const dom = {
  projectId: $('#project-id'),
  videoType: $('#video-type'),
  brandName: $('#brand-name'),
  uploadZone: $('#upload-zone'),
  fileInput: $('#file-input'),
  assetList: $('#asset-list'),
  reportContent: $('#report-content'),
  timeline: $('#timeline'),
  totalDuration: $('#total-duration'),
  previewFrame: $('#preview-frame'),
  previewTime: $('#preview-time'),
  btnPlay: $('#btn-play'),
  btnMute: $('#btn-mute'),
  seekBar: $('#seek-bar'),
  audioPlayer: $('#audio-player'),
  audioPlaceholder: $('#audio-placeholder'),
  audioDuration: $('#audio-duration'),
  scriptEditor: $('#script-editor'),
  storyboardBody: $('#storyboard-table tbody'),
  srtDisplay: $('#srt-display'),
  ttsVoice: $('#tts-voice'),
  ttsSpeed: $('#tts-speed'),
  ttsSpeedVal: $('#tts-speed-val'),
  toast: $('#toast'),
  loading: $('#loading'),
  loadingMsg: $('#loading-msg'),
  statusText: $('#topbar-status'),
};

// ── Init ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupUpload();
  setupTabs();
  setupTTSControls();
});

// ═══════════════════════════════════════════════════
// Tab switching
// ═══════════════════════════════════════════════════
function setupTabs() {
  document.querySelectorAll('.panel-tabs').forEach((bar) => {
    bar.addEventListener('click', (e) => {
      const tab = e.target.closest('.tab');
      if (!tab) return;
      const paneId = tab.dataset.tab;
      // Deactivate siblings
      bar.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      // Show matching pane
      const parent = bar.parentElement;
      parent.querySelectorAll('.pane').forEach((p) => p.classList.remove('active'));
      const pane = parent.querySelector('#' + paneId);
      if (pane) pane.classList.add('active');
    });
  });
}

// ═══════════════════════════════════════════════════
// Upload
// ═══════════════════════════════════════════════════
function setupUpload() {
  const zone = dom.uploadZone;
  const input = dom.fileInput;

  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
  });
  input.addEventListener('change', () => handleFiles(input.files));
}

function handleFiles(fileList) {
  if (!fileList.length) return;
  const files = Array.from(fileList);
  // Show preview
  dom.assetList.innerHTML = '';
  files.forEach((f) => {
    const url = URL.createObjectURL(f);
    const isVideo = f.type.startsWith('video/');
    const div = document.createElement('div');
    div.className = 'asset-item';
    div.innerHTML = isVideo
      ? `<div class="thumb" style="display:flex;align-items:center;justify-content:center;font-size:20px;">&#9654;</div>`
      : `<img class="thumb" src="${url}" />`;
    div.innerHTML += `<span class="name">${f.name}</span>`;
    div.innerHTML += `<span class="badge">${isVideo ? '视频' : '图片'}</span>`;
    dom.assetList.appendChild(div);
  });
  // Store for upload
  state.pendingFiles = files;
  dom.statusText.textContent = `${files.length} 个文件待上传`;
}

// ═══════════════════════════════════════════════════
// TTS Controls
// ═══════════════════════════════════════════════════
function setupTTSControls() {
  dom.ttsSpeed.addEventListener('input', () => {
    dom.ttsSpeedVal.textContent = parseFloat(dom.ttsSpeed.value).toFixed(1) + 'x';
  });
}

// ═══════════════════════════════════════════════════
// Workflow Steps
// ═══════════════════════════════════════════════════

async function stepUpload() {
  if (!state.pendingFiles || !state.pendingFiles.length) {
    showToast('请先选择素材文件', 'error');
    return;
  }

  showLoading('正在上传并分析素材...');
  setStepActive('upload');

  const form = new FormData();
  state.pendingFiles.forEach((f) => form.append('files', f));
  form.append('video_type', dom.videoType.value);

  try {
    const resp = await fetch('/api/upload', { method: 'POST', body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || '上传失败');

    state.projectId = data.project_id;
    state.report = data.report;
    state.assets = data.assets;
    dom.projectId.textContent = state.projectId;

    renderAssets();
    renderReport();
    enableStep('generate');
    setStepDone('upload');
    dom.statusText.textContent = '分析完成';
    showToast(`分析完成：${state.assets.length} 个素材`, 'success');
  } catch (err) {
    showToast('上传失败: ' + err.message, 'error');
  } finally {
    hideLoading();
  }
}

async function stepGenerate() {
  if (!state.projectId) return;

  showLoading('正在生成脚本...');
  setStepActive('generate');

  const form = new FormData();
  form.append('project_id', state.projectId);
  form.append('video_type', dom.videoType.value);
  form.append('brand_name', dom.brandName.value);

  try {
    const resp = await fetch('/api/generate', { method: 'POST', body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || '生成失败');

    state.script = data.script;
    renderTimeline();
    renderScriptEditor();
    renderStoryboardTable();
    enableStep('tts');
    enableStep('preview');
    setStepDone('generate');
    dom.statusText.textContent = '脚本已生成';
    showToast('脚本生成成功', 'success');
  } catch (err) {
    showToast('脚本生成失败: ' + err.message, 'error');
  } finally {
    hideLoading();
  }
}

async function stepTTS() {
  if (!state.projectId) return;

  showLoading('正在合成语音...');
  setStepActive('tts');

  const form = new FormData();
  form.append('project_id', state.projectId);
  form.append('voice', dom.ttsVoice.value);
  form.append('speed', dom.ttsSpeed.value);

  try {
    const resp = await fetch('/api/tts', { method: 'POST', body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || 'TTS失败');

    state.tts = data;
    state.audioUrl = data.audio_url;
    state.totalDuration = data.duration_s;

    // Setup audio player
    dom.audioPlayer.src = data.audio_url;
    dom.audioPlayer.style.display = 'block';
    dom.audioPlaceholder.style.display = 'none';
    dom.audioDuration.textContent = formatTime(data.duration_s);

    // Show SRT
    dom.srtDisplay.textContent = data.srt || '(无字幕数据)';

    setStepDone('tts');
    enableStep('export');
    dom.statusText.textContent = `TTS完成 (${data.duration_s.toFixed(1)}s)`;
    showToast('语音合成成功', 'success');
  } catch (err) {
    showToast('TTS失败: ' + err.message, 'error');
  } finally {
    hideLoading();
  }
}

function stepPreview() {
  if (!state.script) return;

  showLoading('正在生成预览...');
  setStepActive('preview');

  const form = new FormData();
  form.append('project_id', state.projectId);

  fetch('/api/preview', { method: 'POST', body: form })
    .then((r) => r.text())
    .then((html) => {
      state.previewHtml = html;
      loadPreview(html);
      setStepDone('preview');
      dom.statusText.textContent = '预览就绪';
      hideLoading();
    })
    .catch((err) => {
      showToast('预览生成失败: ' + err.message, 'error');
      hideLoading();
    });
}

async function stepExport() {
  if (!state.projectId) return;

  showLoading('正在导出MP4 (最长5分钟)...');
  setStepActive('export');

  const form = new FormData();
  form.append('project_id', state.projectId);
  form.append('fps', '24');

  try {
    const resp = await fetch('/api/export', { method: 'POST', body: form });
    const data = await resp.json();

    if (data.error) {
      showToast('导出失败: ' + data.error, 'error');
      return;
    }

    setStepDone('export');
    dom.statusText.textContent = `导出完成 (${data.size_mb}MB)`;

    // Trigger download
    const a = document.createElement('a');
    a.href = data.video_url;
    a.download = `${state.projectId}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    showToast(`视频导出成功 (${data.size_mb}MB)`, 'success');
  } catch (err) {
    showToast('导出失败: ' + err.message, 'error');
  } finally {
    hideLoading();
  }
}

// ═══════════════════════════════════════════════════
// Rendering
// ═══════════════════════════════════════════════════

function renderAssets() {
  dom.assetList.innerHTML = '';
  state.assets.forEach((name) => {
    const url = `/api/asset/${state.projectId}/${name}`;
    const div = document.createElement('div');
    div.className = 'asset-item';
    div.innerHTML = `<img class="thumb" src="${url}" /><span class="name">${name}</span>`;
    dom.assetList.appendChild(div);
  });
}

function renderReport() {
  if (!state.report) return;
  const results = state.report.results || [state.report];
  let html = '';

  results.forEach((r, ri) => {
    html += `<div style="padding:8px 10px;font-size:11px;color:var(--accent);font-weight:600;">素材 ${ri + 1}: ${r.image || '—'}</div>`;

    (r.detector_results || []).forEach((d) => {
      if (d.error) return;
      (d.findings || []).forEach((f) => {
        const sev = f.severity || 'low';
        const isFlaw = ['face', 'hand', 'text', 'texture'].includes(d.detector);
        const labelClass = isFlaw ? 'flaw' : 'quality';
        const scorePct = ((f.score || 0) * 100).toFixed(0);
        html += `<div class="finding-item severity-${sev}">
          <span class="detector-label ${labelClass}">${d.detector}</span>
          <span style="font-size:10px;color:var(--text-secondary)">score=${(f.score || 0).toFixed(2)}</span>
          <div class="desc">${f.desc}</div>
          <div class="details">${f.details || ''}</div>
          <div class="score-bar"><div class="score-bar-fill ${sev}" style="width:${scorePct}%"></div></div>
        </div>`;
      });
    });
  });

  dom.reportContent.innerHTML = html || '<div class="report-placeholder">未检测到显著特征</div>';
}

function renderTimeline() {
  if (!state.script || !state.script.storyboard) return;

  const shots = state.script.storyboard;
  dom.timeline.innerHTML = '';
  let totalSec = 0;

  shots.forEach((shot, i) => {
    const dur = parseDuration(shot.duration);
    totalSec += dur;

    const assetIdx = i % state.assets.length;
    const imgUrl = state.assets.length
      ? `/api/asset/${state.projectId}/${state.assets[assetIdx]}`
      : '';

    const card = document.createElement('div');
    card.className = 'shot-card';
    card.dataset.index = i;
    card.innerHTML = `
      ${imgUrl ? `<img class="shot-img" src="${imgUrl}" />` : '<div class="shot-img"></div>'}
      <div class="shot-info">
        <span class="shot-num">镜头 ${shot.shot || i + 1}</span>
        <span class="shot-dur">${shot.duration}</span>
        <div class="shot-cap">${shot.caption || '(无字幕)'}</div>
      </div>`;
    card.addEventListener('click', () => selectShot(card, i));
    dom.timeline.appendChild(card);
  });

  dom.totalDuration.textContent = formatTime(totalSec);
}

function renderScriptEditor() {
  if (!state.script) return;
  dom.scriptEditor.value = JSON.stringify(state.script, null, 2);
}

function renderStoryboardTable() {
  if (!state.script || !state.script.storyboard) return;
  const tbody = dom.storyboardBody;
  tbody.innerHTML = '';

  state.script.storyboard.forEach((shot, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${shot.shot || i + 1}</td>
      <td><input value="${shot.duration || '5s'}" data-field="duration" data-idx="${i}" /></td>
      <td><textarea rows="1" data-field="visual" data-idx="${i}">${shot.visual || ''}</textarea></td>
      <td><textarea rows="1" data-field="audio" data-idx="${i}">${shot.audio || ''}</textarea></td>
      <td><textarea rows="1" data-field="caption" data-idx="${i}">${shot.caption || ''}</textarea></td>
      <td><button class="del-btn" onclick="deleteShot(${i})">✕</button></td>`;
    tbody.appendChild(tr);
  });
}

// ═══════════════════════════════════════════════════
// Preview
// ═══════════════════════════════════════════════════

function loadPreview(html) {
  const frame = dom.previewFrame;
  frame.srcdoc = html;
  // Wait for iframe to load before enabling controls
  frame.onload = function() {
    enablePreviewControls();
  };
}

function enablePreviewControls() {
  dom.btnPlay.disabled = false;
  dom.seekBar.disabled = false;
  dom.btnMute.disabled = false;
}

function togglePlay() {
  const frame = dom.previewFrame;
  const ctrl = frame.contentWindow && frame.contentWindow.previewControls;
  if (!ctrl) return;

  state.playing = !state.playing;
  dom.btnPlay.textContent = state.playing ? '⏸' : '▶';

  if (state.playing) {
    ctrl.play();
  } else {
    ctrl.pause();
  }

  // Sync audio
  const audio = dom.audioPlayer;
  if (audio.src && !audio.src.endsWith('blank')) {
    if (state.playing) {
      audio.currentTime = state.currentTime;
      audio.play().catch(function() {});
    } else {
      audio.pause();
    }
  }

  if (state.playing) {
    requestAnimationFrame(tickPreview);
  }
}

function tickPreview() {
  if (!state.playing) return;

  const frame = dom.previewFrame;
  if (frame.contentWindow && frame.contentWindow.previewControls) {
    state.currentTime = frame.contentWindow.previewControls.getTime();
  }

  // Sync audio
  const audio = dom.audioPlayer;
  if (audio.src && !audio.paused && Math.abs(audio.currentTime - state.currentTime) > 0.3) {
    // Don't fight the user if they scrubbed audio
  }

  updatePreviewUI();
  requestAnimationFrame(tickPreview);
}

function updatePreviewUI() {
  const total = state.totalDuration || 30;
  dom.previewTime.textContent = formatTime(state.currentTime) + ' / ' + formatTime(total);
  dom.seekBar.max = total;
  dom.seekBar.value = state.currentTime;
}

function seekPreview(value) {
  const t = parseFloat(value);
  state.currentTime = t;

  const frame = dom.previewFrame;
  if (frame.contentWindow && frame.contentWindow.previewControls) {
    frame.contentWindow.previewControls.seek(t);
  }

  const audio = dom.audioPlayer;
  if (audio.src && !audio.src.endsWith('blank')) {
    audio.currentTime = t;
  }

  updatePreviewUI();
}

function toggleMute() {
  const audio = dom.audioPlayer;
  audio.muted = !audio.muted;
  dom.btnMute.textContent = audio.muted ? '🔇' : '🔊';
}

// ── Audio event sync ──
dom.audioPlayer.addEventListener('timeupdate', () => {
  if (state.playing) {
    state.currentTime = dom.audioPlayer.currentTime;
    // Push to preview
    const frame = dom.previewFrame;
    if (frame.contentWindow && frame.contentWindow.previewControls) {
      const frameTime = frame.contentWindow.previewControls.getTime();
      if (Math.abs(frameTime - state.currentTime) > 0.5) {
        frame.contentWindow.previewControls.seek(state.currentTime);
      }
    }
    updatePreviewUI();
  }
});

dom.audioPlayer.addEventListener('ended', () => {
  state.playing = false;
  dom.btnPlay.textContent = '▶';
});

// ═══════════════════════════════════════════════════
// Script Editing
// ═══════════════════════════════════════════════════

function applyScriptEdits() {
  try {
    state.script = JSON.parse(dom.scriptEditor.value);
    renderTimeline();
    renderStoryboardTable();
    showToast('脚本已更新', 'success');
  } catch (e) {
    showToast('JSON 格式错误: ' + e.message, 'error');
  }
}

function revertScriptEdits() {
  renderScriptEditor();
  showToast('已还原', 'success');
}

function applyStoryboardEdits() {
  const inputs = dom.storyboardBody.querySelectorAll('[data-field]');
  inputs.forEach((inp) => {
    const idx = parseInt(inp.dataset.idx);
    const field = inp.dataset.field;
    if (state.script.storyboard[idx]) {
      state.script.storyboard[idx][field] = inp.value;
    }
  });
  renderScriptEditor();
  renderTimeline();
  showToast('分镜表已更新', 'success');
}

function addShotRow() {
  if (!state.script) return;
  const newShot = { shot: state.script.storyboard.length + 1, duration: '5s', visual: '', audio: '', caption: '' };
  state.script.storyboard.push(newShot);
  renderStoryboardTable();
  renderScriptEditor();
}

function deleteShot(idx) {
  if (!state.script) return;
  state.script.storyboard.splice(idx, 1);
  // Re-number
  state.script.storyboard.forEach((s, i) => { s.shot = i + 1; });
  renderStoryboardTable();
  renderScriptEditor();
  renderTimeline();
}

// ═══════════════════════════════════════════════════
// Timeline Shot Selection
// ═══════════════════════════════════════════════════

function selectShot(card, index) {
  document.querySelectorAll('.shot-card').forEach((c) => c.classList.remove('selected'));
  card.classList.add('selected');
  // Scroll the storyboard table to this shot
  const rows = dom.storyboardBody.querySelectorAll('tr');
  if (rows[index]) rows[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ═══════════════════════════════════════════════════
// Workflow Helpers
// ═══════════════════════════════════════════════════

function enableStep(step) {
  document.querySelectorAll(`.wf-btn[data-step="${step}"]`).forEach((b) => { b.disabled = false; });
}

function setStepActive(step) {
  document.querySelectorAll('.wf-btn').forEach((b) => b.classList.remove('active'));
  const btn = document.querySelector(`.wf-btn[data-step="${step}"]`);
  if (btn) btn.classList.add('active');
}

function setStepDone(step) {
  const btn = document.querySelector(`.wf-btn[data-step="${step}"]`);
  if (btn) btn.classList.remove('active');
}

// ═══════════════════════════════════════════════════
// UI Helpers
// ═══════════════════════════════════════════════════

function showToast(msg, type) {
  const t = dom.toast;
  t.textContent = msg;
  t.className = 'toast ' + (type || '');
  t.classList.remove('hidden');
  clearTimeout(t._timeout);
  t._timeout = setTimeout(() => t.classList.add('hidden'), 3000);
}

function showLoading(msg) {
  dom.loadingMsg.textContent = msg || '处理中...';
  dom.loading.classList.remove('hidden');
}

function hideLoading() {
  dom.loading.classList.add('hidden');
}

function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function parseDuration(d) {
  if (typeof d === 'number') return d;
  return parseFloat(String(d).replace(/[^0-9.]/g, '')) || 5;
}
