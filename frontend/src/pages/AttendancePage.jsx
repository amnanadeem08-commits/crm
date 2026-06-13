import React, { useEffect, useState } from "react";
import { Save } from "lucide-react";

import { api } from "../api/client";

export function AttendancePage() {
  const today = new Date().toISOString().slice(0, 10);
  const [employees, setEmployees] = useState([]);
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState({ employee_id: "", work_date: today, status: "present", check_in: "", note: "" });

  async function load() {
    const [employeeRows, attendanceRows] = await Promise.all([api.employees(), api.attendance()]);
    setEmployees(employeeRows);
    setRows(attendanceRows);
  }
  useEffect(() => { load().catch(console.error); }, []);

  async function submit(event) {
    event.preventDefault();
    await api.createAttendance({ ...form, employee_id: Number(form.employee_id), check_in: form.check_in || null, note: form.note || null });
    setForm({ employee_id: "", work_date: today, status: "present", check_in: "", note: "" });
    await load();
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Attendance Management</h1><p>Daily attendance, late arrivals, and absences.</p></div></header>
      <section className="split"><form className="panel" onSubmit={submit}>
        <h2><Save size={19} /> Mark attendance</h2>
        <label>Employee<select value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} required><option value="">Select employee</option>{employees.map((row) => <option key={row.id} value={row.id}>{row.full_name}</option>)}</select></label>
        <label>Date<input type="date" value={form.work_date} onChange={(e) => setForm({ ...form, work_date: e.target.value })} required /></label>
        <label>Status<select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}><option value="present">Present</option><option value="late">Late</option><option value="absent">Absent</option></select></label>
        <label>Check in<input type="time" value={form.check_in} onChange={(e) => setForm({ ...form, check_in: e.target.value })} /></label>
        <label>Note<input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} /></label>
        <button className="primary"><Save size={17} /> Save attendance</button>
      </form></section>
      <section className="tableWrap"><table><thead><tr><th>Date</th><th>Employee</th><th>Status</th><th>Check in</th><th>Note</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}><td>{row.work_date}</td><td>{row.employee.full_name}</td><td>{row.status}</td><td>{row.check_in || ""}</td><td>{row.note || ""}</td></tr>)}</tbody></table></section>
    </>
  );
}

