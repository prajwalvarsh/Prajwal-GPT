import { useEffect, useState } from "react";
import { APP_CONFIG } from "./config";

type HealthResponse = {
  status: string;
  model: string;
};

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch(`${APP_CONFIG.apiBaseUrl}/health`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return (await response.json()) as HealthResponse;
      })
      .then(setHealth)
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      });

    return () => controller.abort();
  }, []);

  return (
    <div className="app">
      <header className="app__header">
        <h1>PrajwalGPT</h1>
        <p className="app__subtitle">
          Retrieval-augmented generation starter kit wired to the shared
          configuration module.
        </p>
      </header>

      <section className="app__section">
        <h2>Active Model</h2>
        <p>{APP_CONFIG.defaultModel}</p>
      </section>

      <section className="app__section">
        <h2>Backend status</h2>
        {error && <p className="app__error">{error}</p>}
        {!error && !health && <p>Checking health…</p>}
        {health && (
          <dl>
            <div className="app__stat">
              <dt>Status</dt>
              <dd>{health.status}</dd>
            </div>
            <div className="app__stat">
              <dt>Model</dt>
              <dd>{health.model}</dd>
            </div>
          </dl>
        )}
      </section>
    </div>
  );
}

export default App;
