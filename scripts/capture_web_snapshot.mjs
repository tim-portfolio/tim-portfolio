#!/usr/bin/env node
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

const chromeCandidates = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
];

const [, , inputUrl, outputPng, ...flags] = process.argv;
const langFlag = flags.find((flag) => flag.startsWith("--lang="));
const snapshotLanguage = langFlag ? langFlag.split("=")[1] : "zh";

if (!inputUrl || !outputPng || !["en", "zh"].includes(snapshotLanguage)) {
  console.error("Usage: node scripts/capture_web_snapshot.mjs <url> <output.png> [--lang=en|zh]");
  process.exit(2);
}

const exists = async (path) => {
  try {
    await import("node:fs/promises").then((fs) => fs.access(path));
    return true;
  } catch {
    return false;
  }
};

const chromePath = (await Promise.all(chromeCandidates.map(async (path) => ((await exists(path)) ? path : null))))
  .find(Boolean);

if (!chromePath) {
  console.error("Chrome, Edge, or Chromium was not found.");
  process.exit(1);
}

const port = 41000 + Math.floor(Math.random() * 10000);
const userDataDir = join(tmpdir(), `portfolio-snapshot-${Date.now()}`);
await mkdir(userDataDir, { recursive: true });

const chrome = spawn(chromePath, [
  "--headless=new",
  "--disable-gpu",
  "--disable-extensions",
  "--disable-component-extensions-with-background-pages",
  "--disable-background-networking",
  "--hide-scrollbars",
  "--no-first-run",
  "--no-default-browser-check",
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${userDataDir}`,
  "about:blank",
], {
  stdio: "ignore",
});

const cleanup = async () => {
  try {
    chrome.kill("SIGTERM");
  } catch {
    // ignore cleanup failures
  }
  await delay(400);
  for (let i = 0; i < 5; i += 1) {
    try {
      await rm(userDataDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 });
      return;
    } catch {
      await delay(250);
    }
  }
};

process.on("exit", () => {
  try {
    chrome.kill("SIGTERM");
  } catch {
    // ignore cleanup failures
  }
});

const fetchJson = async (url, options) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${url}`);
  }
  return response.json();
};

const waitForChrome = async () => {
  const versionUrl = `http://127.0.0.1:${port}/json/version`;
  for (let i = 0; i < 80; i += 1) {
    try {
      return await fetchJson(versionUrl);
    } catch {
      await delay(100);
    }
  }
  throw new Error("Timed out waiting for Chrome DevTools.");
};

const connectCdp = async (webSocketUrl) => new Promise((resolve, reject) => {
  const ws = new WebSocket(webSocketUrl);
  const pending = new Map();
  const listeners = new Map();
  let id = 0;

  ws.addEventListener("open", () => {
    const send = (method, params = {}) => new Promise((res, rej) => {
      id += 1;
      pending.set(id, { res, rej });
      ws.send(JSON.stringify({ id, method, params }));
    });

    const waitEvent = (method, timeoutMs = 15000) => new Promise((res, rej) => {
      const timer = setTimeout(() => {
        const list = listeners.get(method) || [];
        listeners.set(method, list.filter((item) => item.res !== res));
        rej(new Error(`Timed out waiting for ${method}`));
      }, timeoutMs);
      const list = listeners.get(method) || [];
      list.push({ res, timer });
      listeners.set(method, list);
    });

    resolve({ send, waitEvent, close: () => ws.close() });
  });

  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { res, rej } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) {
        rej(new Error(message.error.message || JSON.stringify(message.error)));
      } else {
        res(message.result);
      }
      return;
    }
    if (message.method && listeners.has(message.method)) {
      const list = listeners.get(message.method);
      const item = list.shift();
      if (item) {
        clearTimeout(item.timer);
        item.res(message.params || {});
      }
    }
  });

  ws.addEventListener("error", reject);
});

try {
  await waitForChrome();
  const target = await fetchJson(
    `http://127.0.0.1:${port}/json/new?${encodeURIComponent("about:blank")}`,
    { method: "PUT" }
  );
  const cdp = await connectCdp(target.webSocketDebuggerUrl);

  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 1200,
    deviceScaleFactor: 1,
    mobile: false,
  });

  const loaded = cdp.waitEvent("Page.loadEventFired", 20000);
  await cdp.send("Page.navigate", { url: inputUrl });
  try {
    await loaded;
  } catch {
    await delay(1500);
  }

  await cdp.send("Runtime.evaluate", {
    expression: `
      (() => {
        const button = document.querySelector('[data-lang-toggle]');
        const language = ${JSON.stringify(snapshotLanguage)};
        if (!button) return;
        const label = button.textContent.trim();
        if (language === 'zh' && label === '中文') button.click();
        if (language === 'en' && label === 'EN') button.click();
      })();
    `,
  });

  await delay(2500);
  await cdp.send("Runtime.evaluate", {
    awaitPromise: true,
    expression: `
      Promise.race([
        Promise.all(Array.from(document.images).map((img) => img.complete ? true : new Promise((resolve) => {
          img.addEventListener('load', resolve, { once: true });
          img.addEventListener('error', resolve, { once: true });
        }))),
        new Promise((resolve) => setTimeout(resolve, 5000))
      ])
    `,
  });

  await cdp.send("Runtime.evaluate", {
    expression: `
      (() => {
        document.body.classList.remove('motion-ready');
        const style = document.createElement('style');
        style.textContent = [
          '* { animation: none !important; transition: none !important; }',
          '.reveal, .reveal-item { opacity: 1 !important; transform: none !important; filter: none !important; }',
          '.site-nav { position: static !important; }'
        ].join('\\n');
        document.head.appendChild(style);
        window.scrollTo(0, 0);
      })();
    `,
  });

  await delay(300);
  const metrics = await cdp.send("Page.getLayoutMetrics");
  const width = Math.ceil(metrics.contentSize.width);
  const height = Math.ceil(metrics.contentSize.height);
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width,
    height: Math.min(height, 20000),
    deviceScaleFactor: 1,
    mobile: false,
  });
  const screenshot = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: true,
    clip: {
      x: 0,
      y: 0,
      width,
      height,
      scale: 1,
    },
  });

  await writeFile(outputPng, Buffer.from(screenshot.data, "base64"));
  cdp.close();
  await cleanup();
} catch (error) {
  await cleanup();
  console.error(error.stack || error.message);
  process.exit(1);
}
