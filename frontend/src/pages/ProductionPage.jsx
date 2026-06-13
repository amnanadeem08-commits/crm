import React, { useEffect, useState } from "react";
import { Plus, Save } from "lucide-react";

import { api } from "../api/client";

export function ProductionPage() {
  const today = new Date().toISOString().slice(0, 10);
  const [products, setProducts] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [batches, setBatches] = useState([]);
  const [materialForm, setMaterialForm] = useState({ name: "", unit: "kg", current_stock: 0, low_stock_threshold: 0 });
  const [batchForm, setBatchForm] = useState({ batch_date: today, finished_product_id: "", quantity_produced: "", raw_material_cost: 0, wastage_quantity: 0, note: "" });
  const [error, setError] = useState("");

  async function load() {
    const [productRows, materialRows, batchRows] = await Promise.all([api.products(), api.rawMaterials(), api.productionBatches()]);
    setProducts(productRows);
    setMaterials(materialRows);
    setBatches(batchRows);
  }
  useEffect(() => { load().catch(console.error); }, []);

  async function saveMaterial(event) {
    event.preventDefault();
    await api.createRawMaterial({ ...materialForm, current_stock: Number(materialForm.current_stock), low_stock_threshold: Number(materialForm.low_stock_threshold) });
    setMaterialForm({ name: "", unit: "kg", current_stock: 0, low_stock_threshold: 0 });
    await load();
  }

  async function saveBatch(event) {
    event.preventDefault();
    setError("");
    try {
      await api.createProductionBatch({
        ...batchForm,
        finished_product_id: Number(batchForm.finished_product_id),
        quantity_produced: Number(batchForm.quantity_produced),
        raw_material_cost: Number(batchForm.raw_material_cost),
        wastage_quantity: Number(batchForm.wastage_quantity),
      });
      setBatchForm({ batch_date: today, finished_product_id: "", quantity_produced: "", raw_material_cost: 0, wastage_quantity: 0, note: "" });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Production Management</h1><p>Raw materials, production batches, finished goods, and wastage.</p></div></header>
      <section className="split">
        <form className="panel" onSubmit={saveMaterial}>
          <h2><Plus size={19} /> Raw material</h2>
          <label>Name<input value={materialForm.name} onChange={(e) => setMaterialForm({ ...materialForm, name: e.target.value })} required /></label>
          <label>Unit<input value={materialForm.unit} onChange={(e) => setMaterialForm({ ...materialForm, unit: e.target.value })} required /></label>
          <label>Current stock<input type="number" min="0" value={materialForm.current_stock} onChange={(e) => setMaterialForm({ ...materialForm, current_stock: e.target.value })} /></label>
          <label>Low threshold<input type="number" min="0" value={materialForm.low_stock_threshold} onChange={(e) => setMaterialForm({ ...materialForm, low_stock_threshold: e.target.value })} /></label>
          <button className="primary"><Save size={17} /> Save material</button>
        </form>
        <form className="panel" onSubmit={saveBatch}>
          <h2><Save size={19} /> Production batch</h2>
          <label>Date<input type="date" value={batchForm.batch_date} onChange={(e) => setBatchForm({ ...batchForm, batch_date: e.target.value })} required /></label>
          <label>Finished product<select value={batchForm.finished_product_id} onChange={(e) => setBatchForm({ ...batchForm, finished_product_id: e.target.value })} required><option value="">Select product</option>{products.map((row) => <option key={row.id} value={row.id}>{row.name}</option>)}</select></label>
          <label>Quantity produced<input type="number" min="1" value={batchForm.quantity_produced} onChange={(e) => setBatchForm({ ...batchForm, quantity_produced: e.target.value })} required /></label>
          <label>Raw material cost<input type="number" min="0" value={batchForm.raw_material_cost} onChange={(e) => setBatchForm({ ...batchForm, raw_material_cost: e.target.value })} /></label>
          <label>Wastage quantity<input type="number" min="0" value={batchForm.wastage_quantity} onChange={(e) => setBatchForm({ ...batchForm, wastage_quantity: e.target.value })} /></label>
          {error && <p className="error">{error}</p>}
          <button className="primary"><Save size={17} /> Save batch</button>
        </form>
      </section>
      <section className="tableWrap"><h2>Raw materials</h2><table><thead><tr><th>Name</th><th>Unit</th><th>Stock</th><th>Low alert</th></tr></thead><tbody>{materials.map((row) => <tr key={row.id}><td>{row.name}</td><td>{row.unit}</td><td>{row.current_stock}</td><td>{row.low_stock_threshold}</td></tr>)}</tbody></table></section>
      <section className="tableWrap"><h2>Production batches</h2><table><thead><tr><th>Date</th><th>Product</th><th>Produced</th><th>Wastage</th><th>Cost</th></tr></thead><tbody>{batches.map((row) => <tr key={row.id}><td>{row.batch_date}</td><td>{row.finished_product.name}</td><td>{row.quantity_produced}</td><td>{row.wastage_quantity}</td><td>{row.raw_material_cost}</td></tr>)}</tbody></table></section>
    </>
  );
}
