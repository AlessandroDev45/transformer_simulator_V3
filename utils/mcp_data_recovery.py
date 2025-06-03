"""
MCP Data Recovery Utility
Fixes the data synchronization problem where test stores have complete data
but transformer-inputs-store (authoritative source) has incomplete data.
"""

import logging
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)

def extract_complete_transformer_data(app) -> Optional[Dict[str, Any]]:
    """
    Extracts complete transformer data from test stores that have nested transformer_data.
    
    Args:
        app: Dash application instance with MCP
        
    Returns:
        Dict containing the most complete transformer data found, or None if no data found
    """
    if not app.mcp:
        log.error("[Data Recovery] MCP not available")
        return None
    
    # List of stores that might contain complete data in transformer_data structure
    test_stores = [
        "losses-store",
        "impulse-store", 
        "dieletric-analysis-store",
        "applied-voltage-store",
        "short-circuit-store",
        "temperature-rise-store",
        "comprehensive-analysis-store"
    ]
    
    most_complete_data = None
    max_fields = 0
    source_store = None
    
    log.info("[Data Recovery] Searching for complete transformer data in test stores...")
    
    for store_name in test_stores:
        store_data = app.mcp.get_data(store_name)
        
        if store_data and isinstance(store_data, dict):
            # Check if this store has transformer_data
            transformer_data = store_data.get("transformer_data")
            
            if transformer_data and isinstance(transformer_data, dict):
                # Count non-null fields to find the most complete data
                non_null_fields = sum(1 for v in transformer_data.values() if v is not None)
                
                log.info(f"[Data Recovery] Store {store_name} has {non_null_fields} non-null fields")
                
                if non_null_fields > max_fields:
                    max_fields = non_null_fields
                    most_complete_data = transformer_data.copy()
                    source_store = store_name
    
    if most_complete_data:
        log.info(f"[Data Recovery] Most complete data found in {source_store} with {max_fields} fields")
        
        # Log a sample of the data found
        sample_fields = ["potencia_mva", "tensao_at", "tensao_bt", "tipo_transformador"]
        sample_data = {k: most_complete_data.get(k) for k in sample_fields}
        log.info(f"[Data Recovery] Sample data: {sample_data}")
        
        return most_complete_data
    else:
        log.warning("[Data Recovery] No complete transformer data found in test stores")
        return None


def fix_mcp_data_synchronization(app) -> bool:
    """
    Fixes the MCP data synchronization by:
    1. Extracting complete data from test stores
    2. Populating transformer-inputs-store as authoritative source
    3. Re-propagating data correctly to all test stores
    
    Args:
        app: Dash application instance with MCP
        
    Returns:
        bool: True if synchronization was fixed successfully
    """
    if not app.mcp:
        log.error("[Data Recovery] MCP not available for synchronization fix")
        return False
    
    log.info("[Data Recovery] Starting MCP data synchronization fix...")
    
    # Step 1: Extract complete transformer data
    complete_data = extract_complete_transformer_data(app)
    
    if not complete_data:
        log.error("[Data Recovery] Cannot fix synchronization: no complete data found")
        return False
    
    # Step 2: Update transformer-inputs-store with complete data
    log.info("[Data Recovery] Updating transformer-inputs-store with complete data...")
    
    try:
        # Set the complete data in the authoritative source
        app.mcp.set_data("transformer-inputs-store", complete_data)
        log.info("[Data Recovery] transformer-inputs-store updated with complete data")
        
        # Verify the update worked
        updated_data = app.mcp.get_data("transformer-inputs-store")
        non_null_count = sum(1 for v in updated_data.values() if v is not None) if updated_data else 0
        log.info(f"[Data Recovery] Verification: transformer-inputs-store now has {non_null_count} non-null fields")
        
    except Exception as e:
        log.error(f"[Data Recovery] Failed to update transformer-inputs-store: {e}")
        return False
    
    # Step 3: Force save to disk to persist the fix
    try:
        app.mcp.save_to_disk(force=True)
        log.info("[Data Recovery] MCP state saved to disk")
    except Exception as e:
        log.warning(f"[Data Recovery] Failed to save MCP state to disk: {e}")
    
    # Step 4: Re-propagate data from authoritative source to all test stores
    log.info("[Data Recovery] Re-propagating data from authoritative source to test stores...")
    
    try:
        from utils.mcp_persistence import ensure_mcp_data_propagation
        
        # List of all test stores to propagate to
        target_stores = [
            "losses-store",
            "impulse-store",
            "dieletric-analysis-store", 
            "applied-voltage-store",
            "induced-voltage-store",
            "short-circuit-store",
            "temperature-rise-store",
            "comprehensive-analysis-store"
        ]
        
        # Propagate data from transformer-inputs-store (authoritative) to all test stores
        propagation_results = ensure_mcp_data_propagation(
            app, "transformer-inputs-store", target_stores
        )
        
        # Log results
        successful_propagations = sum(1 for success in propagation_results.values() if success)
        total_stores = len(target_stores)
        
        log.info(f"[Data Recovery] Propagation completed: {successful_propagations}/{total_stores} stores updated")
        
        for store, success in propagation_results.items():
            if success:
                log.info(f"[Data Recovery] ✓ Data propagated to {store}")
            else:
                log.warning(f"[Data Recovery] ✗ Failed to propagate data to {store}")
        
        # Consider it successful if most stores were updated
        success_rate = successful_propagations / total_stores
        return success_rate >= 0.7  # 70% success rate threshold
        
    except Exception as e:
        log.error(f"[Data Recovery] Failed to propagate data: {e}")
        return False


def verify_data_synchronization(app) -> Dict[str, Any]:
    """
    Verifies that MCP data synchronization is working correctly.
    
    Args:
        app: Dash application instance with MCP
        
    Returns:
        Dict containing verification results
    """
    if not app.mcp:
        return {"status": "error", "message": "MCP not available"}
    
    log.info("[Data Recovery] Verifying data synchronization...")
    
    result = {
        "status": "unknown",
        "transformer_inputs_complete": False,
        "test_stores_synchronized": False,
        "details": {}
    }
    
    # Check transformer-inputs-store completeness
    transformer_data = app.mcp.get_data("transformer-inputs-store")
    if transformer_data:
        non_null_fields = sum(1 for v in transformer_data.values() if v is not None)
        essential_fields = ["potencia_mva", "tensao_at", "tensao_bt", "tipo_transformador"]
        essential_complete = all(transformer_data.get(field) is not None for field in essential_fields)
        
        result["details"]["transformer_inputs"] = {
            "total_fields": len(transformer_data),
            "non_null_fields": non_null_fields,
            "essential_complete": essential_complete
        }
        
        result["transformer_inputs_complete"] = essential_complete and non_null_fields > 20
    
    # Check test stores synchronization
    test_stores = [
        "losses-store", "impulse-store", "dieletric-analysis-store",
        "applied-voltage-store", "short-circuit-store", "temperature-rise-store"
    ]
    
    synchronized_stores = 0
    total_test_stores = len(test_stores)
    
    for store_name in test_stores:
        store_data = app.mcp.get_data(store_name)
        if store_data and "transformer_data" in store_data:
            transformer_data_in_store = store_data["transformer_data"]
            if transformer_data_in_store and isinstance(transformer_data_in_store, dict):
                non_null_in_store = sum(1 for v in transformer_data_in_store.values() if v is not None)
                if non_null_in_store > 10:  # Reasonable threshold
                    synchronized_stores += 1
    
    result["details"]["test_stores"] = {
        "total_stores": total_test_stores,
        "synchronized_stores": synchronized_stores,
        "synchronization_rate": synchronized_stores / total_test_stores if total_test_stores > 0 else 0
    }
    
    result["test_stores_synchronized"] = synchronized_stores >= total_test_stores * 0.8  # 80% threshold
    
    # Overall status
    if result["transformer_inputs_complete"] and result["test_stores_synchronized"]:
        result["status"] = "ok"
    elif result["transformer_inputs_complete"] or result["test_stores_synchronized"]:
        result["status"] = "partial"
    else:
        result["status"] = "error"
    
    log.info(f"[Data Recovery] Verification result: {result['status']}")
    return result


def run_complete_mcp_recovery(app) -> Dict[str, Any]:
    """
    Runs a complete MCP data recovery process.
    
    Args:
        app: Dash application instance with MCP
        
    Returns:
        Dict containing recovery results and status
    """
    log.info("[Data Recovery] Starting complete MCP data recovery...")
    
    result = {
        "status": "unknown",
        "steps_completed": [],
        "errors": [],
        "verification": {}
    }
    
    try:
        # Step 1: Initial verification
        initial_verification = verify_data_synchronization(app)
        log.info(f"[Data Recovery] Initial status: {initial_verification['status']}")
        
        if initial_verification["status"] == "ok":
            result["status"] = "ok"
            result["steps_completed"].append("No recovery needed - data already synchronized")
            result["verification"] = initial_verification
            return result
        
        # Step 2: Attempt data synchronization fix
        fix_successful = fix_mcp_data_synchronization(app)
        result["steps_completed"].append("Data synchronization fix attempted")
        
        if not fix_successful:
            result["errors"].append("Data synchronization fix failed")
            result["status"] = "error"
            return result
        
        result["steps_completed"].append("Data synchronization fix completed")
        
        # Step 3: Final verification
        final_verification = verify_data_synchronization(app)
        result["verification"] = final_verification
        
        if final_verification["status"] == "ok":
            result["status"] = "ok"
            result["steps_completed"].append("Recovery successful - data synchronized")
        elif final_verification["status"] == "partial":
            result["status"] = "partial"
            result["steps_completed"].append("Recovery partially successful")
        else:
            result["status"] = "error"
            result["errors"].append("Recovery failed - data still not synchronized")
        
    except Exception as e:
        log.error(f"[Data Recovery] Exception during recovery: {e}")
        result["status"] = "error"
        result["errors"].append(f"Exception: {str(e)}")
    
    log.info(f"[Data Recovery] Complete recovery finished with status: {result['status']}")
    return result
