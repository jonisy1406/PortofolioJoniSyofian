(async function () {
  const state = document.getElementById("analysisState");
  const rootPrefix = document.body.dataset.rootPrefix || "";
  const pythonFiles = [
    "scripts/__init__.py",
    "scripts/formatter.py",
    "scripts/optimizer.py",
    "scripts/dom_app.py",
  ];

  function setState(value) {
    if (state) state.textContent = window.sqlI18n ? window.sqlI18n.t(value) : value;
  }

  try {
    const pyodide = await loadPyodide();
    window.pyodide = pyodide;
    pyodide.FS.mkdirTree("scripts");

    for (const path of pythonFiles) {
      const response = await fetch(`${rootPrefix}${path}`);
      if (!response.ok) throw new Error(`${path} tidak ditemukan`);
      pyodide.FS.writeFile(path, await response.text());
    }

    const response = await fetch(`${rootPrefix}app.py`);
    if (!response.ok) throw new Error("app.py tidak ditemukan");

    await pyodide.runPythonAsync(await response.text());
    window.pythonSqlAppReady = true;

    if (state) {
      setState("state.pythonReady");
    }
  } catch (error) {
    console.error(error);
    setState("state.fallbackActive");
  }
})();
