async () => {
  const results = [];
  const check = async (name, fn) => {
    DOMPurify.removeAllHooks();
    DOMPurify.clearConfig();
    document.body.replaceChildren();
    try {
      await fn();
      results.push({ name, pass: true });
    } catch (error) {
      results.push({ name, pass: false, error: String(error) });
    }
  };
  const assert = (condition) => {
    if (!condition) throw new Error("Sanitizer security contract failed");
  };
  await check("attached-shadow-template-expression", () => {
    const host = document.createElement("div");
    const shadow = host.attachShadow({ mode: "open" });
    shadow.append(
      document.createTextNode("{"),
      document.createElement("script"),
      document.createTextNode("{7*7}}"),
    );
    DOMPurify.sanitize(host, { SAFE_FOR_TEMPLATES: true, IN_PLACE: true });
    assert(!/\{\{[\s\S]*\}\}/.test(shadow.textContent));
  });
  const image = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
  for (const mode of ["parent", "nextSibling"]) {
    await check(`hook-detaches-${mode}`, async () => {
      window.__patchMarker = 0;
      const root = document.createElement("div");
      root.innerHTML = `<figure><img class="bad" src="${image}"><img id="evil" src="${image}" onload="window.__patchMarker++"></figure><p>ok</p>`;
      const evil = root.querySelector("#evil");
      DOMPurify.addHook("afterSanitizeAttributes", (node) => {
        if (node.getAttribute?.("class") === "bad") {
          if (mode === "parent") node.parentNode.remove();
          else node.nextElementSibling.remove();
        }
      });
      DOMPurify.sanitize(root, { IN_PLACE: true });
      await new Promise((resolve) => setTimeout(resolve, 150));
      assert(evil.getAttribute("onload") === null && window.__patchMarker === 0);
    });
  }
  await check("xhtml-smil-href-rewrite", () => {
    const clean = DOMPurify.sanitize(
      '<svg xmlns="http://www.w3.org/2000/svg"><a><animate attributeName="href" values="x;javascript:window.__patchMarker++" dur="0.01s" fill="freeze"/></a></svg>',
      {
        PARSER_MEDIA_TYPE: "application/xhtml+xml",
        ALLOWED_TAGS: ["svg", "a", "animate"],
        ALLOWED_ATTR: ["attributeName", "values", "dur", "fill"],
      },
    );
    assert(!/attributeName=["']href["']/i.test(clean));
  });
  return results;
};
