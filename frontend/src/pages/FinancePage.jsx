import React, { useEffect, useState } from "react";
import { Save } from "lucide-react";

import { api } from "../api/client";

export function FinancePage() {
  const today = new Date().toISOString().slice(0, 10);
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [form, setForm] = useState({ expense_date: today, category: "", amount: "", note: "" });

  async function load() {
    const [expenseRows, profitLoss] = await Promise.all([api.expenses(), api.profitLoss()]);
    setExpenses(expenseRows);
    setSummary(profitLoss);
  }
  useEffect(() => { load().catch(console.error); }, []);

  async function submit(event) {
    event.preventDefault();
    await api.createExpense({ ...form, amount: Number(form.amount) });
    setForm({ expense_date: today, category: "", amount: "", note: "" });
    await load();
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Profit & Loss</h1><p>Revenue, expenses, payroll cost, and profit status.</p></div></header>
      {summary && <section className="metrics"><article><span>Revenue</span><strong>{summary.total_revenue}</strong></article><article><span>Expenses</span><strong>{summary.expenses}</strong></article><article><span>{summary.status}</span><strong>{summary.net_profit}</strong></article></section>}
      <section className="split"><form className="panel" onSubmit={submit}>
        <h2><Save size={19} /> Add expense</h2>
        <label>Date<input type="date" value={form.expense_date} onChange={(e) => setForm({ ...form, expense_date: e.target.value })} required /></label>
        <label>Category<input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required /></label>
        <label>Amount<input type="number" min="0.01" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></label>
        <label>Note<input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} /></label>
        <button className="primary"><Save size={17} /> Save expense</button>
      </form></section>
      <section className="tableWrap"><table><thead><tr><th>Date</th><th>Category</th><th>Amount</th><th>Note</th></tr></thead><tbody>{expenses.map((row) => <tr key={row.id}><td>{row.expense_date}</td><td>{row.category}</td><td>{row.amount}</td><td>{row.note}</td></tr>)}</tbody></table></section>
    </>
  );
}

