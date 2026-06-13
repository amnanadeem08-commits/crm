import React, { useEffect, useState } from "react";
import { AlertTriangle, Package, TrendingUp } from "lucide-react";

import { api } from "../api/client";

export function DashboardPage() {
  const [summary, setSummary] = useState({ products: 0, stock: 0, low: 0 });
  const [insight, setInsight] = useState(null);
  const [health, setHealth] = useState(null);
  const [brief, setBrief] = useState(null);

  useEffect(() => {
    async function load() {
      const [products, stock, low, ai, healthData, dailyBrief] = await Promise.all([
        api.products(),
        api.stock(),
        api.lowStock(),
        api.inventoryInsight(),
        api.businessHealth(),
        api.dailyBrief(),
      ]);
      setSummary({ products: products.length, stock: stock.length, low: low.length });
      setInsight(ai);
      setHealth(healthData);
      setBrief(dailyBrief);
    }
    load().catch(console.error);
  }, []);

  return (
    <>
      <header className="pageHeader">
        <div>
          <h1>Dashboard</h1>
          <p>Phase 1 operating view for products and inventory.</p>
        </div>
      </header>
      <section className="metrics">
        <article><Package size={22} /><span>Products</span><strong>{summary.products}</strong></article>
        <article><TrendingUp size={22} /><span>Stock records</span><strong>{summary.stock}</strong></article>
        <article><AlertTriangle size={22} /><span>Low stock</span><strong>{summary.low}</strong></article>
      </section>
      {insight && (
        <section className="insight">
          <h2>AI Business Guidance</h2>
          <dl>
            <dt>1. Problem Summary</dt><dd>{insight.problem_summary}</dd>
            <dt>2. Data Availability Check</dt><dd>{insight.data_availability_check}</dd>
            <dt>3. Key Issue</dt><dd>{insight.key_issue}</dd>
            <dt>4. Simple Insight</dt><dd>{insight.simple_insight}</dd>
            <dt>5. Recommended Action</dt><dd>{insight.recommended_action.join(" ")}</dd>
          </dl>
        </section>
      )}
      {health && (
        <section className="insight">
          <h2>Business Health Monitoring</h2>
          <dl>
            <dt>Sales Performance</dt><dd>{health.sales_performance}</dd>
            <dt>Profit Performance</dt><dd>{health.profit_performance}</dd>
            <dt>Inventory Health</dt><dd>{health.inventory_health}</dd>
            <dt>Production Efficiency</dt><dd>{health.production_efficiency}</dd>
            <dt>Employee Attendance</dt><dd>{health.employee_attendance}</dd>
            <dt>Payroll Costs</dt><dd>{health.payroll_costs}</dd>
          </dl>
          <div className="alertList">
            {health.exceptions.map((item) => (
              <article key={`${item.issue}-${item.reason}`}>
                <strong>{item.issue}</strong>
                <span>{item.reason}</span>
                <span>{item.business_impact}</span>
                <b>{item.recommended_action}</b>
              </article>
            ))}
          </div>
        </section>
      )}
      {brief && (
        <section className="insight">
          <h2>Daily Business Brief</h2>
          <dl>
            <dt>Business Summary</dt><dd>{brief.business_summary}</dd>
            <dt>Key Metrics</dt><dd>{brief.key_metrics.join(" ")}</dd>
            <dt>Important Alerts</dt><dd>{brief.important_alerts.join(" ")}</dd>
            <dt>Recommended Actions</dt><dd>{brief.recommended_actions.join(" ")}</dd>
          </dl>
        </section>
      )}
    </>
  );
}
