import React, { useEffect, useState } from "react";
import { Save } from "lucide-react";

import { api } from "../api/client";

export function SalesPage() {
  const [products, setProducts] = useState([]);
  const [sales, setSales] = useState([]);
  const [report, setReport] = useState(null);
  const [form, setForm] = useState({ customer_name: "Walk-in Customer", product_id: "", quantity: "", unit_price: "" });
  const [error, setError] = useState("");

  async function load() {
    const [productRows, saleRows, daily] = await Promise.all([api.products(), api.sales(), api.salesReport("daily")]);
    setProducts(productRows);
    setSales(saleRows);
    setReport(daily);
  }
  useEffect(() => { load().catch(console.error); }, []);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await api.createSale({ customer_name: form.customer_name, items: [{ product_id: Number(form.product_id), quantity: Number(form.quantity), unit_price: Number(form.unit_price) }] });
      setForm({ customer_name: "Walk-in Customer", product_id: "", quantity: "", unit_price: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Sales Management</h1><p>Record sales, reports, and customer transactions.</p></div></header>
      {report && <section className="metrics"><article><span>Daily sales</span><strong>{report.total_sales}</strong></article><article><span>Daily revenue</span><strong>{report.total_revenue}</strong></article><article><span>Gross profit</span><strong>{report.gross_profit}</strong></article></section>}
      <section className="split"><form className="panel" onSubmit={submit}>
        <h2><Save size={19} /> Record sale</h2>
        <label>Customer<input value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} required /></label>
        <label>Product<select value={form.product_id} onChange={(e) => setForm({ ...form, product_id: e.target.value })} required><option value="">Select product</option>{products.map((row) => <option key={row.id} value={row.id}>{row.name}</option>)}</select></label>
        <label>Quantity<input type="number" min="1" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} required /></label>
        <label>Unit price<input type="number" min="0" step="0.01" value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} required /></label>
        {error && <p className="error">{error}</p>}
        <button className="primary"><Save size={17} /> Save sale</button>
      </form></section>
      <section className="tableWrap"><table><thead><tr><th>Date</th><th>Customer</th><th>Revenue</th><th>Cost</th><th>Items</th></tr></thead><tbody>{sales.map((row) => <tr key={row.id}><td>{new Date(row.created_at).toLocaleString()}</td><td>{row.customer_name}</td><td>{row.total_revenue}</td><td>{row.total_cost}</td><td>{row.items.map((item) => `${item.product.name} x ${item.quantity}`).join(", ")}</td></tr>)}</tbody></table></section>
    </>
  );
}

