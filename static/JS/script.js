/* ============================================================
   WMAA — WA Multicultural Assistance Alliance
   script.js  — multi-page version
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  const nav     = document.getElementById('mainNav');
  const backBtn = document.getElementById('backToTop');
  const page    = document.body.dataset.page || '';

  /* ── 1. Navbar: scroll behaviour ─────────────────────── */
  function updateNav() {
    // Inner pages always stay "scrolled" (white bg), home page toggles
    if (page === 'home') {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    } else {
      nav.classList.add('scrolled');
    }
  }
  window.addEventListener('scroll', updateNav, { passive: true });
  updateNav();


  /* ── 2. Navbar: close mobile menu on link click ───────── */
  document.querySelectorAll('#navMenu .nav-link, #navMenu .dropdown-item').forEach(link => {
    link.addEventListener('click', () => {
      const bsCollapse = bootstrap.Collapse.getInstance(document.getElementById('navMenu'));
      if (bsCollapse) bsCollapse.hide();
    });
  });


  /* ── 3. Active nav link: URL-based ───────────────────── */
  const currentFile = window.location.pathname.split('/').pop() || 'index.html';

  document.querySelectorAll('#navMenu .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    const linkFile = href.split('/').pop().split('#')[0] || 'index.html';
    if (linkFile === currentFile) {
      link.classList.add('active');
      // Also mark parent dropdown toggle if inside dropdown
      const dropdownParent = link.closest('.dropdown');
      if (dropdownParent) {
        dropdownParent.querySelector('.dropdown-toggle')?.classList.add('active');
      }
    }
  });


  /* ── 4. Scroll animations (IntersectionObserver) ──────── */
  const animatedEls = document.querySelectorAll('[data-animate]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => entry.target.classList.add('visible'), parseInt(delay));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  animatedEls.forEach(el => observer.observe(el));


  /* ── 5. Back to Top ────────────────────────────────────── */
  if (backBtn) {
    window.addEventListener('scroll', () => {
      backBtn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
    backBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }


  /* ── 6. Donate: amount selector ───────────────────────── */
  const donateBtns = document.querySelectorAll('.donate-btn');
  const donateLabel = document.getElementById('donateLabel');
  const customInput = document.getElementById('customAmount');
  const donationAmountInput = document.getElementById('donationAmountInput');

  if (donateBtns.length && donateLabel && donationAmountInput) {
    let selectedAmount = 50;
    donationAmountInput.value = selectedAmount;

    donateBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        donateBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedAmount = btn.dataset.amount;
        donateLabel.textContent = `$${selectedAmount}`;
        donationAmountInput.value = selectedAmount;
        if (customInput) customInput.value = '';
      });
    });

    if (customInput) {
      customInput.addEventListener('input', () => {
        const val = customInput.value.trim();
        if (val && Number(val) > 0) {
          donateBtns.forEach(b => b.classList.remove('active'));
          selectedAmount = val;
          donateLabel.textContent = `$${selectedAmount}`;
          donationAmountInput.value = selectedAmount;
        }
      });
    }
  }


  /* ── 7. Contact form ───────────────────────────────────── */
  const contactForm  = document.getElementById('contactForm');
  const formFeedback = document.getElementById('formFeedback');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!contactForm.checkValidity()) { contactForm.classList.add('was-validated'); return; }

      const name    = document.getElementById('contactName')?.value.trim();
      const email   = document.getElementById('contactEmail')?.value.trim();
      const subject = document.getElementById('contactSubject')?.value.trim();
      const message = document.getElementById('contactMessage')?.value.trim();

      // Mailto fallback — replace with backend API or form service (e.g. Formspree)
      const mailtoLink = `mailto:admin@wmaacharity.com.au?subject=${encodeURIComponent(subject || 'Website Enquiry')}&body=${encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\n${message}`)}`;
      window.location.href = mailtoLink;

      if (formFeedback) {
        formFeedback.style.display = 'block';
        formFeedback.innerHTML = `<div class="alert alert-success" role="alert"><i class="bi bi-check-circle me-2"></i>Thank you, <strong>${name}</strong>! Your message has been sent. We'll get back to you at <strong>${email}</strong> shortly.</div>`;
      }
      contactForm.reset();
      contactForm.classList.remove('was-validated');
    });
  }


  /* ── 8. News filter (news.html only) ───────────────────── */
  window.filterNews = function(category, btn) {
    document.querySelectorAll('.jump-link').forEach(b => b.classList.remove('active-filter'));
    btn.classList.add('active-filter');

    document.querySelectorAll('.news-item').forEach(item => {
      if (category === 'all' || item.dataset.category === category) {
        item.classList.remove('hidden');
      } else {
        item.classList.add('hidden');
      }
    });
  };


  /* ── 9. Smooth scroll for anchor links (same page) ──────── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const offset = (nav?.offsetHeight || 70) + 20;
        const top    = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });


  /* ── 10. Services jump nav: highlight on scroll ─────────── */
  if (page === 'services') {
    const servicesSections = document.querySelectorAll('.service-detail-section[id]');
    const jumpLinks        = document.querySelectorAll('.jump-link');

    window.addEventListener('scroll', () => {
      let current = '';
      servicesSections.forEach(sec => {
        if (window.scrollY >= sec.offsetTop - 150) current = sec.getAttribute('id');
      });
      jumpLinks.forEach(link => {
        link.classList.remove('active-filter');
        if (link.getAttribute('href') === `#${current}`) link.classList.add('active-filter');
      });
    }, { passive: true });
  }

});
