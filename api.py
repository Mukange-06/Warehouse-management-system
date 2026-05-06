"""
Flask REST API for Inventory Management System v3.0
Now includes Fulfilment Engine integration (replaces supply chain)
Single Graph Rule: Uses graph.py as the fulfilment graph
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from inventory import Inventory
from product import Product
from graph import Graph
from storage import load_inventory, save_inventory, DEFAULT_DB_FILE

# Import fulfilment engine
try:
    from fulfilment_engine import (
        FulfilmentEngine, Order, OrderItem, 
        ProductType, Urgency, create_sample_fulfilment_engine
    )
    HAS_FULFILMENT = True
    print("✓ Fulfilment engine imported successfully")
except ImportError as e:
    HAS_FULFILMENT = False
    print(f"✗ Fulfilment engine import failed: {e}")

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# ==================== GLOBAL INSTANCES ====================

# Use the same Inventory instance as the CLI would
inventory = Inventory()

# Load persisted inventory (if present)
try:
    loaded = load_inventory(inventory, DEFAULT_DB_FILE)
    if loaded:
        print(f"✓ Loaded {loaded} products from {DEFAULT_DB_FILE}")
except Exception as e:
    print(f"⚠️ Failed to load persisted inventory: {e}")

# Create SINGLE graph instance (fulfilment graph)
fulfilment_graph = Graph()

# ==================== INITIALIZE GRAPH ====================

def initialize_graph():
    """Initialize the fulfilment graph with nodes and edges"""
    # Add all warehouse nodes
    warehouses = ["main", "north", "south", "east", "west", "local1", "local2", "local3"]
    
    for wh in warehouses:
        fulfilment_graph.add_node(wh)
    
    # Add edges with distances (in km)
    edges = [
        ("main", "north", 150),
        ("main", "south", 200),
        ("main", "east", 180),
        ("main", "west", 120),
        ("north", "local1", 50),
        ("south", "local3", 60),
        ("east", "local2", 70),
        ("west", "local2", 90),
        ("north", "east", 220),
        ("south", "west", 250)
    ]
    
    for src, dest, weight in edges:
        try:
            fulfilment_graph.add_edge(src, dest, weight, bidirectional=True)
        except Exception as e:
            print(f"Warning: Could not add edge {src}->{dest}: {e}")
    
    print(f"✓ Graph initialized with {len(fulfilment_graph.nodes())} nodes and {len(fulfilment_graph.edges())} edges")

# Initialize the graph
initialize_graph()

# Create fulfilment engine if available
if HAS_FULFILMENT:
    try:
        fulfilment_engine = create_sample_fulfilment_engine(inventory, fulfilment_graph)
        print(f"✓ Fulfilment engine created successfully")
    except Exception as e:
        print(f"✗ Failed to create fulfilment engine: {e}")
        fulfilment_engine = None
        HAS_FULFILMENT = False
else:
    fulfilment_engine = None

# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    import traceback
    error_details = traceback.format_exc()
    print(f"500 Error: {error_details}")
    return jsonify({"error": "Internal server error", "message": str(error), "details": error_details}), 500

# ==================== ROOT & HEALTH ====================

@app.route('/')
def home():
    return jsonify({
        "message": "Inventory Management API v3.0",
        "version": "3.0",
        "modules": {
            "inventory": "✓ Active",
            "fulfilment": "✓ Active" if HAS_FULFILMENT else "⚠️ Limited",
            "graph": "✓ Active" if fulfilment_graph.nodes() else "⚠️ Empty"
        },
        "graph_info": {
            "nodes": len(fulfilment_graph.nodes()),
            "edges": len(fulfilment_graph.edges()),
            "nodes_list": fulfilment_graph.nodes()
        },
        "endpoints": {
            "GET /api/products": "List all products",
            "POST /api/products": "Add a product",
            "GET /api/products/search": "Search products",
            "PATCH /api/products/<id>": "Update product",
            "DELETE /api/products/<id>": "Delete product",
            "POST /api/fulfilment/order": "Place new order",
            "GET /api/fulfilment/process": "Process next order",
            "GET /api/fulfilment/stats": "Fulfilment statistics",
            "GET /api/fulfilment/warehouses": "Warehouse inventory",
            "POST /api/delivery/route": "Calculate delivery route",
            "GET /api/graph/data": "Fulfilment graph visualization",
            "GET /api/health": "Health check"
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "Inventory Management API v3.0",
        "inventory_count": len(inventory),
        "fulfilment_active": HAS_FULFILMENT,
        "graph_nodes": len(fulfilment_graph.nodes()),
        "graph_edges": len(fulfilment_graph.edges()),
        "graph_has_nodes": bool(fulfilment_graph.nodes())
    }), 200

# ==================== INVENTORY ENDPOINTS ====================
# [Keep all your inventory endpoints as they are - they're working]
# ... [INVENTORY ENDPOINTS UNCHANGED] ...
# ==================== INVENTORY ENDPOINTS ====================

@app.route('/api/products', methods=['GET'])
def get_all_products():
    """Get all products from inventory"""
    try:
        products = []
        for product_id in inventory:
            product = inventory.get_product(product_id)
            if product:
                products.append({
                    "id": product.product_id,
                    "name": product.name,
                    "price": product.price,
                    "quantity": product.quantity,
                    "category": product.category
                })
        return jsonify({"products": products, "count": len(products)}), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve products", "message": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product to inventory"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No product data provided"}), 400
        # Validate required fields (accept either 'id' or 'product_id')
        pid = data.get('id') or data.get('product_id')
        if not pid:
            return jsonify({"error": "Missing required field: id (or product_id)"}), 400

        for field in ['name', 'price', 'quantity', 'category']:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create product (strong validation lives in Product.__post_init__)
        try:
            product = Product(
                product_id=str(pid),
                name=str(data['name']),
                price=float(data['price']),
                quantity=int(data['quantity']),
                category=str(data['category'])
            )
        except (ValueError, TypeError) as e:
            return jsonify({"error": "Invalid product data", "message": str(e)}), 400
        
        # Add to inventory, handle duplicates/validation
        try:
            inventory.add_product(product)
            try:
                save_inventory(inventory, DEFAULT_DB_FILE)
            except Exception as se:
                print(f"⚠️ Failed to save inventory after add: {se}")
        except ValueError as e:
            return jsonify({"error": "Product could not be added", "message": str(e)}), 409
        except TypeError as e:
            return jsonify({"error": "Product type error", "message": str(e)}), 400

        return jsonify({
            "message": "Product added successfully",
            "product": {
                "id": product.product_id,
                "name": product.name,
                "price": product.price,
                "quantity": product.quantity,
                "category": product.category
            }
        }), 201
    except Exception as e:
        return jsonify({"error": "Failed to add product", "message": str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    try:
        product = inventory.get_product(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        return jsonify({
            "id": product.product_id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "category": product.category
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve product", "message": str(e)}), 500

@app.route('/api/products/<product_id>', methods=['PATCH'])
def update_product(product_id):
    """Update a product"""
    try:
        data = request.get_json()
        product = inventory.get_product(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            product.price = float(data['price'])
        if 'quantity' in data:
            product.quantity = int(data['quantity'])
        if 'category' in data:
            product.category = data['category']
        
        # Persist changes
        try:
            save_inventory(inventory, DEFAULT_DB_FILE)
        except Exception as se:
            print(f"⚠️ Failed to save inventory after update: {se}")

        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.product_id,
                "name": product.name,
                "price": product.price,
                "quantity": product.quantity,
                "category": product.category
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to update product", "message": str(e)}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        # Inventory.remove_product raises KeyError if not found
        inventory.remove_product(product_id)
        try:
            save_inventory(inventory, DEFAULT_DB_FILE)
        except Exception as se:
            print(f"⚠️ Failed to save inventory after delete: {se}")
        return jsonify({"message": f"Product {product_id} deleted successfully"}), 200
    except Exception as e:
        # Handle not-found explicitly
        import traceback
        tb = traceback.format_exc()
        if isinstance(e, KeyError):
            return jsonify({"error": "Product not found", "message": str(e)}), 404
        return jsonify({"error": "Failed to delete product", "message": str(e), "details": tb}), 500

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """Search products by name or category"""
    try:
        query = request.args.get('q', '').lower()
        category = request.args.get('category', '').lower()
        
        results = []
        for product_id in inventory:
            product = inventory.get_product(product_id)
            if product:
                matches_query = query in product.name.lower() or query in product.category.lower()
                matches_category = not category or category == product.category.lower()
                
                if matches_query and matches_category:
                    results.append({
                        "id": product.product_id,
                        "name": product.name,
                        "price": product.price,
                        "quantity": product.quantity,
                        "category": product.category
                    })
        
        return jsonify({"results": results, "count": len(results)}), 200
    except Exception as e:
        return jsonify({"error": "Search failed", "message": str(e)}), 500

# ...existing code...
# ==================== FULFILMENT ENGINE ENDPOINTS ====================

@app.route('/api/fulfilment/warehouses', methods=['GET'])
def get_warehouses():
    """Get all warehouses with inventory data"""
    try:
        if HAS_FULFILMENT and fulfilment_engine:
            # Try to get warehouses from engine
            try:
                warehouses = fulfilment_engine.get_warehouses()
                return jsonify(warehouses), 200
            except:
                # Fallback to mock data
                pass
        
        # Mock data
        return jsonify([
            {"warehouse_id": "main", "name": "Main Warehouse", "total_items": 4500, "unique_products": 8},
            {"warehouse_id": "north", "name": "North Regional", "total_items": 1500, "unique_products": 6},
            {"warehouse_id": "south", "name": "South Regional", "total_items": 1500, "unique_products": 6},
            {"warehouse_id": "east", "name": "East Regional", "total_items": 1500, "unique_products": 6},
            {"warehouse_id": "west", "name": "West Regional", "total_items": 1500, "unique_products": 6}
        ]), 200
    except Exception as e:
        return jsonify({"error": "Failed to get warehouses", "message": str(e)}), 500

@app.route('/api/fulfilment/order', methods=['POST'])
def place_order():
    """Place a new order for fulfilment"""
    try:
        if not HAS_FULFILMENT or not fulfilment_engine:
            return jsonify({"error": "Fulfilment engine not available"}), 503
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No order data provided"}), 400
        
        # Add default order_id if missing
        if 'order_id' not in data:
            from datetime import datetime
            data['order_id'] = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Add default customer_id if missing
        if 'customer_id' not in data:
            data['customer_id'] = "CUST001"
        
        # Build Order object expected by fulfilment engine
        try:
            items = []
            raw_items = data.get('items', [])
            for it in raw_items:
                pid = it.get('product_id') or it.get('id') or it.get('productId')
                qty = int(it.get('quantity', 0))
                ptype_raw = (it.get('product_type') or it.get('type') or 'other').lower()

                # Map to ProductType enum; fallback to OTHER
                try:
                    ptype = ProductType(ptype_raw)
                except Exception:
                    # try to match by value
                    matched = None
                    for v in ProductType:
                        if v.value == ptype_raw:
                            matched = v
                            break
                    ptype = matched or ProductType.OTHER

                items.append(OrderItem(pid, qty, ptype))

            dest = data.get('destination') or data.get('destination_id') or data.get('warehouse')
            urgency_raw = (data.get('urgency') or 'standard').lower()
            try:
                urgency = Urgency(urgency_raw)
            except Exception:
                urgency = Urgency.STANDARD

            order_obj = Order(
                order_id=data['order_id'],
                customer_id=data.get('customer_id', 'CUST001'),
                items=items,
                destination=dest,
                urgency=urgency
            )

            result = fulfilment_engine.place_order(order_obj)

            return jsonify({
                "message": "Order placed successfully",
                "order_id": order_obj.order_id,
                "result": result
            }), 200
        except Exception as e:
            import traceback
            print(f"Order placement error (construction): {traceback.format_exc()}")
            return jsonify({"error": "Invalid order data", "message": str(e)}), 400
        
    except Exception as e:
        import traceback
        print(f"Order placement error: {traceback.format_exc()}")
        return jsonify({"error": "Failed to place order", "message": str(e)}), 500

@app.route('/api/fulfilment/process', methods=['GET'])
def process_order():
    """Process the next order in queue"""
    try:
        if not HAS_FULFILMENT or not fulfilment_engine:
            return jsonify({"error": "Fulfilment engine not available"}), 503
        
        result = fulfilment_engine.process_next_order()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to process order", "message": str(e)}), 500

@app.route('/api/fulfilment/stats', methods=['GET'])
def fulfilment_stats():
    """Get fulfilment engine statistics"""
    try:
        if HAS_FULFILMENT and fulfilment_engine:
            try:
                stats = fulfilment_engine.get_statistics()
                return jsonify(stats), 200
            except:
                # Fallback to basic stats
                pass
        
        return jsonify({
            "fulfilled_orders": 0,
            "failed_orders": 0,
            "pending_orders": 0,
            "total_delivery_distance": 0,
            "warehouse_count": 8,
            "avg_distance_per_order": 0
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to get stats", "message": str(e)}), 500

# ==================== DELIVERY ROUTING ENDPOINTS ====================

@app.route('/api/delivery/route', methods=['POST'])
def calculate_delivery_route():
    """Calculate optimal delivery route using Dijkstra"""
    try:
        print("\n[DEBUG] Route calculation requested")
        data = request.get_json()
        print(f"[DEBUG] Request data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        source = data.get('source')
        destination = data.get('destination')
        product_type = data.get('product_type', 'standard')
        urgency = data.get('urgency', 'standard')
        
        print(f"[DEBUG] Source: {source}, Destination: {destination}")
        
        if not source or not destination:
            return jsonify({"error": "Source and destination required"}), 400
        
        # Check if nodes exist in graph
        nodes = fulfilment_graph.nodes()
        print(f"[DEBUG] Available nodes: {nodes}")
        
        if source not in nodes:
            return jsonify({"error": f"Source node '{source}' not found in graph"}), 404
        
        if destination not in nodes:
            return jsonify({"error": f"Destination node '{destination}' not found in graph"}), 404
        
        # Use the SINGLE graph for all routing
        print(f"[DEBUG] Calculating shortest path from {source} to {destination}")
        distance, path = fulfilment_graph.shortest_path(source, destination)
        print(f"[DEBUG] Result: distance={distance}, path={path}")
        
        if distance == float("inf"):
            return jsonify({"error": "No route available between these nodes"}), 404
        
        # Calculate delivery metrics
        base_time = distance / 60  # hours (assuming 60km/h average)
        base_cost = distance * 0.5  # $0.5 per km
        
        # Adjust for product type
        if product_type == 'furniture':
            base_time *= 1.3
            base_cost *= 1.2
        elif product_type == 'electronics':
            base_cost *= 1.5
        elif product_type == 'food':
            base_cost *= 2.0
        
        # Adjust for urgency
        if urgency == 'express':
            base_time *= 0.6
            base_cost *= 1.5
        elif urgency == 'urgent':
            base_time *= 0.3
            base_cost *= 2.5
        
        return jsonify({
            "source": source,
            "destination": destination,
            "distance": distance,
            "estimated_time": round(base_time, 1),
            "cost": round(base_cost, 2),
            "path": path,
            "product_type": product_type,
            "urgency": urgency,
            "algorithm": "Dijkstra",
            "message": f"Route calculated from {source} to {destination} via {len(path)-2 if len(path)>2 else 0} intermediate nodes"
        }), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Route calculation failed: {error_details}")
        return jsonify({"error": "Route calculation failed", "message": str(e), "details": error_details}), 500

# ==================== GRAPH VISUALIZATION ENDPOINTS ====================

@app.route('/api/graph/data', methods=['GET'])
def get_graph_data():
    """Get data for fulfilment graph visualization"""
    try:
        # Get nodes and edges from the SINGLE graph
        nodes = fulfilment_graph.nodes()
        edges = fulfilment_graph.edges()
        
        print(f"[DEBUG] Graph data: {len(nodes)} nodes, {len(edges)} edges")
        
        # Create visualization data
        graph_data = {
            "nodes": [],
            "edges": [],
            "type": "fulfilment_graph",
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
        
        if not nodes:
            return jsonify(graph_data), 200
        
        # Position nodes in a circle for visualization
        import math
        center_x, center_y = 400, 300
        radius = 200
        
        for i, node in enumerate(nodes):
            angle = (2 * math.pi * i) / len(nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Determine node type
            node_type = "warehouse"
            if "local" in node:
                node_type = "store"
            elif node == "main":
                node_type = "hub"
            
            graph_data["nodes"].append({
                "id": node,
                "label": node,
                "x": x,
                "y": y,
                "type": node_type
            })
        
        # Add edges
        for src, dest, weight in edges:
            graph_data["edges"].append({
                "from": src,
                "to": dest,
                "label": f"{weight}km",
                "weight": weight
            })
        
        return jsonify(graph_data), 200
    except Exception as e:
        import traceback
        print(f"Graph data error: {traceback.format_exc()}")
        return jsonify({"error": "Failed to get graph data", "message": str(e)}), 500

# ==================== SYSTEM STATUS ====================

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get comprehensive system status"""
    return jsonify({
        "system": "Inventory Management System v3.0",
        "status": "operational",
        "components": {
            "inventory": {
                "status": "active",
                "product_count": len(inventory),
                "data_structure": "HashTable + BST"
            },
            "fulfilment": {
                "status": "active" if HAS_FULFILMENT else "disabled",
                "engine": "FulfilmentEngine" if HAS_FULFILMENT else "mock"
            },
            "graph": {
                "status": "active",
                "nodes": len(fulfilment_graph.nodes()),
                "edges": len(fulfilment_graph.edges()),
                "nodes_list": fulfilment_graph.nodes(),
                "algorithm": "Dijkstra",
                "purpose": "Fulfilment routing (single graph)"
            }
        },
        "data_structures_used": [
            "Hash Tables (inventory storage)",
            "Binary Search Trees (price indexing)",
            "Graph (fulfilment routing)",
            "Priority Queues (order scheduling)",
            "Greedy Algorithms (warehouse selection)"
        ]
    }), 200

# ==================== STARTUP ====================

if __name__ == '__main__':
    print("=" * 70)
    print("INVENTORY MANAGEMENT SYSTEM API v3.0")
    print("=" * 70)
    print(f"Fulfilment Engine: {'✓ ACTIVE' if HAS_FULFILMENT else '⚠️ DISABLED'}")
    print(f"Graph: ✓ INITIALIZED")
    print(f"Graph Nodes: {len(fulfilment_graph.nodes())}")
    print(f"Graph Edges: {len(fulfilment_graph.edges())}")
    if fulfilment_graph.nodes():
        print(f"Node List: {', '.join(fulfilment_graph.nodes())}")
    print("\nKey DSA Components:")
    print("  • Hash Tables - Inventory storage")
    print("  • BST - Price indexing and range queries")
    print("  • Graph + Dijkstra - Optimal routing")
    print("  • Priority Queues - Order scheduling")
    print("  • Greedy Algorithms - Warehouse selection")
    print("\nAvailable endpoints:")
    print("  /api/products           - Inventory management")
    print("  /api/fulfilment/*       - Order fulfilment")
    print("  POST /api/delivery/route - Delivery routing")
    print("  /api/graph/data         - Fulfilment graph")
    print("  /api/system/status      - System overview")
    print("\nStarting server on http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    app.run(debug=True, port=5001)