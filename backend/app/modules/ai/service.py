from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.ai.schemas import BusinessException, BusinessHealth, BusinessInsight, DailyBrief
from app.modules.attendance.models import AttendanceRecord, AttendanceStatus
from app.modules.finance.schemas import ProfitLossSummary
from app.modules.inventory.models import InventoryStock, MovementType, StockMovement
from app.modules.payroll.models import PayrollRecord
from app.modules.production.models import ProductionBatch
from app.modules.sales.models import Sale


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

    def full_business_health(
        self,
        stock_rows: list[InventoryStock],
        movements: list[StockMovement],
        sales: list[Sale],
        attendance: list[AttendanceRecord],
        payroll: list[PayrollRecord],
        profit_loss: ProfitLossSummary,
        batches: list[ProductionBatch],
    ) -> BusinessHealth:
        exceptions = self.detect_exceptions(stock_rows, movements)
        exceptions.extend(self._module_exceptions(sales, attendance, payroll, profit_loss, batches))

        sales_status = "Not available: no sales records found."
        if sales:
            total_revenue = sum(row.total_revenue for row in sales)
            sales_status = f"{len(sales)} sale(s) recorded with total revenue {total_revenue}."

        profit_status = "Not available: no revenue, payroll, or expense records found."
        if sales or payroll or profit_loss.expenses:
            profit_status = f"{profit_loss.status}: net result is {profit_loss.net_profit}."

        production_status = "Not available: no production batches found."
        if batches:
            produced = sum(row.quantity_produced for row in batches)
            wasted = sum(row.wastage_quantity for row in batches)
            production_status = f"{len(batches)} batch(es), {produced} finished goods, {wasted} wastage units."

        attendance_status = "Not available: no attendance records found."
        if attendance:
            issues = [row for row in attendance if row.status in {AttendanceStatus.absent, AttendanceStatus.late}]
            attendance_status = f"{len(attendance)} attendance record(s), {len(issues)} issue(s)."

        payroll_status = "Not available: no payroll records found."
        if payroll:
            total_payroll = sum(row.net_salary for row in payroll)
            payroll_status = f"{len(payroll)} payroll record(s), total net salary {total_payroll}."

        return BusinessHealth(
            sales_performance=sales_status,
            profit_performance=profit_status,
            inventory_health=self.business_health(stock_rows, movements).inventory_health,
            production_efficiency=production_status,
            employee_attendance=attendance_status,
            payroll_costs=payroll_status,
            exceptions=exceptions,
        )

    def full_daily_brief(
        self,
        stock_rows: list[InventoryStock],
        movements: list[StockMovement],
        sales: list[Sale],
        attendance: list[AttendanceRecord],
        profit_loss: ProfitLossSummary,
        batches: list[ProductionBatch],
    ) -> DailyBrief:
        exceptions = self.detect_exceptions(stock_rows, movements)
        exceptions.extend(self._module_exceptions(sales, attendance, [], profit_loss, batches))
        revenue = sum(row.total_revenue for row in sales)
        top_products: dict[str, int] = {}
        for sale in sales:
            for item in sale.items:
                top_products[item.product.name] = top_products.get(item.product.name, 0) + item.quantity
        top_product = max(top_products, key=top_products.get) if top_products else "Not available"
        attendance_issues = [row for row in attendance if row.status in {AttendanceStatus.absent, AttendanceStatus.late}]
        production_issues = [row for row in batches if row.wastage_quantity > 0]

        return DailyBrief(
            business_summary="Daily brief is based only on available CRM records.",
            key_metrics=[
                f"Total Sales: {len(sales)}",
                f"Total Revenue: {revenue}",
                f"Profit/Loss Status: {profit_loss.status} ({profit_loss.net_profit})",
                f"Low Stock Items: {len([row for row in stock_rows if row.current_stock <= row.low_stock_threshold])}",
                f"Employee Attendance Issues: {len(attendance_issues)}",
                f"Production Issues: {len(production_issues)}",
                f"Top Performing Product: {top_product}",
            ],
            important_alerts=[exception.issue for exception in exceptions[:5]] or ["No supported operational alerts found in available CRM data."],
            recommended_actions=[exception.recommended_action for exception in exceptions[:2]] or ["Keep CRM records updated daily."],
        )

    def _module_exceptions(
        self,
        sales: list[Sale],
        attendance: list[AttendanceRecord],
        payroll: list[PayrollRecord],
        profit_loss: ProfitLossSummary,
        batches: list[ProductionBatch],
    ) -> list[BusinessException]:
        exceptions: list[BusinessException] = []
        if sales and profit_loss.net_profit < 0:
            exceptions.append(
                BusinessException(
                    issue="Profit/Loss risk",
                    reason=f"Net result is {profit_loss.net_profit}.",
                    business_impact="The business is spending more than it earns in recorded CRM data.",
                    recommended_action="Review expenses, payroll records, and product margins.",
                )
            )
        attendance_issues = [row for row in attendance if row.status in {AttendanceStatus.absent, AttendanceStatus.late}]
        if attendance_issues:
            exceptions.append(
                BusinessException(
                    issue="Attendance issues",
                    reason=f"{len(attendance_issues)} late or absent attendance record(s) found.",
                    business_impact="Operations may slow down if staff attendance is inconsistent.",
                    recommended_action="Speak with affected employees and review shift coverage.",
                )
            )
        payroll_total = sum((row.net_salary for row in payroll), Decimal("0"))
        revenue_total = sum((row.total_revenue for row in sales), Decimal("0"))
        if payroll and sales and payroll_total > revenue_total:
            exceptions.append(
                BusinessException(
                    issue="Excess payroll cost",
                    reason=f"Recorded payroll {payroll_total} is higher than recorded revenue {revenue_total}.",
                    business_impact="Payroll may be putting pressure on cash flow.",
                    recommended_action="Review staffing cost against current sales before adding shifts.",
                )
            )
        waste_batches = [row for row in batches if row.wastage_quantity > 0]
        if waste_batches:
            exceptions.append(
                BusinessException(
                    issue="Production wastage",
                    reason=f"{len(waste_batches)} batch(es) include wastage.",
                    business_impact="Wastage can reduce profit and consume raw materials faster.",
                    recommended_action="Check the production process for batches with wastage.",
                )
            )
        return exceptions
