import React, { useContext, useState } from "react";
import { Boxes } from "lucide-react";

import { api } from "../api/client";
import { AuthContext } from "../auth/context";

export function LoginPage() {
  const { login } = useContext(AuthContext);
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "owner" });
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const payload = mode === "login"
        ? await api.login({ email: form.email, password: form.password })
        : await api.register(form);
      login(payload);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="authPage">
      <section className="authPanel">
        <div className="authBrand"><Boxes size={32} /><strong>Smart CRM</strong></div>
        <div className="segmented">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Sign in</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>
        <form onSubmit={submit}>
          {mode === "register" && (
            <label>Full name<input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /></label>
          )}
          <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
          <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8} /></label>
          {mode === "register" && (
            <label>Role<select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="owner">Owner</option><option value="manager">Manager</option><option value="staff">Staff</option></select></label>
          )}
          {error && <p className="error">{error}</p>}
          <button className="primary" type="submit">{mode === "login" ? "Sign in" : "Create account"}</button>
        </form>
      </section>
    </div>
  );
}

