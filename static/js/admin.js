/* =============================================================
   WMAA Admin Panel — admin.js   (static/js/admin.js)
   ============================================================= */

/* ── Scroll Fix ─────────────────────────────────────────────────
   style.css sets overflow:hidden on body/html for hero animations.
   This runs immediately (before DOMContentLoaded) and overrides it
   on every admin page with !important via setProperty.
   ─────────────────────────────────────────────────────────────── */
document.documentElement.style.setProperty('overflow-y', 'auto', 'important');
document.documentElement.style.setProperty('overflow-x', 'hidden', 'important');

/* ── Image Upload Preview ────────────────────────────────────── */
function previewImg(input, boxId) {
  const box  = document.getElementById(boxId);
  const file = input.files[0];
  if (!file || !box) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    box.innerHTML = `<img class="preview" src="${e.target.result}" alt="Preview" />`;
    box.classList.add('has-image');
  };
  reader.readAsDataURL(file);
}

/* ── Table Text Search ───────────────────────────────────────── */
function filterTable(tbodyId, query) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  const q = query.toLowerCase();
  tbody.querySelectorAll('tr[data-type], tr[data-status], tr[data-category]').forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

/* ── Filter by Event Type ────────────────────────────────────── */
function filterByType(type) {
  const tbody = document.getElementById('eventsBody');
  if (!tbody) return;
  tbody.querySelectorAll('tr[data-type]').forEach((row) => {
    row.style.display = (type === 'all' || row.dataset.type === type) ? '' : 'none';
  });
}

/* ── Filter by Category ──────────────────────────────────────── */
function filterByCategory(cat) {
  const tbody = document.getElementById('newsBody');
  if (!tbody) return;
  tbody.querySelectorAll('tr[data-category]').forEach((row) => {
    row.style.display = (cat === 'all' || row.dataset.category === cat) ? '' : 'none';
  });
}

/* ── Filter by Status ────────────────────────────────────────── */
function filterByStatus(status, btn) {
  document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'));
  btn.classList.add('active');
  ['volsBody', 'donationsBody'].forEach((id) => {
    const tbody = document.getElementById(id);
    if (!tbody) return;
    tbody.querySelectorAll('tr[data-status]').forEach((row) => {
      row.style.display = (status === 'all' || row.dataset.status === status) ? '' : 'none';
    });
  });
}

/* ── Delete Confirmation ─────────────────────────────────────── */
function confirmDelete(label) {
  return confirm('Are you sure you want to delete ' + label + '? This cannot be undone.');
}

/* ── Export Table to CSV ─────────────────────────────────────── */
function exportCSV() {
  const table = document.getElementById('donationsTable');
  if (!table) return;
  const csv = Array.from(table.querySelectorAll('tr')).map((row) =>
    Array.from(row.cells).map((c) => '"' + c.textContent.trim().replace(/"/g, '""') + '"').join(',')
  ).join('\n');
  const a    = document.createElement('a');
  a.href     = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = 'wmaa-donations.csv';
  a.click();
}

/* ── Open Edit Modal — Events ────────────────────────────────── */
function openEditEvent(event) {
  const form = document.getElementById('editEventForm');
  if (!form) return;
  form.action = '/admin/events/' + event.id + '/edit';
  document.getElementById('editEventTitle').value    = event.title       || '';
  document.getElementById('editEventDate').value     = event.date        || '';
  document.getElementById('editEventTime').value     = event.time        || '';
  document.getElementById('editEventLocation').value = event.location    || '';
  document.getElementById('editEventDesc').value     = event.description || '';
  document.getElementById('editEventType').value     = event.event_type  || 'upcoming';
  document.getElementById('editEventCategory').value = event.category    || 'Fundraiser';
  new bootstrap.Modal(document.getElementById('editEventModal')).show();
}

/* ── Open Edit Modal — News ──────────────────────────────────── */
function openEditNews(article) {
  const form = document.getElementById('editNewsForm');
  if (!form) return;
  form.action = '/admin/news/' + article.id + '/edit';
  document.getElementById('editNewsTitle').value    = article.title        || '';
  document.getElementById('editNewsCategory').value = article.category     || 'community';
  document.getElementById('editNewsDate').value     = article.date         || '';
  document.getElementById('editNewsExcerpt').value  = article.excerpt      || '';
  document.getElementById('editNewsContent').value  = article.full_content || '';
  new bootstrap.Modal(document.getElementById('editNewsModal')).show();
}

/* ── Open Edit Modal — Stories ───────────────────────────────── */
function openEditStory(story) {
  const form = document.getElementById('editStoryForm');
  if (!form) return;
  form.action = '/admin/stories/' + story.id + '/edit';
  document.getElementById('editStoryTitle').value    = story.title    || '';
  document.getElementById('editStoryCategory').value = story.category || 'Community';
  document.getElementById('editStoryContent').value  = story.content  || '';
  new bootstrap.Modal(document.getElementById('editStoryModal')).show();
}

/* ── Password Toggle ─────────────────────────────────────────── */
function togglePw() {
  const input = document.getElementById('pwInput');
  const icon  = document.getElementById('pwIcon');
  if (!input || !icon) return;
  input.type     = input.type === 'password' ? 'text' : 'password';
  icon.className = input.type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
}

/* ── DOMContentLoaded ────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

  /* Re-apply scroll fix after all CSS has loaded */
  document.documentElement.style.setProperty('overflow-y', 'auto', 'important');
  document.body.style.setProperty('overflow-y', 'auto', 'important');
  document.body.style.setProperty('overflow-x', 'hidden', 'important');

  /* Services accordion */
  document.querySelectorAll('.accordion-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const panel   = document.getElementById(btn.dataset.target);
      const chevron = btn.querySelector('.chevron-icon');
      if (!panel) return;
      const isOpen        = panel.style.display !== 'none';
      panel.style.display = isOpen ? 'none' : 'block';
      if (chevron) chevron.classList.toggle('open', !isOpen);
    });
  });

});