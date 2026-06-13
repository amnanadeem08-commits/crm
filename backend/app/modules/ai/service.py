from datetime import datetime, timedelta

from app.modules.ai.schemas import BusinessException, BusinessHealth, BusinessInsight, DailyBrief
from app.modules.inventory.models import InventoryStock, MovementType, StockMovement


class AiInsightService:
    def inventory_insight(self, stock_rows: list[InventoryStock]) -> BusinessInsight:
        if not stock_rows:
            return BusinessInsight(
                problem_summary="Inventory review cannot be completed.",
                data_availability_check="No inventory stock records are available.",
                key_issue="Current stock and low stock thresholds are missing.",
                simple_insight="The CRM cannot detect stock problems until products have stock records.",
                recommended_action=["Add stock quantity and low stock threshold for each active product."],
            )

        low_stock = [row for row in stock_rows if row.current_stock <= row.low_stock_threshold]
        if not low_stock:
            return BusinessInsight(
                problem_summary="Inventory stock looks stable.",
                data_availability_check=f"{len(stock_rows)} stock records were checked.",
                key_issue="No product is currently at or below its low stock threshold.",
                simple_insight="There is no immediate stock shortage visible in the available CRM data.",
                recommended_action=["Keep recording purchases, sales, and adjustments to maintain accurate stock."],
            )

        names = ", ".join(row.product.name for row in low_stock[:3])
        return BusinessInsight(
            problem_summary="Some products need stock attention.",
            data_availability_check=f"{len(stock_rows)} stock records were checked; {len(low_stock)} low stock item(s) found.",
            key_issue=f"Low stock detected for: {names}.",
            simple_insight="These products may run out soon if sales or production continue without restocking.",
            recommended_action=["Restock the low stock products.", "Review recent stock movements for these products."],
        )

    def business_health(self, stock_rows: list[InventoryStock], movements: list[StockMovement]) -> BusinessHealth:
        exceptions = self.detect_exceptions(stock_rows, movements)
        if not stock_rows:
            inventory_health = "Inventory cannot be monitored because stock records are missing."
        elif any(row.current_stock <= row.low_stock_threshold for row in stock_rows):
            inventory_health = "Inventory risk found from current stock records."
        else:
            inventory_health = "Inventory looks stable from available stock records."

        return BusinessHealth(
            sales_performance="Not available: sales module data has not been recorded yet.",
            profit_performance="Not available: revenue and expense data has not been recorded yet.",
            inventory_health=inventory_health,
            production_efficiency="Not available: production batch and wastage data has not been recorded yet.",
            employee_attendance="Not available: attendance records have not been recorded yet.",
            payroll_costs="Not available: payroll records have not been recorded yet.",
            exceptions=exceptions,
        )

    def detect_exceptions(self, stock_rows: list[InventoryStock], movements: list[StockMovement]) -> list[BusinessException]:
        exceptions: list[BusinessException] = []
        stock_by_product = {row.product_id: row for row in stock_rows}

        for stock in stock_rows:
            if stock.current_stock <= stock.low_stock_threshold:
                exceptions.append(
                    BusinessException(
                        issue=f"Low stock risk: {stock.product.name}",
                        reason=f"Current stock is {stock.current_stock}, threshold is {stock.low_stock_threshold}.",
                        business_impact="The shop may miss sales or delay production if this item runs out.",
                        recommended_action="Restock this product or raise a purchase request today.",
                    )
                )

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        outbound: dict[int, int] = {}
        recent_movements = [row for row in movements if row.created_at >= seven_days_ago]
        for movement in recent_movements:
            if movement.movement_type in {MovementType.sale, MovementType.adjustment, MovementType.wastage}:
                outbound[movement.product_id] = outbound.get(movement.product_id, 0) + movement.quantity

        for product_id, consumed_qty in outbound.items():
            stock = stock_by_product.get(product_id)
            if stock and consumed_qty > stock.low_stock_threshold and stock.current_stock <= stock.low_stock_threshold * 2:
                exceptions.append(
                    BusinessException(
                        issue=f"Rapid stock consumption: {stock.product.name}",
                        reason=f"{consumed_qty} units moved out in the last 7 days and only {stock.current_stock} remain.",
                        business_impact="This product may reach low stock faster than usual.",
                        recommended_action="Review recent sales or usage and restock before the next busy period.",
                    )
                )

        moved_product_ids = {row.product_id for row in movements}
        for stock in stock_rows:
            if stock.current_stock > stock.low_stock_threshold and stock.product_id not in moved_product_ids:
                exceptions.append(
                    BusinessException(
                        issue=f"Slow-moving inventory: {stock.product.name}",
                        reason="This product has stock available but no movement history in the CRM.",
                        business_impact="Cash may be tied up in inventory that is not moving.",
                        recommended_action="Check whether this product should be promoted, discounted, or reordered less often.",
                    )
                )

        return exceptions

    def daily_brief(self, stock_rows: list[InventoryStock], movements: list[StockMovement]) -> DailyBrief:
        exceptions = self.detect_exceptions(stock_rows, movements)
        low_stock_names = [row.product.name for row in stock_rows if row.current_stock <= row.low_stock_threshold]
        today = datetime.utcnow().date()
        today_movements = [row for row in movements if row.created_at.date() == today]

        key_metrics = [
            "Total Sales: Not available until sales records are added.",
            "Total Revenue: Not available until sales records are added.",
            "Profit/Loss Status: Not available until revenue and expense records are added.",
            f"Low Stock Items: {len(low_stock_names)}",
            "Employee Attendance Issues: Not available until attendance records are added.",
            "Production Issues: Not available until production records are added.",
            f"Stock Movements Today: {len(today_movements)}",
        ]

        important_alerts = [exception.issue for exception in exceptions[:5]]
        if not important_alerts:
            important_alerts = ["No supported operational alerts found in available CRM data."]

        actions = [exception.recommended_action for exception in exceptions[:2]]
        if not actions:
            actions = ["Keep product and stock movement records updated daily."]

        return DailyBrief(
            business_summary="Daily brief is based only on available CRM data. Sales, profit, payroll, attendance, and production summaries will appear when those modules have records.",
            key_metrics=key_metrics,
            important_alerts=important_alerts,
            recommended_actions=actions,
        )
