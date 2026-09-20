(function () {
  "use strict";
  var key = "lakokonyv-image-layout";
  var saved = JSON.parse(localStorage.getItem(key) || "{}"), layout = Object.assign({}, window.LAYOUT_DATA, saved);
  var grid = document.getElementById("image-grid");

  function settingFor(file) {
    var value = layout[file];
    return typeof value === "object" ? value : { width: Number(value || 100), invert: false };
  }

  function renderImage(item) {
    var setting = settingFor(item.file);
    var card = document.createElement("article");
    card.className = "image-card";
    card.innerHTML = '<h2>' + item.file + '</h2><div class="preview" style="--preview-width:' + setting.width + '%"><img src="../sources/images/' + item.file + '" alt="' + item.file + '"></div><label class="controls"><input type="range" min="25" max="100" step="1" value="' + setting.width + '"><output>' + setting.width + '%</output></label><label class="invert-control"><input type="checkbox" ' + (setting.invert ? 'checked' : '') + '> invertálható sötét módban</label>';
    var input = card.querySelector("input"), output = card.querySelector("output"), preview = card.querySelector(".preview");
    var invert = card.querySelector(".invert-control input");
    function save() {
      layout[item.file] = { width: Number(input.value), invert: invert.checked };
      localStorage.setItem(key, JSON.stringify(layout));
    }
    input.addEventListener("input", function () {
      output.value = input.value + "%";
      output.textContent = input.value + "%";
      preview.style.setProperty("--preview-width", input.value + "%");
      save();
    });
    invert.addEventListener("change", save);
    grid.appendChild(card);
  }
  window.IMAGE_DATA.forEach(renderImage);
  document.getElementById("reset-all").addEventListener("click", function () {
    layout = {};
    localStorage.removeItem(key);
    location.reload();
  });
  document.getElementById("export-layout").addEventListener("click", function () {
    var blob = new Blob([JSON.stringify(layout, null, 2) + "\n"], { type: "application/json" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "image_layout.json";
    link.click();
    URL.revokeObjectURL(link.href);
  });
})();
