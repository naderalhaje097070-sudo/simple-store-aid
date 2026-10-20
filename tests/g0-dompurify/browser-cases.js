async () => {
  const results = [];
  const check = async (name, fn) => {
    DOMPurify.removeAllHooks();
    DOMPurify.clearConfig();
    try {
      const details = await fn();
      results.push({ name, pass: true, details });
    } catch (error) {
      results.push({ name, pass: false, error: String(error) });
    } finally {
      document.body.replaceChildren();
    }
  };
  const assert = (condition, message) => {
    if (!condition) throw new Error(message);
  };
  for (const kind of ["regex", "function"]) {
    await check(`c2j3-custom-${kind}`, () => {
      const seen = [];
      DOMPurify.addHook("afterSanitizeElements", (node) => {
        seen.push(node.nodeName);
        node.removeAttribute?.("data-note");
      });
      const config = {
        CUSTOM_ELEMENT_HANDLING: {
          tagNameCheck: kind === "regex" ? /^x-note$/ : (tag) => tag === "x-note",
        },
      };
      const clean = DOMPurify.sanitize(
        '<div data-note="private">ok</div><x-note data-note="private">safe</x-note>',
        config,
      );
      assert(!clean.includes("data-note"), "custom post-element policy skipped");
      assert(
        seen.includes("X-NOTE") && clean.includes("<x-note>safe</x-note>"),
        "custom element not visited or lost",
      );
      return { clean, seen };
    });
  }
  const image = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
  const detached = async (hook) => {
    window.__localMarker = 0;
    const root = document.createElement("div");
    root.innerHTML = `<footer><img src="${image}" onload="window.__localMarker++"></footer><div>safe</div>`;
    const img = root.querySelector("img");
    if (hook)
      DOMPurify.addHook(hook, (node) => {
        if (node.nodeName === "FOOTER") node.remove();
      });
    DOMPurify.sanitize(root, {
      IN_PLACE: true,
      ALLOWED_TAGS: hook ? ["div", "footer", "#text"] : ["div", "#text"],
    });
    document.body.append(root);
    await new Promise((resolve) => setTimeout(resolve, 120));
    const details = {
      html: root.innerHTML,
      handler: img.getAttribute("onload"),
      fired: window.__localMarker,
      connected: img.isConnected,
    };
    assert(details.html === "<div>safe</div>" && !details.connected, "removed subtree escaped");
    assert(
      details.handler === null && details.fired === 0,
      "detached resource handler not neutralized",
    );
    return details;
  };
  for (const hook of ["beforeSanitizeElements", "uponSanitizeElement"]) {
    await check(`55q2-detach-${hook}`, () => detached(hook));
  }
  await check("6688-rawtext-return-reparse", () => {
    const parent = document.createElement("div");
    const root = document.createElement("style");
    root.textContent = '</style><img onerror="window.__localMarker++">';
    parent.append(root);
    let returned;
    try {
      returned = DOMPurify.sanitize(root, { IN_PLACE: true });
    } catch (error) {
      assert(
        error instanceof TypeError && /in.place|remov|root/i.test(error.message),
        "unexpected sanitizer exception",
      );
      return { failClosed: error.message };
    }
    const probe = document.createElement("div");
    probe.innerHTML = returned?.outerHTML || "";
    assert(!probe.querySelector("img[onerror]"), "returned rawtext reopens active markup");
    return { returned: returned?.outerHTML || "", removed: root.parentNode === null };
  });
  await check("ordinary-hook-removal-control", () => detached(null));
  await check("ordinary-arabic-html", () => {
    const input = '<p dir="rtl"><strong>فاتورة تجريبية</strong> <em>100</em></p>';
    const clean = DOMPurify.sanitize(input);
    assert(clean === input, "ordinary formatting changed");
    return { clean };
  });
  await check("ordinary-dangerous-attributes", () => {
    const clean = DOMPurify.sanitize(
      '<p onclick="window.__localMarker++">ok</p><a href="javascript:void(0)">link</a>',
    );
    assert(clean === "<p>ok</p><a>link</a>", "event or script URI survived");
    return { clean };
  });
  await check("ordinary-in-place-node", () => {
    const root = document.createElement("div");
    root.innerHTML = "<b>safe</b>";
    assert(
      DOMPurify.sanitize(root, { IN_PLACE: true }) === root && root.innerHTML === "<b>safe</b>",
      "ordinary in-place contract changed",
    );
    return { html: root.outerHTML };
  });
  await check("ordinary-rawtext-dom-output", () => {
    const root = document.createElement("style");
    root.textContent = '</style><img onerror="window.__localMarker++">';
    const fragment = DOMPurify.sanitize(root, { RETURN_DOM_FRAGMENT: true });
    assert(fragment.childNodes.length === 0, "non-in-place control not empty");
    return { children: fragment.childNodes.length };
  });
  return { version: DOMPurify.version, results };
};
