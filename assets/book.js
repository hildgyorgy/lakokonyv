(function () {
  "use strict";

  var toc = document.querySelector(".toc");
  var article = document.querySelector(".book-content");

  var languageData = document.getElementById("language-targets");
  if (languageData && article) {
    var languageTargets = JSON.parse(languageData.textContent);
    var locations = Array.prototype.slice.call(article.querySelectorAll("h1[id], h2[id], h3[id], h4[id], h5[id], h6[id], figure[id]"));
    var languageLinks = document.querySelectorAll(".language-switch a");
    var navigationTarget = decodeURIComponent(window.location.hash.slice(1));
    document.addEventListener("click", function (event) {
      var anchor = event.target.closest('a[href^="#"]');
      if (anchor) navigationTarget = decodeURIComponent(anchor.hash.slice(1));
    });
    window.addEventListener("hashchange", function () {
      navigationTarget = decodeURIComponent(window.location.hash.slice(1));
    });
    function clearNavigationTarget() { navigationTarget = ""; }
    window.addEventListener("wheel", clearNavigationTarget, { passive: true });
    window.addEventListener("touchmove", clearNavigationTarget, { passive: true });
    window.addEventListener("pointerdown", function (event) {
      if (!event.target.closest(".language-switch")) clearNavigationTarget();
    });
    window.addEventListener("keydown", function (event) {
      if (["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " "].indexOf(event.key) !== -1) clearNavigationTarget();
    });
    function updateLanguageLinks() {
      var current = "top";
      var threshold = window.innerHeight * 0.25;
      locations.forEach(function (element) {
        if (window.scrollY > 50 && element.getBoundingClientRect().top <= threshold) current = element.id;
      });
      if (navigationTarget && languageTargets[navigationTarget]) current = navigationTarget;
      languageLinks.forEach(function (link) {
        var ownLanguage = link.dataset.language === document.documentElement.lang;
        var target = ownLanguage ? current : (languageTargets[current] || "top");
        link.hash = target === "top" ? "" : target;
      });
    }
    languageLinks.forEach(function (link) {
      ["pointerdown", "focus", "click", "contextmenu"].forEach(function (event) {
        link.addEventListener(event, updateLanguageLinks);
      });
    });
  }

  // Direct deep links must settle before the observer opens TOC branches.
  // Image dimensions supplied by the build keep this position stable.
  if (window.location.hash) {
    var initialTarget = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if (initialTarget) initialTarget.scrollIntoView({ behavior: "instant", block: "start" });
  }

  var picker = document.querySelector(".color-picker");
  if (picker) {
    var storedColor = localStorage.getItem("lakokonyv-accent-color-v2");
    if (storedColor && storedColor.toLowerCase() === "#7b3f2a") storedColor = "#a75348";
    var swatches = picker.querySelectorAll(".color-swatch");
    function setAccent(color) {
      document.documentElement.style.setProperty("--accent", color);
      localStorage.setItem("lakokonyv-accent-color-v2", color);
      swatches.forEach(function (swatch) {
        swatch.classList.toggle("is-selected", swatch.dataset.color.toLowerCase() === color.toLowerCase());
      });
    }
    swatches.forEach(function (swatch) {
      swatch.addEventListener("click", function () { setAccent(swatch.dataset.color); });
    });
    setAccent(storedColor || "#8A2432");
  }

  var alignmentPicker = document.querySelector(".alignment-picker");
  if (alignmentPicker) {
    var storedAlignment = localStorage.getItem("lakokonyv-text-alignment-v1") || "left";
    var alignmentOptions = alignmentPicker.querySelectorAll(".alignment-option");
    function setAlignment(alignment) {
      document.querySelector(".book-content").classList.toggle("text-justified", alignment === "justify");
      localStorage.setItem("lakokonyv-text-alignment-v1", alignment);
      alignmentOptions.forEach(function (option) {
        option.classList.toggle("is-selected", option.dataset.alignment === alignment);
      });
    }
    alignmentOptions.forEach(function (option) {
      option.addEventListener("click", function () { setAlignment(option.dataset.alignment); });
    });
    setAlignment(storedAlignment === "justify" ? "justify" : "left");
  }

  if (!toc || !article || !window.IntersectionObserver) return;

  var links = {};
  toc.querySelectorAll('a[href^="#"]').forEach(function (link) {
    links[link.getAttribute("href").slice(1)] = link;
  });

  var headings = Array.prototype.filter.call(
    article.querySelectorAll("h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]"),
    function (heading) { return links[heading.id]; }
  );
  var visible = new Set();

  function preloadAhead(heading) {
    var images = Array.prototype.filter.call(
      article.querySelectorAll("img[loading=\"lazy\"]"),
      function (image) {
        return Boolean(heading.compareDocumentPosition(image) & Node.DOCUMENT_POSITION_FOLLOWING);
      }
    ).slice(0, 8);
    images.forEach(function (image, index) {
      image.loading = "eager";
      if (index < 3) image.fetchPriority = "high";
    });
  }

  toc.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function () {
      var target = document.getElementById(link.getAttribute("href").slice(1));
      if (target) {
        preloadAhead(target);
        if (links[target.id]) activate(target);
      }
    });
  });

  function activate(heading) {
    headings.forEach(function (item) {
      var link = links[item.id];
      link.classList.toggle("is-active", item === heading);
      if (item === heading) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });

    var activeLink = links[heading.id];
    var details = activeLink.closest("details");
    while (details) {
      details.open = true;
      details = details.parentElement.closest("details");
    }
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) visible.add(entry.target);
      else visible.delete(entry.target);
    });
    var current = headings.filter(function (heading) { return visible.has(heading); })[0];
    if (current) activate(current);
  }, { rootMargin: "-12% 0px -72% 0px", threshold: 0 });

  headings.forEach(function (heading) { observer.observe(heading); });

  var imageObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.loading = "eager";
      imageObserver.unobserve(entry.target);
    });
  }, { rootMargin: "1400px 0px 1400px 0px", threshold: 0 });
  article.querySelectorAll("img[loading=\"lazy\"]").forEach(function (image) {
    imageObserver.observe(image);
  });

})();
