// Presentation only: option values, FC rules, drafts and event payloads stay unchanged.
(() => {
  let language = 'it', dictionary = {}, pattern = null, observer = null;
  const originals = new WeakMap();
  const attributes = new WeakMap();
  const escape = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  function tr(text) {
    if (language !== 'en' || !text) return text;
    if (Object.hasOwn(dictionary, text)) return dictionary[text];
    return pattern ? text.replace(pattern, (key, offset, source) => {
      if (offset && /[\p{L}\p{N}]/u.test(source[offset-1]) && /[\p{L}\p{N}]/u.test(key[0])) return key;
      if (offset+key.length < source.length && /[\p{L}\p{N}]/u.test(source[offset+key.length]) && /[\p{L}\p{N}]/u.test(key.at(-1))) return key;
      return dictionary[key];
    }) : text;
  }
  function update() {
    observer?.disconnect();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement?.closest('script,style,textarea,[data-no-translate]')) continue;
      const old = originals.get(node);
      const source = old && node.data === old.rendered ? old.source : node.data;
      const rendered = tr(source);
      if (node.data !== rendered) node.data = rendered;
      originals.set(node, {source, rendered});
    }
    for (const element of document.querySelectorAll('[aria-label],[title],[placeholder]')) {
      const saved = attributes.get(element) || {};
      for (const name of ['aria-label','title','placeholder']) {
        if (!element.hasAttribute(name)) continue;
        const current = element.getAttribute(name), old = saved[name];
        const source = old && current === old.rendered ? old.source : current;
        const rendered = tr(source);
        if (current !== rendered) element.setAttribute(name, rendered);
        saved[name] = {source, rendered};
      }
      attributes.set(element, saved);
    }
    document.documentElement.lang = language;
    observer?.observe(document.body, {subtree:true, childList:true, characterData:true,
      attributes:true, attributeFilter:['aria-label','title','placeholder']});
  }
  window.FCTranslation = {set(languageCode, texts) {
    language = languageCode === 'en' ? 'en' : 'it';
    dictionary = texts || {};
    pattern = new RegExp(Object.keys(dictionary).filter(key=>!['Data','Rigor'].includes(key)).sort((a,b)=>b.length-a.length).map(escape).join('|'), 'gu');
    observer ||= new MutationObserver(update);
    update();
  }, text:tr};
})();
