(function () {
  "use strict";

  var toc = document.querySelector(".toc");
  var article = document.querySelector(".book-content");

  var picker = document.querySelector(".color-picker");
  if (picker) {
    var storedColor = localStorage.getItem("lakokonyv-accent-color-v2");
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
