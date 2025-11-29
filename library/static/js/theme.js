(function () {
    const html = document.documentElement;
    const toggle = document.getElementById('themeToggle');
    const label = document.getElementById('themeLabel');

    if (!toggle || !label) return;

    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || saved === 'light') {
        html.setAttribute('data-bs-theme', saved);
    }
    applyState();

    toggle.addEventListener('change', function () {
        const next = toggle.checked ? 'dark' : 'light';
        html.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        applyState();
    });

    function applyState() {
        const mode = html.getAttribute('data-bs-theme') || 'light';
        toggle.checked = mode === 'dark';
        label.textContent = mode === 'dark' ? 'Тёмная тема' : 'Светлая тема';
    }
})();
