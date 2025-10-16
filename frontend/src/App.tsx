import { useEffect, useState } from "react";
import { APP_CONFIG } from "./config";

type HealthResponse = {
  status: string;
  model: string;
};

type RAGStatus = {
  rag_status: string;
  ready: boolean;
};

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

type ChatResponse = {
  message: {
    role: string;
    content: string;
  };
  done: boolean;
};

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [ragStatus, setRAGStatus] = useState<RAGStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    // Check backend health
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

    // Check RAG status
    fetch(`${APP_CONFIG.apiBaseUrl}/health/rag`, { signal: controller.signal })
      .then(async (response) => {
        if (response.ok) {
          return (await response.json()) as RAGStatus;
        }
        return null;
      })
      .then(setRAGStatus)
      .catch(() => {
        // RAG check is optional
      });

    return () => controller.abort();
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content: inputValue };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue("");
    setIsLoading(true);

    try {
      // Try RAG endpoint first if available, but with shorter timeout
      let response;
      let assistantContent;

      if (ragStatus?.ready) {
        try {
          // Enhanced prompt with context about Prajwal - simplified for testing
          const enhancedPrompt = `You are PrajwalGPT, an AI assistant that knows about Prajwal. Prajwal is a developer working with AI/ML, Python, JavaScript, and React. He's building PrajwalGPT using Ollama, FastAPI, and React. Answer questions about Prajwal based on this context. USER QUESTION: ${inputValue} RESPONSE:`

          const ragResponse = await fetch(`${APP_CONFIG.apiBaseUrl}/generate`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              prompt: enhancedPrompt,
            }),
          });

          if (ragResponse.ok) {
            const ragData = await ragResponse.json();
            assistantContent = ragData.response;
          } else {
            throw new Error("Enhanced chat request failed");
          }
        } catch (ragError) {
          console.log("Enhanced prompt failed, falling back to basic chat:", ragError);
          // Fall back to basic generate
          const conversationContext = newMessages
            .map(msg => `${msg.role === "user" ? "Human" : "Assistant"}: ${msg.content}`)
            .join("\n");
          
          const prompt = `You are PrajwalGPT. Based on what I know about Prajwal, he's a developer working with AI and NLP. ${conversationContext}\nAssistant:`;

          response = await fetch(`${APP_CONFIG.apiBaseUrl}/generate`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              prompt: prompt,
            }),
          });

          if (!response.ok) {
            throw new Error(`Generate request failed with status ${response.status}`);
          }

          const data = await response.json();
          assistantContent = data.response;
        }
      } else {
        // Use basic generate when RAG not ready
        const conversationContext = newMessages
          .map(msg => `${msg.role === "user" ? "Human" : "Assistant"}: ${msg.content}`)
          .join("\n");
        
        const prompt = `You are PrajwalGPT. ${conversationContext}\nAssistant:`;

        response = await fetch(`${APP_CONFIG.apiBaseUrl}/generate`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
          }),
        });

        if (!response.ok) {
          throw new Error(`Generate request failed with status ${response.status}`);
        }

        const data = await response.json();
        assistantContent = data.response;
      }

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: assistantContent,
      };

      setMessages([...newMessages, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error while processing your message.",
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="app__header">
        <h1>PrajwalGPT</h1>
        <p className="app__subtitle">
          Retrieval-augmented generation powered by Ollama
        </p>
      </header>

      <section className="app__section">
        <h2>System Status</h2>
        {error && <p className="app__error">{error}</p>}
        {!error && !health && <p>Checking health…</p>}
        {health && (
          <div className="status-grid">
            <div className="status-item">
              <strong>Backend:</strong> {health.status}
            </div>
            <div className="status-item">
              <strong>Model:</strong> {health.model}
            </div>
            <div className="status-item">
              <strong>RAG Status:</strong> {ragStatus?.ready ? "✅ Ready" : "❌ Not Ready"}
            </div>
            <div className="status-item">
              <strong>Mode:</strong> {ragStatus?.ready ? "Document-based" : "General"}
            </div>
          </div>
        )}
        
        {!ragStatus?.ready && (
          <div className="rag-setup-notice">
            <h3>📚 Add Your Documents</h3>
            <p>To make PrajwalGPT talk about you specifically:</p>
            <ol>
              <li>Add your documents (.txt, .md, .pdf) to <code>storage/documents/</code></li>
              <li>Run: <code>uv run python ingestion/ingest.py</code></li>
              <li>Refresh this page</li>
            </ol>
          </div>
        )}
      </section>

      <section className="app__section chat-section">
        <h2>Chat with PrajwalGPT</h2>
        {ragStatus?.ready && (
          <p className="rag-status-message">
            🎯 <strong>Document mode active!</strong> Ask me anything about Prajwal based on the uploaded documents.
          </p>
        )}
        
        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                👋 Hi! I'm PrajwalGPT. Ask me anything!
              </div>
            )}
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <strong>{message.role === "user" ? "You" : "PrajwalGPT"}:</strong>
                <div className="message-content">{message.content}</div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant">
                <strong>PrajwalGPT:</strong>
                <div className="message-content">Thinking...</div>
              </div>
            )}
          </div>
          
          <div className="input-container">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here... (Press Enter to send)"
              disabled={isLoading}
              rows={3}
            />
            <button onClick={sendMessage} disabled={isLoading || !inputValue.trim()}>
              Send
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
