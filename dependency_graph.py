"""
Supplier-Product Dependency Graph Module

Models supplier-to-product relationships as a directed graph.
Enables simulation of supplier failures and identifies impacted products.

Author: Inventory Management System
Date: 2026
"""

from typing import Dict, Set, List, Tuple, Optional, Any
from collections import deque


class DependencyGraph:
    """
    A directed graph modeling supplier-to-product dependencies.
    
    Nodes can be suppliers or products.
    Edges represent "supplier provides product" relationships.
    
    Attributes:
        _suppliers (Set[str]): Set of supplier IDs
        _products (Set[str]): Set of product IDs
        _adjacency (Dict[str, Set[str]]): Adjacency list representation
        _reverse_adjacency (Dict[str, Set[str]]): Reverse edges for fast lookups
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        self._suppliers: Set[str] = set()
        self._products: Set[str] = set()
        self._adjacency: Dict[str, Set[str]] = {}  # supplier -> {products}
        self._reverse_adjacency: Dict[str, Set[str]] = {}  # product -> {suppliers}
    
    # --------------------- Basic Graph Operations ---------------------
    
    def add_supplier(self, supplier_id: str) -> None:
        """Add a supplier node to the graph."""
        if not isinstance(supplier_id, str):
            raise TypeError("Supplier ID must be a string")
        
        self._suppliers.add(supplier_id)
        if supplier_id not in self._adjacency:
            self._adjacency[supplier_id] = set()
        if supplier_id not in self._reverse_adjacency:
            self._reverse_adjacency[supplier_id] = set()
    
    def add_product(self, product_id: str) -> None:
        """Add a product node to the graph."""
        if not isinstance(product_id, str):
            raise TypeError("Product ID must be a string")
        
        self._products.add(product_id)
        if product_id not in self._adjacency:
            self._adjacency[product_id] = set()
        if product_id not in self._reverse_adjacency:
            self._reverse_adjacency[product_id] = set()
    
    def add_dependency(self, supplier_id: str, product_id: str) -> None:
        """
        Add a directed edge from supplier to product.
        
        Args:
            supplier_id: ID of the supplier
            product_id: ID of the product
            
        Raises:
            ValueError: If supplier or product doesn't exist
        """
        if supplier_id not in self._suppliers:
            raise ValueError(f"Supplier '{supplier_id}' not found")
        if product_id not in self._products:
            raise ValueError(f"Product '{product_id}' not found")
        
        # Add edge: supplier -> product
        self._adjacency[supplier_id].add(product_id)
        # Add reverse edge: product <- supplier
        self._reverse_adjacency[product_id].add(supplier_id)
    
    def remove_supplier(self, supplier_id: str) -> bool:
        """
        Remove a supplier and all its outgoing edges.
        
        Returns:
            True if supplier was removed, False if not found
        """
        if supplier_id not in self._suppliers:
            return False
        
        # Remove supplier from sets
        self._suppliers.remove(supplier_id)
        
        # Remove all outgoing edges (supplier -> products)
        if supplier_id in self._adjacency:
            for product_id in self._adjacency[supplier_id]:
                self._reverse_adjacency[product_id].discard(supplier_id)
            del self._adjacency[supplier_id]
        
        # Remove all incoming edges (shouldn't exist for suppliers)
        if supplier_id in self._reverse_adjacency:
            for node in self._reverse_adjacency[supplier_id]:
                self._adjacency[node].discard(supplier_id)
            del self._reverse_adjacency[supplier_id]
        
        return True
    
    def remove_product(self, product_id: str) -> bool:
        """
        Remove a product and all its incoming edges.
        
        Returns:
            True if product was removed, False if not found
        """
        if product_id not in self._products:
            return False
        
        # Remove product from sets
        self._products.remove(product_id)
        
        # Remove all incoming edges (suppliers -> product)
        if product_id in self._reverse_adjacency:
            for supplier_id in self._reverse_adjacency[product_id]:
                self._adjacency[supplier_id].discard(product_id)
            del self._reverse_adjacency[product_id]
        
        # Remove all outgoing edges (shouldn't exist for products)
        if product_id in self._adjacency:
            for node in self._adjacency[product_id]:
                self._reverse_adjacency[node].discard(product_id)
            del self._adjacency[product_id]
        
        return True
    
    def get_suppliers_for_product(self, product_id: str) -> Set[str]:
        """
        Get all suppliers that provide a given product.
        
        Returns:
            Set of supplier IDs
        """
        return self._reverse_adjacency.get(product_id, set()).copy()
    
    def get_products_for_supplier(self, supplier_id: str) -> Set[str]:
        """
        Get all products provided by a given supplier.
        
        Returns:
            Set of product IDs
        """
        return self._adjacency.get(supplier_id, set()).copy()
    
    # --------------------- Failure Simulation ---------------------
    
    def simulate_supplier_failure(self, failed_supplier_id: str) -> Dict[str, List[str]]:
        """
        Simulate failure of a supplier and analyze impact on products.
        
        Args:
            failed_supplier_id: ID of the failed supplier
            
        Returns:
            Dictionary with three categories:
            - 'failed': Products with ZERO remaining suppliers
            - 'at_risk': Products with LIMITED suppliers (1-2 remaining)
            - 'safe': Products with ADEQUATE suppliers (3+ remaining)
            
            Each category contains a list of product IDs.
        """
        if failed_supplier_id not in self._suppliers:
            raise ValueError(f"Supplier '{failed_supplier_id}' not found")
        
        # Get all products this supplier provides
        affected_products = self.get_products_for_supplier(failed_supplier_id)
        
        # Categorize products based on remaining suppliers
        failed_products = []
        at_risk_products = []
        safe_products = []
        
        for product_id in affected_products:
            # Count remaining suppliers after failure
            remaining_suppliers = len(self.get_suppliers_for_product(product_id)) - 1
            
            if remaining_suppliers <= 0:
                failed_products.append(product_id)
            elif remaining_suppliers <= 2:
                at_risk_products.append(product_id)
            else:  # 3 or more suppliers remaining
                safe_products.append(product_id)
        
        return {
            'failed': failed_products,
            'at_risk': at_risk_products,
            'safe': safe_products
        }
    
    def simulate_multiple_failures(self, failed_supplier_ids: List[str]) -> Dict[str, List[str]]:
        """
        Simulate failure of multiple suppliers (cascade effect).
        
        Args:
            failed_supplier_ids: List of supplier IDs that fail
            
        Returns:
            Same structure as simulate_supplier_failure, but considers
            all failed suppliers simultaneously.
        """
        # Validate all suppliers exist
        for supplier_id in failed_supplier_ids:
            if supplier_id not in self._suppliers:
                raise ValueError(f"Supplier '{supplier_id}' not found")
        
        # Get all products affected by any failed supplier
        affected_products = set()
        for supplier_id in failed_supplier_ids:
            affected_products.update(self.get_products_for_supplier(supplier_id))
        
        # Count how many of the failed suppliers provided each product
        supplier_counts = {}
        for supplier_id in failed_supplier_ids:
            for product_id in self.get_products_for_supplier(supplier_id):
                supplier_counts[product_id] = supplier_counts.get(product_id, 0) + 1
        
        # Categorize products
        failed_products = []
        at_risk_products = []
        safe_products = []
        
        for product_id in affected_products:
            total_suppliers = len(self.get_suppliers_for_product(product_id))
            failed_for_product = supplier_counts.get(product_id, 0)
            remaining = total_suppliers - failed_for_product
            
            if remaining <= 0:
                failed_products.append(product_id)
            elif remaining <= 2:
                at_risk_products.append(product_id)
            else:
                safe_products.append(product_id)
        
        return {
            'failed': failed_products,
            'at_risk': at_risk_products,
            'safe': safe_products
        }
    
    # --------------------- Analysis & Queries ---------------------
    
    def get_critical_suppliers(self, threshold: int = 1) -> List[Tuple[str, int]]:
        """
        Identify suppliers whose failure would impact the most products.
        
        Args:
            threshold: Minimum number of products to be considered critical
            
        Returns:
            List of (supplier_id, product_count) tuples, sorted by impact
        """
        critical = []
        for supplier_id in self._suppliers:
            product_count = len(self.get_products_for_supplier(supplier_id))
            if product_count >= threshold:
                critical.append((supplier_id, product_count))
        
        # Sort by impact (highest first)
        critical.sort(key=lambda x: x[1], reverse=True)
        return critical
    
    def get_vulnerable_products(self, min_suppliers: int = 2) -> List[Tuple[str, int]]:
        """
        Identify products with limited supplier options.
        
        Args:
            min_suppliers: Products with fewer suppliers than this are vulnerable
            
        Returns:
            List of (product_id, supplier_count) tuples for vulnerable products
        """
        vulnerable = []
        for product_id in self._products:
            supplier_count = len(self.get_suppliers_for_product(product_id))
            if 0 < supplier_count < min_suppliers:
                vulnerable.append((product_id, supplier_count))
        
        # Sort by most vulnerable (fewest suppliers) first
        vulnerable.sort(key=lambda x: x[1])
        return vulnerable
    
    def get_supply_chain_depth(self, start_supplier: str, max_depth: int = 10) -> Dict[int, List[str]]:
        """
        Perform BFS to find all products reachable from a supplier within N degrees.
        
        Args:
            start_supplier: Starting supplier node
            max_depth: Maximum depth to search
            
        Returns:
            Dictionary mapping depth -> list of product IDs at that depth
        """
        if start_supplier not in self._suppliers:
            raise ValueError(f"Supplier '{start_supplier}' not found")
        
        visited = set()
        queue = deque([(start_supplier, 0)])
        result = {i: [] for i in range(max_depth + 1)}
        
        while queue:
            node, depth = queue.popleft()
            
            if node in visited or depth > max_depth:
                continue
            
            visited.add(node)
            
            # If this is a product (not a supplier), add to results
            if node in self._products and depth > 0:
                result[depth].append(node)
            
            # Explore neighbors (products supplied by this node)
            for neighbor in self._adjacency.get(node, set()):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        # Remove empty depth levels
        return {k: v for k, v in result.items() if v}
    
    # --------------------- Integration Helpers ---------------------
    
    def load_from_inventory(self, inventory: Any) -> None:
        """
        Load existing products from an Inventory instance.
        
        Args:
            inventory: An instance of Inventory class with snapshot() method
                       that returns product data
        """
        try:
            products_data = inventory.snapshot()
            for product_data in products_data:
                product_id = product_data.get('product_id') or product_data.get('id')
                if product_id:
                    self.add_product(str(product_id))
        except AttributeError:
            raise TypeError("Inventory object must have a snapshot() method")
        except Exception as e:
            raise ValueError(f"Failed to load from inventory: {e}")
    
    def get_supplier_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current dependency graph state.
        
        Returns:
            Dictionary with counts and statistics
        """
        total_dependencies = sum(len(products) for products in self._adjacency.values())
        
        # Calculate average suppliers per product
        supplier_counts = [len(self.get_suppliers_for_product(p)) for p in self._products]
        avg_suppliers = sum(supplier_counts) / len(supplier_counts) if supplier_counts else 0
        
        return {
            'total_suppliers': len(self._suppliers),
            'total_products': len(self._products),
            'total_dependencies': total_dependencies,
            'avg_suppliers_per_product': avg_suppliers,
            'products_with_no_suppliers': len([p for p in self._products 
                                               if len(self.get_suppliers_for_product(p)) == 0])
        }
    
    # --------------------- Utility Methods ---------------------
    
    def clear(self) -> None:
        """Clear the entire graph."""
        self._suppliers.clear()
        self._products.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()
    
    def __contains__(self, node_id: str) -> bool:
        """Check if a node exists in the graph."""
        return node_id in self._suppliers or node_id in self._products
    
    def __str__(self) -> str:
        """String representation of the graph."""
        summary = self.get_supplier_summary()
        return (f"DependencyGraph(suppliers={summary['total_suppliers']}, "
                f"products={summary['total_products']}, "
                f"dependencies={summary['total_dependencies']})")
    
    def __repr__(self) -> str:
        return self.__str__()


# --------------------- Example Usage & Testing ---------------------

def example_usage():
    """
    Example demonstrating how to use the DependencyGraph module.
    This simulates a real-world supply chain scenario.
    """
    print("=" * 60)
    print("DEPENDENCY GRAPH MODULE - EXAMPLE USAGE")
    print("=" * 60)
    
    # 1. Initialize the dependency graph
    graph = DependencyGraph()
    print("1. Initialized empty dependency graph")
    print(f"   {graph}\n")
    
    # 2. Add suppliers
    suppliers = ["S001", "S002", "S003", "S004", "S005"]
    for supplier in suppliers:
        graph.add_supplier(supplier)
    print("2. Added suppliers:", ", ".join(suppliers))
    
    # 3. Add products (from inventory)
    products = ["P100", "P101", "P102", "P103", "P104", "P105", "P106"]
    for product in products:
        graph.add_product(product)
    print("3. Added products:", ", ".join(products))
    
    # 4. Create dependencies (supplier -> product relationships)
    dependencies = [
        ("S001", "P100"), ("S001", "P101"), ("S001", "P102"),  # S001 supplies 3 products
        ("S002", "P100"), ("S002", "P103"),                   # S002 supplies 2 products
        ("S003", "P101"), ("S003", "P104"),                   # S003 supplies 2 products
        ("S004", "P102"), ("S004", "P103"), ("S004", "P104"), # S004 supplies 3 products
        ("S005", "P105"), ("S005", "P106"),                   # S005 supplies 2 products
    ]
    
    for supplier, product in dependencies:
        graph.add_dependency(supplier, product)
    
    print("4. Created supplier-product dependencies")
    print(f"   Total dependencies: {graph.get_supplier_summary()['total_dependencies']}\n")
    
    # 5. Analyze initial state
    print("5. Initial Analysis:")
    summary = graph.get_supplier_summary()
    print(f"   Average suppliers per product: {summary['avg_suppliers_per_product']:.2f}")
    
    critical = graph.get_critical_suppliers(threshold=2)
    print(f"   Critical suppliers (supply ≥2 products): {len(critical)}")
    
    vulnerable = graph.get_vulnerable_products(min_suppliers=2)
    print(f"   Vulnerable products (<2 suppliers): {len(vulnerable)}")
    for product, count in vulnerable[:3]:  # Show first 3
        print(f"     - {product}: {count} supplier(s)")
    if len(vulnerable) > 3:
        print(f"     ... and {len(vulnerable) - 3} more")
    print()
    
    # 6. Simulate single supplier failure
    print("6. SIMULATING SUPPLIER FAILURE: S001")
    impact = graph.simulate_supplier_failure("S001")
    
    print(f"   Failed products (no suppliers): {len(impact['failed'])}")
    if impact['failed']:
        print(f"     {', '.join(impact['failed'])}")
    
    print(f"   At-risk products (1-2 suppliers): {len(impact['at_risk'])}")
    if impact['at_risk']:
        print(f"     {', '.join(impact['at_risk'])}")
    
    print(f"   Safe products (3+ suppliers): {len(impact['safe'])}")
    if impact['safe']:
        print(f"     {', '.join(impact['safe'])}")
    print()
    
    # 7. Simulate multiple supplier failures (cascade)
    print("7. SIMULATING MULTIPLE FAILURES: S001 and S004")
    impact_multi = graph.simulate_multiple_failures(["S001", "S004"])
    
    print(f"   Failed products: {len(impact_multi['failed'])}")
    if impact_multi['failed']:
        print(f"     {', '.join(impact_multi['failed'])}")
    
    print(f"   At-risk products: {len(impact_multi['at_risk'])}")
    if impact_multi['at_risk']:
        print(f"     {', '.join(impact_multi['at_risk'])}")
    
    # 8. Show supply chain depth analysis
    print("\n8. Supply Chain Depth Analysis for S003:")
    chain_depth = graph.get_supply_chain_depth("S003", max_depth=2)
    for depth, products in chain_depth.items():
        print(f"   Depth {depth}: {len(products)} product(s)")
        if products:
            print(f"     {', '.join(products)}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    # Run examples when module is executed directly
    example_usage()