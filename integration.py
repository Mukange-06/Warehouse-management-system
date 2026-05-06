"""
Integration Module - Connects Inventory, Supply Chain, and Delivery systems
"""

from inventory import Inventory
from dependency_graph import DependencyGraph

class IntegratedSystem:
    """Main integration class connecting all modules"""
    
    def __init__(self):
        self.inventory = Inventory()
        self.supply_chain = DependencyGraph()
        self._setup_integration()
    
    def _setup_integration(self):
        """Setup initial integration between systems"""
        # Load products from inventory into supply chain
        self.supply_chain.load_from_inventory(self.inventory)
        
        # Add mock suppliers (in real system, load from database)
        self._add_mock_suppliers()
        
        # Create mock dependencies (in real system, load from purchase orders)
        self._create_mock_dependencies()
    
    def _add_mock_suppliers(self):
        """Add mock supplier data for demonstration"""
        suppliers = [
            "TechSupplies Inc",
            "GlobalParts Co", 
            "QualityComponents Ltd",
            "ElectroCorp",
            "FastDelivery Ltd",
            "Precision Tools"
        ]
        
        for supplier in suppliers:
            self.supply_chain.add_supplier(supplier)
    
    def _create_mock_dependencies(self):
        """Create mock supplier-product dependencies"""
        # Get product IDs from inventory
        try:
            products_data = self.inventory.snapshot()
            if not products_data:
                return
            
            # Create dependencies (in real system, this would come from actual data)
            for i, product_data in enumerate(products_data):
                product_id = str(product_data.get('product_id') or product_data.get('id'))
                
                # Assign suppliers based on index
                if i % 3 == 0:
                    self.supply_chain.add_dependency("TechSupplies Inc", product_id)
                    self.supply_chain.add_dependency("QualityComponents Ltd", product_id)
                elif i % 3 == 1:
                    self.supply_chain.add_dependency("GlobalParts Co", product_id)
                    self.supply_chain.add_dependency("ElectroCorp", product_id)
                else:
                    self.supply_chain.add_dependency("FastDelivery Ltd", product_id)
                    self.supply_chain.add_dependency("Precision Tools", product_id)
                    
        except Exception as e:
            print(f"Warning: Could not create dependencies: {e}")
    
    def get_system_summary(self):
        """Get summary of entire integrated system"""
        inventory_summary = {
            "total_products": len(self.inventory),
            "is_empty": self.inventory.is_empty()
        }
        
        supply_chain_summary = self.supply_chain.get_supplier_summary()
        
        return {
            "inventory": inventory_summary,
            "supply_chain": supply_chain_summary,
            "integrated": True
        }
    
    def simulate_supplier_failure(self, supplier_name):
        """Simulate supplier failure and get impact on inventory"""
        impact = self.supply_chain.simulate_supplier_failure(supplier_name)
        
        # Get detailed product information for affected products
        detailed_impact = {}
        for category, product_ids in impact.items():
            detailed_impact[category] = []
            for product_id in product_ids:
                product = self.inventory.get_by_id(product_id)
                if product:
                    detailed_impact[category].append({
                        "id": product.product_id,
                        "name": product.name,
                        "quantity": product.quantity,
                        "price": product.price,
                        "value": product.quantity * product.price
                    })
        
        return {
            "failed_supplier": supplier_name,
            "impact": impact,
            "detailed_impact": detailed_impact,
            "total_products_affected": sum(len(items) for items in detailed_impact.values())
        }
    
    def get_risk_analysis(self):
        """Get comprehensive risk analysis"""
        vulnerable_products = self.supply_chain.get_vulnerable_products(min_suppliers=2)
        critical_suppliers = self.supply_chain.get_critical_suppliers(threshold=2)
        
        return {
            "vulnerable_products": vulnerable_products,
            "critical_suppliers": critical_suppliers,
            "supply_chain_health": self._calculate_health_score()
        }
    
    def _calculate_health_score(self):
        """Calculate overall supply chain health score (0-100)"""
        try:
            summary = self.supply_chain.get_supplier_summary()
            
            # Simple health calculation
            total_products = summary['total_products']
            products_no_suppliers = summary['products_with_no_suppliers']
            avg_suppliers = summary['avg_suppliers_per_product']
            
            if total_products == 0:
                return 100
            
            # Penalize products with no suppliers
            no_supplier_penalty = (products_no_suppliers / total_products) * 50
            
            # Reward multiple suppliers per product
            supplier_bonus = min(avg_suppliers * 10, 30)
            
            health_score = 100 - no_supplier_penalty + supplier_bonus
            return max(0, min(100, health_score))
            
        except:
            return 50  # Default score if calculation fails


# Singleton instance for easy access
integrated_system = IntegratedSystem()