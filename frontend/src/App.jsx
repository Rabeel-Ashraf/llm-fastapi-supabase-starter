import React, { useState } from "react";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_KEY);

function App() {
  const [view, setView] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleAuth(endpoint) {
    const res = await fetch(`http://localhost:8000/api/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (data.access_token) {
      setToken(data.access_token);
      localStorage.setItem("token", data.access_token);
      setView("chat");
    } else {
      alert("Auth failed");
    }
  }

  async function handleLLM() {
    setLoading(true);
    const res = await fetch("http://localhost:8000/api/llm", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt, model: "gpt-3.5-turbo" })
    });
    if (res.status === 429) {
      setResponse("Rate limit exceeded. Try again later.");
    } else {
      const data = await res.json();
      setResponse(data.response);
    }
    setLoading(false);
  }

  if (view === "login" || view === "signup") {
    return (
      <div style={{padding: 40}}>
        <h2>{view === "login" ? "Login" : "Sign Up"}</h2>
        <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} /><br />
        <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} /><br />
        <button onClick={()=>handleAuth(view)}>{view === "login" ? "Login" : "Sign Up"}</button>
        <button onClick={()=>setView(view === "login" ? "signup" : "login")}>
          {view === "login" ? "Need an account? Sign up" : "Already have an account? Login"}
        </button>
      </div>
    );
  }

  return (
    <div style={{margin: 40}}>
      <h2>LLM Chat UI</h2>
      <button onClick={() => {
        setToken("");
        localStorage.removeItem("token");
        setView("login");
      }}>Logout</button>
      <div>
        <textarea rows={4} style={{width: 400}} value={prompt} onChange={e=>setPrompt(e.target.value)} />
        <br />
        <button onClick={handleLLM} disabled={loading}>{loading ? "Sending..." : "Send"}</button>
      </div>
      <div style={{marginTop: 20}}>
        <b>Response:</b>
        <div>{response}</div>
      </div>
    </div>
  );
}

export default App;
