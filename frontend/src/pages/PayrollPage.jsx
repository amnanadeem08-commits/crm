import React, { useEffect, useState } from "react";
import { Save } from "lucide-react";

import { api } from "../api/client";

export function PayrollPage() {
  const now = new Date();
  const [employees, setEmployees] = useState([]);
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({ employee_id: "", payroll_month: now.getMonth() + 1, payroll_year: now.getFullYear(), advances: 0, deductions: 0, note: "" });

  async function load() {
    const [employeeRows, payrollRows] = await Promise.all([api.employees(), api.payroll()]);
    setEmployees(employeeRows);
    setRows(payrollRows);
  }
  useEffect(() => { load().catch(console.error); }, []);

  async function submit(event) {
    event.preventDefault();
    await api.createPayroll({ ...form, employee_id: Number(form.employee_id), payroll_month: Number(form.payroll_month), payroll_year: Number(form.payroll_year), advances: Number(form.advances), deductions: Number(form.deductions) });
    setForm({ ...form, employee_id: "", advances: 0, deductions: 0, note: "" });
    await load();
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Payroll Management</h1><p>Salary, advances, deductions, and net salary.</p></div></header>
      <section className="split"><form className="panel" onSubmit={submit}>
        <h2><Save size={19} /> Calculate payroll</h2>
        <label>Employee<select value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} required><option value="">Select employee</option>{employees.map((row) => <option key={row.id} value={row.id}>{row.full_name}</option>)}</select></label>
        <label>Month<input type="number" min="1" max="12" value={form.payroll_month} onChange={(e) => setForm({ ...form, payroll_month: e.target.value })} /></label>
        <label>Year<input type="number" value={form.payroll_year} onChange={(e) => setForm({ ...form, payroll_year: e.target.value })} /></label>
        <label>Advances<input type="number" min="0" value={form.advances} onChange={(e) => setForm({ ...form, advances: e.target.value })} /></label>
        <label>Deductions<input type="number" min="0" value={form.deductions} onChange={(e) => setForm({ ...form, deductions: e.target.value })} /></label>
        <button className="primary"><Save size={17} /> Save payroll</button>
      </form></section>
      <section className="tableWrap"><table><thead><tr><th>Employee</th><th>Month</th><th>Base</th><th>Advances</th><th>Deductions</th><th>Net</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}><td>{row.employee.full_name}</td><td>{row.payroll_month}/{row.payroll_year}</td><td>{row.base_salary}</td><td>{row.advances}</td><td>{row.deductions}</td><td>{row.net_salary}</td></tr>)}</tbody></table></section>
    </>
  );
}
