"""
Google Sheets Service - MCP Integration
Handles all data operations with Google Sheets
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid

# MCP Google Sheets integration
from mcp_google_sheets import SheetsClient
from models.customer import Customer, Order, Product

class SheetsService:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.spreadsheet_id = os.getenv('MAIN_SPREADSHEET_ID')
        
        # Sheet names
        self.CUSTOMERS_SHEET = "Customers"
        self.ORDERS_SHEET = "Orders" 
        self.PRODUCTS_SHEET = "Products"
        self.INTERACTIONS_SHEET = "Interactions"
        self.ANALYTICS_SHEET = "Analytics"

    async def get_customer_by_email(self, email: str, company_id: str) -> Optional[Customer]:
        """Find customer by email and company"""
        try:
            # Get customer data from sheet
            data = await self.sheets_client.get_sheet_data(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.CUSTOMERS_SHEET,
                range="A:H"  # Customer columns
            )
            
            for row in data[1:]:  # Skip header
                if len(row) >= 3 and row[2] == email and row[1] == company_id:
                    return Customer(
                        id=row[0],
                        company_name=row[1],
                        email=row[2],
                        phone=row[3] if len(row) > 3 else "",
                        registration_date=row[4] if len(row) > 4 else "",
                        total_spent=float(row[5]) if len(row) > 5 and row[5] else 0.0,
                        last_order_date=row[6] if len(row) > 6 else "",
                        status=row[7] if len(row) > 7 else "active"
                    )
            return None
        except Exception as e:
            print(f"Error getting customer by email: {e}")
            return None

    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        try:
            data = await self.sheets_client.get_sheet_data(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.CUSTOMERS_SHEET,
                range="A:H"
            )
            
            for row in data[1:]:
                if row[0] == customer_id:
                    return Customer(
                        id=row[0],
                        company_name=row[1],
                        email=row[2],
                        phone=row[3] if len(row) > 3 else "",
                        registration_date=row[4] if len(row) > 4 else "",
                        total_spent=float(row[5]) if len(row) > 5 and row[5] else 0.0,
                        last_order_date=row[6] if len(row) > 6 else "",
                        status=row[7] if len(row) > 7 else "active"
                    )
            return None
        except Exception as e:
            print(f"Error getting customer: {e}")
            return None

    async def get_customer_orders(self, customer_id: str, limit: int = 50) -> List[Order]:
        """Get customer order history"""
        try:
            data = await self.sheets_client.get_sheet_data(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.ORDERS_SHEET,
                range="A:I"  # Order columns
            )
            
            orders = []
            for row in data[1:]:  # Skip header
                if len(row) >= 2 and row[1] == customer_id:
                    orders.append(Order(
                        id=row[0],
                        customer_id=row[1],
                        date=row[2] if len(row) > 2 else "",
                        products=json.loads(row[3]) if len(row) > 3 and row[3] else [],
                        quantities=json.loads(row[4]) if len(row) > 4 and row[4] else [],
                        total_amount=float(row[5]) if len(row) > 5 and row[5] else 0.0,
                        status=row[6] if len(row) > 6 else "pending",
                        tracking_number=row[7] if len(row) > 7 else "",
                        notes=row[8] if len(row) > 8 else ""
                    ))
            
            # Sort by date descending and limit
            orders.sort(key=lambda x: x.date, reverse=True)
            return orders[:limit]
        except Exception as e:
            print(f"Error getting customer orders: {e}")
            return []

    async def get_products(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Product]:
        """Get product catalog with filtering"""
        try:
            data = await self.sheets_client.get_sheet_data(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.PRODUCTS_SHEET,
                range="A:H"  # Product columns
            )
            
            products = []
            for row in data[1:]:  # Skip header
                if len(row) >= 6:
                    product = Product(
                        sku=row[0],
                        name=row[1],
                        category=row[2],
                        price=float(row[3]) if row[3] else 0.0,
                        stock_level=int(row[4]) if row[4] else 0,
                        description=row[5] if len(row) > 5 else "",
                        compatibility=row[6].split(',') if len(row) > 6 and row[6] else [],
                        image_url=row[7] if len(row) > 7 else ""
                    )
                    
                    # Apply filters
                    if category and product.category.lower() != category.lower():
                        continue
                    if search and search.lower() not in product.name.lower() and search.lower() not in product.description.lower():
                        continue
                    
                    products.append(product)
            
            return products
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    async def create_order(self, customer_id: str, products: List[Dict[str, Any]], notes: Optional[str] = None) -> Order:
        """Create new customer order"""
        try:
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            current_date = datetime.now().isoformat()
            
            # Calculate total amount
            total_amount = 0.0
            product_list = []
            quantity_list = []
            
            for item in products:
                product_list.append(item['sku'])
                quantity_list.append(item['quantity'])
                total_amount += item['price'] * item['quantity']
            
            # Add order to sheet
            order_data = [
                order_id,
                customer_id,
                current_date,
                json.dumps(product_list),
                json.dumps(quantity_list),
                total_amount,
                "pending",
                "",  # tracking number
                notes or ""
            ]
            
            await self.sheets_client.add_rows(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.ORDERS_SHEET,
                data=[order_data]
            )
            
            # Update customer total spent
            await self._update_customer_total_spent(customer_id, total_amount)
            
            return Order(
                id=order_id,
                customer_id=customer_id,
                date=current_date,
                products=product_list,
                quantities=quantity_list,
                total_amount=total_amount,
                status="pending",
                tracking_number="",
                notes=notes or ""
            )
        except Exception as e:
            print(f"Error creating order: {e}")
            raise

    async def log_interaction(self, customer_id: str, query: str, response: str, session_id: Optional[str] = None):
        """Log customer interaction"""
        try:
            interaction_data = [
                datetime.now().isoformat(),
                customer_id,
                "chat",
                query,
                response,
                session_id or "",
                ""  # satisfaction score - to be filled later
            ]
            
            await self.sheets_client.add_rows(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.INTERACTIONS_SHEET,
                data=[interaction_data]
            )
        except Exception as e:
            print(f"Error logging interaction: {e}")

    async def get_customer_analytics(self, customer_id: str) -> Dict[str, Any]:
        """Get customer analytics and insights"""
        try:
            orders = await self.get_customer_orders(customer_id, 100)
            
            if not orders:
                return {"total_orders": 0, "total_spent": 0, "avg_order_value": 0}
            
            total_spent = sum(order.total_amount for order in orders)
            avg_order_value = total_spent / len(orders)
            
            # Calculate trends
            recent_orders = [o for o in orders if self._is_recent(o.date, 30)]
            monthly_spend = sum(order.total_amount for order in recent_orders)
            
            # Product preferences
            product_counts = {}
            for order in orders:
                for product in order.products:
                    product_counts[product] = product_counts.get(product, 0) + 1
            
            top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_orders": len(orders),
                "total_spent": total_spent,
                "avg_order_value": avg_order_value,
                "monthly_spend": monthly_spend,
                "top_products": top_products,
                "last_order_date": orders[0].date if orders else None,
                "customer_since": orders[-1].date if orders else None
            }
        except Exception as e:
            print(f"Error getting customer analytics: {e}")
            return {}

    async def check_compatibility(self, sku: str, device_model: str) -> Dict[str, Any]:
        """Check product compatibility with device"""
        try:
            products = await self.get_products()
            
            for product in products:
                if product.sku == sku:
                    is_compatible = any(device_model.lower() in comp.lower() for comp in product.compatibility)
                    return {
                        "compatible": is_compatible,
                        "product_name": product.name,
                        "supported_devices": product.compatibility
                    }
            
            return {"compatible": False, "error": "Product not found"}
        except Exception as e:
            print(f"Error checking compatibility: {e}")
            return {"compatible": False, "error": str(e)}

    async def get_order_tracking(self, order_id: str) -> Dict[str, Any]:
        """Get order tracking information"""
        try:
            data = await self.sheets_client.get_sheet_data(
                spreadsheet_id=self.spreadsheet_id,
                sheet=self.ORDERS_SHEET,
                range="A:I"
            )
            
            for row in data[1:]:
                if row[0] == order_id:
                    return {
                        "order_id": row[0],
                        "status": row[6] if len(row) > 6 else "pending",
                        "tracking_number": row[7] if len(row) > 7 else "",
                        "estimated_delivery": self._calculate_delivery_date(row[2] if len(row) > 2 else ""),
                        "order_date": row[2] if len(row) > 2 else ""
                    }
            
            return {"error": "Order not found"}
        except Exception as e:
            print(f"Error getting order tracking: {e}")
            return {"error": str(e)}

    async def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get business dashboard analytics"""
        try:
            # This would aggregate data across all customers
            # Implementation depends on specific business metrics needed
            return {
                "total_customers": 0,
                "total_orders": 0,
                "total_revenue": 0,
                "avg_order_value": 0,
                "top_products": [],
                "recent_activity": []
            }
        except Exception as e:
            print(f"Error getting dashboard analytics: {e}")
            return {}

    # Helper methods
    async def _update_customer_total_spent(self, customer_id: str, amount: float):
        """Update customer's total spent amount"""
        # Implementation to update customer record
        pass

    def _is_recent(self, date_str: str, days: int) -> bool:
        """Check if date is within recent days"""
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return (datetime.now() - date).days <= days
        except:
            return False

    def _calculate_delivery_date(self, order_date: str) -> str:
        """Calculate estimated delivery date"""
        try:
            date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            delivery_date = date + timedelta(days=5)  # 5 business days
            return delivery_date.isoformat()
        except:
            return ""