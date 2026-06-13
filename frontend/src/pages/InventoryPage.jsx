import React, { useEffect, useState } from "react";
import { AlertTriangle, History, Save } from "lucide-react";

import { api } from "../api/client";

export function InventoryPage() {
  const [products, setProducts] = useState([]);
  const [stock, setStock] = useState([]);
  const [movements, setMovements] = useState([]);
  const [stockForm, setStockForm] = useState({ product_id: "", current_stock: "", low_stock_threshold: 5 });
  const [movementForm, setMovementForm] = useState({ product_id: "", movement_type: "purchase", quantity: "", note: "" });
  const [error, setError] = useState("");

  async function load() {
    const [productRows, stockRows, movementRows] = await Promise.all([api.products(), api.stock(), api.movements()]);
    setProducts(productRows);
    setStock(stockRows);
    setMovements(movementRows);
  }

  useEffect(() => { load().catch(console.error); }, []);

  async function saveStock(event) {
    event.preventDefault();
    setError("");
    try {
      await api.upsertStock({
        product_id: Number(stockForm.product_id),
        current_stock: Number(stockForm.current_stock),
        low_stock_threshold: Number(stockForm.low_stock_threshold),
      });
      setStockForm({ product_id: "", current_stock: "", low_stock_threshold: 5 });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function saveMovement(event) {
    event.preventDefault();
    setError("");
    try {
      await api.createMovement({
        product_id: Number(movementForm.product_id),
        movement_type: movementForm.movement_type,
        quantity: Number(movementForm.quantity),
        note: movementForm.note || null,
      });
      setMovementForm({ product_id: "", movement_type: "purchase", quantity: "", note: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Inventory Management</h1><p>Track current stock, low stock alerts, and movement history.</p></div></header>
      <section className="split">
        <form className="panel" onSubmit={saveStock}>
          <h2><Save size={19} /> Stock setup</h2>
          <label>Product<select value={stockForm.product_id} onChange={(e) => setStockForm({ ...stockForm, product_id: e.target.value })} required><option value="">Select product</option>{products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
          <label>Current stock<input type="number" min="0" value={stockForm.current_stock} onChange={(e) => setStockForm({ ...stockForm, current_stock: e.target.value })} required /></label>
          <label>Low stock threshold<input type="number" min="0" value={stockForm.low_stock_threshold} onChange={(e) => setStockForm({ ...stockForm, low_stock_threshold: e.target.value })} required /></label>
          <button className="primary"><Save size={17} /> Save stock</button>
        </form>
        <form className="panel" onSubmit={saveMovement}>
          <h2><History size={19} /> Stock movement</h2>
          <label>Product<select value={movementForm.product_id} onChange={(e) => setMovementForm({ ...movementForm, product_id: e.target.value })} required><option value="">Select product</option>{products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
          <label>Movement<select value={movementForm.movement_type} onChange={(e) => setMovementForm({ ...movementForm, movement_type: e.target.value })}><option value="purchase">Purchase</option><option value="sale">Sale</option><option value="adjustment">Adjustment out</option><option value="production_in">Production in</option><option value="wastage">Wastage</option></select></label>
          <label>Quantity<input type="number" min="1" value={movementForm.quantity} onChange={(e) => setMovementForm({ ...movementForm, quantity: e.target.value })} required /></label>
          <label>Note<input value={movementForm.note} onChange={(e) => setMovementForm({ ...movementForm, note: e.target.value })} /></label>
          {error && <p className="error">{error}</p>}
          <button className="primary"><Save size={17} /> Record movement</button>
        </form>
      </section>
      <section className="tableWrap">
        <h2><AlertTriangle size={19} /> Current stock</h2>
        <table>
          <thead><tr><th>Product</th><th>Current</th><th>Low alert</th><th>Status</th></tr></thead>
          <tbody>{stock.map((row) => <tr key={row.id}><td>{row.product.name}</td><td>{row.current_stock}</td><td>{row.low_stock_threshold}</td><td><span className={row.current_stock <= row.low_stock_threshold ? "status low" : "status ok"}>{row.current_stock <= row.low_stock_threshold ? "Low" : "OK"}</span></td></tr>)}</tbody>
        </table>
      </section>
      <section className="tableWrap">
        <h2>Movement history</h2>
        <table>
          <thead><tr><th>Date</th><th>Product</th><th>Type</th><th>Qty</th><th>Note</th></tr></thead>
          <tbody>{movements.map((row) => <tr key={row.id}><td>{new Date(row.created_at).toLocaleString()}</td><td>{row.product.name}</td><td>{row.movement_type}</td><td>{row.quantity}</td><td>{row.note || ""}</td></tr>)}</tbody>
        </table>
      </section>
    </>
  );
}

