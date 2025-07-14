// ========== script.js ==========
document.addEventListener('DOMContentLoaded', () => {
  const fileInput   = document.getElementById('pdfFile');
  const convertBtn  = document.getElementById('convertBtn');
  const progressBar = document.getElementById('progressBar');
  const statusText  = document.getElementById('statusText');

  const API_ROOT    = 'http://localhost:8080';

  const showMsg = msg => { statusText.textContent = msg; };
  const setBar  = pct => { progressBar.style.width = pct + '%'; };

  const resetUI = () => {
    setBar(0);
    showMsg('Choose a PDF and click Convert');
    convertBtn.disabled = false;
  };

  convertBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) { alert('Please choose a PDF file first.'); return; }

    const formData = new FormData();
    formData.append('pdf_file', file, file.name);
    formData.append('ocr_lang', 'eng');
    formData.append('dpi', '300');

    convertBtn.disabled = true;
    showMsg('Uploading PDF…');

    try {
      const res = await fetch(`${API_ROOT}/api/convert`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      await pollStatus(data.task_id);
    } catch (err) {
      alert('Error: ' + err.message);
      resetUI();
    }
  });

  async function pollStatus(taskId) {
    showMsg('Converting…');
    setBar(20);

    const poll = async () => {
      try {
        const res = await fetch(`${API_ROOT}/api/status?task_id=${taskId}`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const data = await res.json();

        if (data.status === 'processing') {
          setBar(data.progress || 50);
          setTimeout(poll, 3000);
        } else if (data.status === 'completed') {
          setBar(100);
          showMsg('Conversion complete! Downloading…');
          window.location = `${API_ROOT}${data.download_url}`;
          resetUI();
        } else {
          throw new Error(data.error || 'Conversion failed');
        }
      } catch (e) {
        alert('Error: ' + e.message);
        resetUI();
      }
    };

    poll();
  }

  resetUI();
});
