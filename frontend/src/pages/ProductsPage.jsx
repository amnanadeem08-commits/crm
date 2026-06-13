import React, { useEffect, useState } from "react";
import { Plus, Save, Trash2 } from "lucide-react";

import { api } from "../api/client";

const emptyProduct = { name: "", sku: "", cost_price: "", selling_price: "", category_id: "", is_active: true };

export function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [product, setProduct] = useState(emptyProduct);
  const [categoryName, setCategoryName] = useState("");
  const [error, setError] = useState("");

  async function load() {
    const [productRows, categoryRows] = await Promise.all([api.products(), api.categories()]);
    setProducts(productRows);
    setCategories(categoryRows);
  }

  useEffect(() => { load().catch(console.error); }, []);

  async function createCategory(event) {
    event.preventDefault();
    if (!categoryName.trim()) return;
    await api.createCategory({ name: categoryName });
    setCategoryName("");
    await load();
  }

  async function saveProduct(event) {
    event.preventDefault();
    setError("");
    try {
      await api.createProduct({
        ...product,
        cost_price: Number(product.cost_price),
        selling_price: Number(product.selling_price),
        category_id: product.category_id ? Number(product.category_id) : null,
      });
      setProduct(emptyProduct);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function deleteProduct(id) {
    await api.deleteProduct(id);
    await load();
  }

  return (
    <>
      <header className="pageHeader"><div><h1>Product Management</h1><p>Add products, pricing, SKU, and categories.</p></div></header>
      <section className="split">
        <form className="panel" onSubmit={saveProduct}>
          <h2><Plus size={19} /> Add product</h2>
          <label>Name<input value={product.name} onChange={(e) => setProduct({ ...product, name: e.target.value })} required /></label>
          <label>SKU<input value={product.sku} onChange={(e) => setProduct({ ...product, sku: e.target.value })} required /></label>
          <label>Cost price<input type="number" min="0" step="0.01" value={product.cost_price} onChange={(e) => setProduct({ ...product, cost_price: e.target.value })} required /></label>
          <label>Selling price<input type="number" min="0" step="0.01" value={product.selling_price} onChange={(e) => setProduct({ ...product, selling_price: e.target.value })} required /></label>
          <label>Category<select value={product.category_id} onChange={(e) => setProduct({ ...product, category_id: e.target.value })}><option value="">No category</option>{categories.map((cat) => <option key={cat.id} value={cat.id}>{cat.name}</option>)}</select></label>
          {error && <p className="error">{error}</p>}
          <button className="primary"><Save size={17} /> Save product</button>
        </form>
        <form className="panel compact" onSubmit={createCategory}>
          <h2>Categories</h2>
          <div className="inlineForm"><input placeholder="Category name" value={categoryName} onChange={(e) => setCategoryName(e.target.value)} /><button className="secondary"><Plus size={17} /></button></div>
          <div className="tagList">{categories.map((cat) => <span key={cat.id}>{cat.name}</span>)}</div>
        </form>
      </section>
      <section className="tableWrap">
        <table>
          <thead><tr><th>Product</th><th>SKU</th><th>Category</th><th>Cost</th><th>Selling</th><th></th></tr></thead>
          <tbody>
            {products.map((row) => (
              <tr key={row.id}>
                <td>{row.name}</td><td>{row.sku}</td><td>{row.category?.name || "None"}</td><td>{row.cost_price}</td><td>{row.selling_price}</td>
                <td><button className="iconButton danger" title="Delete product" onClick={() => deleteProduct(row.id)}><Trash2 size={16} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}

