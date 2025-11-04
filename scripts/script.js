const BACKEND_URL = '/api/anonymous-message';

const form = document.getElementById('anonForm');
const messageEl = document.getElementById('message');
const topicEl = document.getElementById('topic');
const sendBtn = document.getElementById('sendBtn');
const btnLabel = document.getElementById('btnLabel');
const btnSpinner = document.getElementById('btnSpinner');
const feedbackText = document.getElementById('feedbackText');
const clearBtn = document.getElementById('clearBtn');
const chars = document.getElementById('chars');

// Update char count
messageEl.addEventListener('input', () => {
  chars.textContent = messageEl.value.length;
});

clearBtn.addEventListener('click', () => {
  if (topicEl) topicEl.value = '';
  messageEl.value = '';
  document.getElementById('sensitivity').value = 'normal';
  document.getElementById('delivery').value = 'team';
  chars.textContent = 0;
  feedbackText.textContent = '';
});

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  feedbackText.textContent = '';

  const message = messageEl.value.trim();
  if (!message) {
    feedbackText.innerHTML = '<span class="err">Please enter a message before sending.</span>';
    messageEl.focus();
    return;
  }

  const payload = {
    topic: topicEl ? (topicEl.value || '').trim() : '',
    message: message,
    sensitivity: document.getElementById('sensitivity').value,
    delivery: document.getElementById('delivery').value,
    timestamp_utc: new Date().toISOString()
  };

  sendBtn.disabled = true;
  btnSpinner.style.display = 'inline-block';
  btnLabel.textContent = 'Sending...';

  try {
    const res = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'omit'
    });

    if (!res.ok) {
      let errText = `Network error: ${res.status} ${res.statusText}`;
      try {
        const body = await res.json();
        if (body && body.error) errText = body.error;
      } catch (_) {}
      throw new Error(errText);
    }

    const data = await res.json().catch(() => ({}));
    if (data && data.ok === false) throw new Error(data.error || 'Server rejected the message.');

    feedbackText.innerHTML = '<span class="ok">Message sent anonymously. Thank you.</span>';
    messageEl.value = '';
    chars.textContent = 0;

  } catch (err) {
    console.error('Send error', err);
    feedbackText.innerHTML = `<span class="err">Failed to send: ${escapeHtml(err.message || String(err))}</span>`;
  } finally {
    sendBtn.disabled = false;
    btnSpinner.style.display = 'none';
    btnLabel.textContent = 'Send anonymously';
  }
});

function escapeHtml(unsafe) {
  return unsafe
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

window.addEventListener('load', () => {
  setTimeout(() => { messageEl.focus(); }, 200);
});
