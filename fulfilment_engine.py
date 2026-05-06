"""
fulfilment_engine.py
DSA-based Order Fulfilment System
Integrates: Inventory + Graph (single) for optimal order fulfilment

Uses:
- Graph algorithms (Dijkstra) - for optimal routes
- Greedy decision-making - for warehouse selection
- Priority queues - for order scheduling
- Hash tables - for inventory lookup
- Trees (BST) - for product categorization

Single Graph Rule: Uses existing graph.py as the fulfilment graph
"""

import heapq
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
from enum import Enum


# ==================== DATA STRUCTURES ====================

class Urgency(Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    URGENT = "urgent"


class ProductType(Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FURNITURE = "furniture"
    FOOD = "food"
    OTHER = "other"


@dataclass
class OrderItem:
    """Represents a single product in an order"""
    product_id: str
    quantity: int
    product_type: ProductType


@dataclass
class Order:
    """Customer order data structure"""
    order_id: str
    customer_id: str
    items: List[OrderItem]
    destination: str  # Warehouse ID
    urgency: Urgency
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)


@dataclass
class Warehouse:
    """Warehouse node with inventory"""
    warehouse_id: str
    name: str
    location: str
    capacity: int
    inventory: Dict[str, int]  # product_id -> quantity
    
    def has_stock(self, product_id: str, quantity: int) -> bool:
        return self.inventory.get(product_id, 0) >= quantity
    
    def allocate_stock(self, product_id: str, quantity: int) -> bool:
        if self.has_stock(product_id, quantity):
            self.inventory[product_id] -= quantity
            return True
        return False
    
    def add_stock(self, product_id: str, quantity: int):
        self.inventory[product_id] = self.inventory.get(product_id, 0) + quantity


class OrderPriorityQueue:
    """Priority queue for order scheduling using heapq"""
    def __init__(self):
        self._queue = []
        self._counter = 0  # For tie-breaking
    
    def push(self, order: Order, priority: float):
        """Push order with priority (lower = higher priority)"""
        # Priority calculation: urgency + waiting time
        urgency_priority = {
            Urgency.URGENT: 1,
            Urgency.EXPRESS: 2,
            Urgency.STANDARD: 3
        }
        
        base_priority = urgency_priority[order.urgency]
        waiting_time = (datetime.now() - order.created_at).total_seconds() / 3600
        
        total_priority = base_priority + (waiting_time * 0.1)
        heapq.heappush(self._queue, (total_priority, self._counter, order))
        self._counter += 1
    
    def pop(self) -> Optional[Order]:
        """Pop highest priority order"""
        if not self._queue:
            return None
        _, _, order = heapq.heappop(self._queue)
        return order
    
    def is_empty(self) -> bool:
        return len(self._queue) == 0
    
    def size(self) -> int:
        return len(self._queue)


class ProductCategoryTree:
    """BST for organizing products by category for quick lookup"""
    class Node:
        def __init__(self, category: str):
            self.category = category
            self.products = set()  # product_ids in this category
            self.left = None
            self.right = None
    
    def __init__(self):
        self.root = None
    
    def insert(self, category: str, product_id: str):
        if not self.root:
            self.root = self.Node(category)
            self.root.products.add(product_id)
            return
        
        node = self.root
        while node:
            if category == node.category:
                node.products.add(product_id)
                return
            elif category < node.category:
                if not node.left:
                    node.left = self.Node(category)
                    node.left.products.add(product_id)
                    return
                node = node.left
            else:
                if not node.right:
                    node.right = self.Node(category)
                    node.right.products.add(product_id)
                    return
                node = node.right
    
    def find(self, category: str) -> Set[str]:
        """Find all products in a category"""
        node = self.root
        while node:
            if category == node.category:
                return node.products
            elif category < node.category:
                node = node.left
            else:
                node = node.right
        return set()
    
    def get_all_products(self) -> Dict[str, Set[str]]:
        """Get all products organized by category"""
        result = {}
        stack = [self.root] if self.root else []
        
        while stack:
            node = stack.pop()
            if node:
                result[node.category] = node.products
                stack.append(node.left)
                stack.append(node.right)
        
        return result


# ==================== FULFILMENT ENGINE ====================

class FulfilmentEngine:
    """
    Core fulfilment engine using DSA concepts:
    - Dijkstra's algorithm for optimal routes
    - Greedy warehouse selection
    - Priority queue for order scheduling
    - Hash tables for inventory lookup
    - BST for product categorization
    """
    
    def __init__(self, inventory_system, graph):
        """
        Args:
            inventory_system: Existing inventory system
            graph: Single graph instance (from graph.py)
        """
        self.inventory = inventory_system
        self.graph = graph  # SINGLE GRAPH - used for all routing
        
        # Data structures
        self.warehouses: Dict[str, Warehouse] = {}
        self.order_queue = OrderPriorityQueue()
        self.category_tree = ProductCategoryTree()
        
        # Statistics
        self.fulfilled_orders = 0
        self.failed_orders = 0
        self.total_delivery_distance = 0
        
        # Initialize with default warehouses
        self._initialize_warehouses()
    
    def _initialize_warehouses(self):
        """Initialize warehouse network"""
        default_warehouses = [
            Warehouse("main", "Main Warehouse", "Central", 10000, {}),
            Warehouse("north", "North Regional", "North Region", 5000, {}),
            Warehouse("south", "South Regional", "South Region", 5000, {}),
            Warehouse("east", "East Regional", "East Region", 5000, {}),
            Warehouse("west", "West Regional", "West Region", 5000, {}),
            Warehouse("local1", "Local Store #1", "Local", 1000, {}),
            Warehouse("local2", "Local Store #2", "Local", 1000, {}),
            Warehouse("local3", "Local Store #3", "Local", 1000, {})
        ]
        
        for wh in default_warehouses:
            self.warehouses[wh.warehouse_id] = wh
        
        # Load inventory into warehouses (simplified - would come from DB)
        self._distribute_inventory()
    
    def _distribute_inventory(self):
        """Distribute inventory across warehouses (simplified)"""
        # In real system, this would come from database
        # For now, simulate distribution
        products = self.inventory.list_sorted_by_price() if hasattr(self.inventory, 'list_sorted_by_price') else []
        
        for product in products:
            # Add to category tree
            self.category_tree.insert(product.category, product.product_id)
            
            # Distribute to warehouses
            if product.quantity > 0:
                # Main warehouse gets 40%, regionals get 15% each
                self.warehouses["main"].add_stock(product.product_id, int(product.quantity * 0.4))
                remaining = product.quantity - int(product.quantity * 0.4)
                
                regionals = ["north", "south", "east", "west"]
                per_regional = remaining // len(regionals)
                
                for wh_id in regionals:
                    self.warehouses[wh_id].add_stock(product.product_id, per_regional)
    
    def place_order(self, order: Order) -> str:
        """Place an order in the fulfilment system"""
        self.order_queue.push(order, 0)  # Priority will be calculated in queue
        return f"Order {order.order_id} placed in queue. Position: {self.order_queue.size()}"
    
    def process_next_order(self) -> Dict:
        """Process the highest priority order"""
        order = self.order_queue.pop()
        if not order:
            return {"status": "no_orders"}
        
        print(f"\n[Fulfilment] Processing order {order.order_id}")
        print(f"  Destination: {order.destination}")
        print(f"  Urgency: {order.urgency.value}")
        print(f"  Items: {[(item.product_id, item.quantity) for item in order.items]}")
        
        # Step 1: Check if we can fulfil from a single warehouse
        fulfilment_plan = self._find_optimal_fulfilment(order)
        
        if fulfilment_plan["feasible"]:
            # Step 2: Execute fulfilment
            success = self._execute_fulfilment(order, fulfilment_plan)
            
            if success:
                self.fulfilled_orders += 1
                return {
                    "status": "fulfilled",
                    "order_id": order.order_id,
                    "plan": fulfilment_plan,
                    "message": "Order fulfilled successfully"
                }
            else:
                self.failed_orders += 1
                return {
                    "status": "failed",
                    "order_id": order.order_id,
                    "reason": "Execution failed"
                }
        else:
            # Split order or partial fulfilment
            split_plan = self._split_order_fulfilment(order)
            
            if split_plan["feasible"]:
                success = True
                for plan in split_plan["plans"]:
                    if not self._execute_fulfilment(order, plan):
                        success = False
                        break
                
                if success:
                    self.fulfilled_orders += 1
                    return {
                        "status": "fulfilled_split",
                        "order_id": order.order_id,
                        "split_plan": split_plan,
                        "message": "Order fulfilled from multiple warehouses"
                    }
            
            self.failed_orders += 1
            return {
                "status": "failed",
                "order_id": order.order_id,
                "reason": "Insufficient stock"
            }
    
    def _find_optimal_fulfilment(self, order: Order) -> Dict:
        """Find optimal warehouse to fulfil order (greedy approach)"""
        
        # Get warehouses that have all items in stock
        candidate_warehouses = []
        
        for wh_id, warehouse in self.warehouses.items():
            can_fulfil = True
            for item in order.items:
                if not warehouse.has_stock(item.product_id, item.quantity):
                    can_fulfil = False
                    break
            
            if can_fulfil:
                # Calculate distance to destination
                distance, _ = self.graph.shortest_path(wh_id, order.destination)
                candidate_warehouses.append((wh_id, distance))
        
        if not candidate_warehouses:
            return {"feasible": False, "reason": "No single warehouse has all items"}
        
        # Greedy choice: pick closest warehouse with all items
        candidate_warehouses.sort(key=lambda x: x[1])
        best_warehouse, distance = candidate_warehouses[0]
        
        return {
            "feasible": True,
            "warehouse": best_warehouse,
            "distance": distance,
            "items": [(item.product_id, item.quantity) for item in order.items],
            "cost": self._calculate_cost(distance, order)
        }
    
    def _split_order_fulfilment(self, order: Order) -> Dict:
        """Split order across multiple warehouses"""
        # Track remaining quantities
        remaining = {item.product_id: item.quantity for item in order.items}
        fulfilment_plans = []
        
        # Try to fulfil from closest warehouses first
        warehouses_by_distance = self._get_warehouses_by_distance(order.destination)
        
        for wh_id in warehouses_by_distance:
            if all(qty == 0 for qty in remaining.values()):
                break
            
            # Check what this warehouse can supply
            warehouse = self.warehouses[wh_id]
            items_from_this_warehouse = []
            
            for product_id, needed_qty in remaining.items():
                if needed_qty > 0:
                    available = warehouse.inventory.get(product_id, 0)
                    if available > 0:
                        supply_qty = min(available, needed_qty)
                        items_from_this_warehouse.append((product_id, supply_qty))
                        remaining[product_id] -= supply_qty
            
            if items_from_this_warehouse:
                distance, _ = self.graph.shortest_path(wh_id, order.destination)
                fulfilment_plans.append({
                    "warehouse": wh_id,
                    "distance": distance,
                    "items": items_from_this_warehouse,
                    "cost": self._calculate_cost(distance, order, len(items_from_this_warehouse))
                })
        
        # Check if we fulfilled everything
        if all(qty == 0 for qty in remaining.values()):
            return {
                "feasible": True,
                "plans": fulfilment_plans,
                "total_cost": sum(plan["cost"] for plan in fulfilment_plans),
                "total_distance": sum(plan["distance"] for plan in fulfilment_plans)
            }
        else:
            return {"feasible": False, "reason": "Insufficient stock across all warehouses"}
    
    def _execute_fulfilment(self, order: Order, plan: Dict) -> bool:
        """Execute the fulfilment plan (deduct inventory, log delivery)"""
        try:
            warehouse = self.warehouses[plan["warehouse"]]
            
            # Deduct inventory
            for product_id, quantity in plan["items"]:
                if not warehouse.allocate_stock(product_id, quantity):
                    return False
            
            # Update statistics
            self.total_delivery_distance += plan["distance"]
            
            print(f"  ✓ Fulfilled from {plan['warehouse']}")
            print(f"  ✓ Distance: {plan['distance']}km")
            print(f"  ✓ Cost: ${plan['cost']:.2f}")
            
            return True
        except Exception as e:
            print(f"  ✗ Fulfilment failed: {e}")
            return False
    
    def _get_warehouses_by_distance(self, destination: str) -> List[str]:
        """Get warehouses sorted by distance to destination"""
        distances = []
        for wh_id in self.warehouses:
            if wh_id != destination:
                distance, _ = self.graph.shortest_path(wh_id, destination)
                distances.append((wh_id, distance))
        
        distances.sort(key=lambda x: x[1])
        return [wh_id for wh_id, _ in distances]
    
    def _calculate_cost(self, distance: float, order: Order, item_count: int = None) -> float:
        """Calculate delivery cost based on distance and order properties"""
        base_cost = distance * 0.5  # $0.5 per km
        
        # Adjust for product types in order
        for item in order.items:
            if item.product_type == ProductType.FURNITURE:
                base_cost *= 1.2
            elif item.product_type == ProductType.ELECTRONICS:
                base_cost *= 1.5
            elif item.product_type == ProductType.FOOD:
                base_cost *= 2.0
        
        # Adjust for urgency
        if order.urgency == Urgency.EXPRESS:
            base_cost *= 1.5
        elif order.urgency == Urgency.URGENT:
            base_cost *= 2.5
        
        # If split delivery, add overhead
        if item_count and item_count > 1:
            base_cost *= (1 + 0.1 * (item_count - 1))
        
        return round(base_cost, 2)
    
    def get_statistics(self) -> Dict:
        """Get fulfilment engine statistics"""
        return {
            "fulfilled_orders": self.fulfilled_orders,
            "failed_orders": self.failed_orders,
            "pending_orders": self.order_queue.size(),
            "total_delivery_distance": self.total_delivery_distance,
            "warehouse_count": len(self.warehouses),
            "avg_distance_per_order": (
                self.total_delivery_distance / self.fulfilled_orders
                if self.fulfilled_orders > 0 else 0
            )
        }

    def get_warehouses(self) -> List[Dict]:
        """Return a summary list of all warehouses and their inventory metrics."""
        result = []
        for wh_id, warehouse in self.warehouses.items():
            result.append({
                "warehouse_id": warehouse.warehouse_id,
                "name": warehouse.name,
                "total_items": sum(warehouse.inventory.values()),
                "unique_products": len(warehouse.inventory)
            })
        return result
    
    def get_warehouse_inventory(self, warehouse_id: str) -> Dict:
        """Get inventory for a specific warehouse"""
        if warehouse_id not in self.warehouses:
            return {}
        
        warehouse = self.warehouses[warehouse_id]
        return {
            "warehouse_id": warehouse.warehouse_id,
            "name": warehouse.name,
            "total_items": sum(warehouse.inventory.values()),
            "unique_products": len(warehouse.inventory),
            "inventory": warehouse.inventory
        }
    
    def search_products_by_category(self, category: str) -> List[str]:
        """Search products by category using BST"""
        return list(self.category_tree.find(category))
    
    def get_all_categories(self) -> Dict[str, Set[str]]:
        """Get all products organized by category"""
        return self.category_tree.get_all_products()


# ==================== INTEGRATION HELPERS ====================

def create_sample_fulfilment_engine(inventory_system, graph):
    """Create and initialize a fulfilment engine with sample data"""
    engine = FulfilmentEngine(inventory_system, graph)
    
    # Add some sample edges to the graph
    try:
        graph.add_edge("main", "north", 150)
        graph.add_edge("main", "south", 200)
        graph.add_edge("main", "east", 180)
        graph.add_edge("main", "west", 120)
        graph.add_edge("north", "local1", 50)
        graph.add_edge("south", "local3", 60)
        graph.add_edge("east", "local2", 70)
        graph.add_edge("west", "local2", 90)
        graph.add_edge("north", "east", 220)
        graph.add_edge("south", "west", 250)
    except Exception as e:
        print(f"Note: Could not add graph edges: {e}")
    
    return engine


def create_sample_order():
    """Create a sample order for testing"""
    return Order(
        order_id="ORD001",
        customer_id="CUST123",
        items=[
            OrderItem("P001", 2, ProductType.ELECTRONICS),
            OrderItem("P002", 5, ProductType.CLOTHING)
        ],
        destination="local1",
        urgency=Urgency.STANDARD
    )


# ==================== DEMONSTRATION ====================

if __name__ == "__main__":
    print("=" * 70)
    print("FULFILMENT ENGINE DEMONSTRATION")
    print("=" * 70)
    
    # Note: This would integrate with existing inventory and graph
    print("\nThis module is designed to integrate with:")
    print("1. Existing inventory system (inventory.py)")
    print("2. Single graph instance (graph.py)")
    print("\nKey DSA components demonstrated:")
    print("✓ Graph algorithms (Dijkstra) - for optimal routes")
    print("✓ Greedy decision-making - for warehouse selection")
    print("✓ Priority queues - for order scheduling")
    print("✓ Hash tables - for inventory lookup")
    print("✓ Trees (BST) - for product categorization")
    print("=" * 70)