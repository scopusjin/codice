/* The archive stays in this browser. Only an explicitly opened case is sent to Streamlit. */
(function(root) {
  'use strict';
  const MAX_BYTES = 1024 * 1024;

  function makeRecord(raw, id, now = new Date()) {
    if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > MAX_BYTES) {
      throw new Error('Il caso supera la dimensione massima di 1 MB.');
    }
    const data = JSON.parse(raw);
    if (data.format !== 'mortem-case' || data.schema_version !== 1 ||
        typeof data.case_code !== 'string' || !['full', 'msil'].includes(data.view)) {
      throw new Error('Caso non valido. Nessun salvataggio è stato modificato.');
    }
    data.saved_at = now.toISOString();
    const code = data.case_code.trim();
    return {id: code ? 'code:' + code : 'draft:' + id, code, view: data.view,
      savedAt: data.saved_at, appVersion: data.app_version, data: JSON.stringify(data)};
  }

  function label(record) {
    const date = new Date(record.savedAt);
    const stamp = Number.isNaN(date.getTime()) ? '' : date.toLocaleString('it-CH',
      {day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit', second:'2-digit'});
    return `${record.code || 'Senza sigla'} · ${record.view === 'msil' ? 'Sopralluogo' : 'Completa'} · ${stamp}`;
  }

  function openDatabase(factory) {
    return new Promise((resolve, reject) => {
      if (!factory) { reject(new Error('Archivio del browser non disponibile. Usa Scarica file.')); return; }
      const request = factory.open('mortem-cases', 1);
      request.onupgradeneeded = () => request.result.createObjectStore('cases', {keyPath:'id'});
      request.onerror = () => reject(request.error);
      request.onblocked = () => reject(new Error('Chiudi le altre schede di Mor-tem e riprova.'));
      request.onsuccess = () => resolve(request.result);
    });
  }

  async function transaction(factory, mode, operation) {
    const db = await openDatabase(factory);
    try {
      return await new Promise((resolve, reject) => {
        const tx = db.transaction('cases', mode);
        let result;
        tx.oncomplete = () => resolve(result);
        tx.onabort = () => reject(tx.error || new Error('Salvataggio interrotto. Riprova.'));
        tx.onerror = () => reject(tx.error);
        operation(tx.objectStore('cases'), value => { result = value; });
      });
    } finally { db.close(); }
  }

  function createStore(factory) {
    return {
      list: () => transaction(factory, 'readonly', (store, done) => {
        const request = store.getAll();
        request.onsuccess = () => done(request.result.sort((a,b) => b.savedAt.localeCompare(a.savedAt)));
      }),
      // Compare within the write transaction: another tab cannot silently overwrite a newer save.
      save: (record, expected = null) => transaction(factory, 'readwrite', (store, done) => {
        const request = store.get(record.id);
        request.onsuccess = () => {
          if (request.result && request.result.data !== expected) {
            done(false);
          } else { store.put(record); done(true); }
        };
      }),
      read: id => transaction(factory, 'readonly', (store, done) => {
        const request = store.get(id);
        request.onsuccess = () => done(request.result || null);
      })
    };
  }
  const api = {makeRecord, label, createStore};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MortemCaseStore = api;
})(typeof window === 'object' ? window : globalThis);
