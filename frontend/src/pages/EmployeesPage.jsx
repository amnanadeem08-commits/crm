import React, { useEffect, useState } from "react";
import { Save } from "lucide-react";

import { api } from "../api/client";

export function EmployeesPage() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({ full_name: "", phone: "", role: "", monthly_salary: "" });

  async function load() { setRows(await api.employees()); }
  useEffect(() => { load().catch(console.error); }, []);

  async function submit(event) {
    event.preventDefault();
    await api.createEmployee({ ...form, monthly_salary: Number(form.monthly_salary || 0), is_active: true });
    setForm({ full_name: "", phone: "", role: "", monthly_salary: "" });
    await load();
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Employee Management</h1><p>Employee profiles, roles, and salary records.</p></div></header>
      <section className="split">
        <form className="panel" onSubmit={submit}>
          <h2><Save size={19} /> Add employee</h2>
          <label>Name<input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /></label>
          <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} required /></label>
          <label>Role<input value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} required /></label>
          <label>Monthly salary<input type="number" min="0" value={form.monthly_salary} onChange={(e) => setForm({ ...form, monthly_salary: e.target.value })} /></label>
          <button className="primary"><Save size={17} /> Save employee</button>
        </form>
      </section>
      <section className="tableWrap"><table><thead><tr><th>Name</th><th>Phone</th><th>Role</th><th>Salary</th><th>Status</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}><td>{row.full_name}</td><td>{row.phone}</td><td>{row.role}</td><td>{row.monthly_salary}</td><td>{row.is_active ? "Active" : "Inactive"}</td></tr>)}</tbody></table></section>
    </>
  );
}

