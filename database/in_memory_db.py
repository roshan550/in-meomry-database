import time
from data_structures.btree import BPlusTree
from data_structures.avl_tree import AVLTree
from data_structures.skip_list import SkipList
from database.wal import WAL
from visualizer.data_structure_viz import DataStructureVisualizer
import copy

class InMemoryDB:
    def __init__(self):
        self.btree = BPlusTree(order=4)
        self.avl_tree = AVLTree()
        self.skip_list = SkipList()
        self.wal = WAL()
        self.current_structure = "btree"
        self.performance_metrics = {
            "btree": {"insert": [], "search": [], "update": [], "delete": []},
            "avl": {"insert": [], "search": [], "update": [], "delete": []},
            "skip_list": {"insert": [], "search": [], "update": [], "delete": []}
        }
        self.used_structures = set(["btree"])  # Start with btree as it's the default
        self.data = {}
        self.visualizer = DataStructureVisualizer()
        self._recover_from_wal()

    def _recover_from_wal(self):
        """Recover data from WAL file on startup"""
        operations = self.wal.recover()
        for operation in operations:
            if operation["operation"] == "insert" or operation["operation"] == "update":
                self.data[operation["key"]] = operation["value"]
            elif operation["operation"] == "delete" and operation["key"] in self.data:
                del self.data[operation["key"]]
        self._sync_data()

    def set_structure(self, structure_name):
        """Change the current data structure with visualization"""
        if structure_name == self.current_structure:
            return None, None

        # Get current structure object
        source_structure = self._get_current_structure()

        # Store old structure type
        old_structure = self.current_structure

        # Update current structure
        self.current_structure = structure_name
        
        # Add to used structures immediately
        self.used_structures.add(structure_name)

        # Sync data to new structure
        self._sync_data()

        # Get new structure object
        target_structure = self._get_current_structure()

        # Create transition visualization
        return self.visualizer.create_transition_animation(
            source_structure, target_structure,
            old_structure, structure_name
        )

    def _get_current_structure(self):
        """Get the current structure object"""
        if self.current_structure == "btree":
            return self.btree
        elif self.current_structure == "avl":
            return self.avl_tree
        return self.skip_list

    def get_current_visualization(self):
        """Get visualization of current structure"""
        return self.visualizer.visualize_structure(
            self.current_structure,
            self._get_current_structure(),
            "Current Structure"
        )

    def _sync_data(self):
        """Ensure all data is present in all structures"""
        if self.current_structure == "btree":
            self.btree = BPlusTree(order=4)
        elif self.current_structure == "avl":
            self.avl_tree = AVLTree()
        else:
            self.skip_list = SkipList()

        for key, value in self.data.items():
            if self.current_structure == "btree":
                self.btree.insert(key, value)
            elif self.current_structure == "avl":
                self.avl_tree.insert(key, value)
            else:
                self.skip_list.insert(key, value)

    def insert(self, key, value):
        try:
            start_time = time.time()
            # Convert key to string if it isn't already
            # Always convert key to string
            str_key = str(key)
            # Convert value to string if it's not already
            str_value = str(value) if not isinstance(value, str) else value
            self.data[str_key] = str_value

            if self.current_structure == "btree":
                self.btree.insert(str_key, str_value)
            elif self.current_structure == "avl":
                self.avl_tree.insert(str_key, str_value)
            else:
                self.skip_list.insert(str_key, str_value)

            end_time = time.time()
            # Add to used structures set to track which structures have been used
            self.used_structures.add(self.current_structure)
            # Record performance metric
            execution_time = (end_time - start_time) * 1000
            self.performance_metrics[self.current_structure]["insert"].append(execution_time)
            print(f"INSERT: Structure: {self.current_structure}, Time: {execution_time:.3f}ms, Used structures: {self.used_structures}")
            self.wal.log_operation("insert", key, value)
        except Exception as e:
            print(f"Error in insert operation for key {key}: {e}")
            raise

    def update(self, key, value):
        """Update an existing key with a new value"""
        str_key = str(key)
        if str_key not in self.data:
            return False

        try:
            start_time = time.time()
            # Convert value to string if it's not already
            str_value = str(value) if not isinstance(value, str) else value
            self.data[str_key] = str_value

            if self.current_structure == "btree":
                self.btree.insert(key, value)  # B+ Tree insert handles updates
            elif self.current_structure == "avl":
                self.avl_tree.insert(key, value)  # AVL insert handles updates
            else:
                self.skip_list.insert(key, value)  # Skip List insert handles updates

            end_time = time.time()
            # Add to used structures set
            self.used_structures.add(self.current_structure)
            # Record performance metric
            execution_time = (end_time - start_time) * 1000
            self.performance_metrics[self.current_structure]["update"].append(execution_time)
            print(f"UPDATE: Structure: {self.current_structure}, Time: {execution_time:.3f}ms, Used structures: {self.used_structures}")
            self.wal.log_operation("update", key, value)
            return True
        except Exception as e:
            print(f"Error in update operation for key {key}: {e}")
            return False

    def delete(self, key):
        """Delete a key-value pair from the database"""
        # Always convert key to string for consistent handling
        str_key = str(key)
        if str_key not in self.data:
            return False

        try:
            start_time = time.time()
            del self.data[str_key]
            self._sync_data()  # Rebuild current structure without the deleted key

            end_time = time.time()
            # Add to used structures set
            self.used_structures.add(self.current_structure)
            # Record performance metric
            execution_time = (end_time - start_time) * 1000
            self.performance_metrics[self.current_structure]["delete"].append(execution_time)
            print(f"DELETE: Structure: {self.current_structure}, Time: {execution_time:.3f}ms, Used structures: {self.used_structures}")
            self.wal.log_operation("delete", key, None)
            return True
        except Exception as e:
            print(f"Error in delete operation for key {key}: {e}")
            return False

    def search(self, key):
        result = None
        try:
            start_time = time.time()
            # Always convert key to string for consistent searching
            str_key = str(key)

            if self.current_structure == "btree":
                result = self.btree.search(str_key)
            elif self.current_structure == "avl":
                result = self.avl_tree.search(str_key)
            else:
                result = self.skip_list.search(str_key)

            end_time = time.time()
            # Add to used structures set
            self.used_structures.add(self.current_structure)
            # Record performance metric
            execution_time = (end_time - start_time) * 1000
            self.performance_metrics[self.current_structure]["search"].append(execution_time)
            print(f"SEARCH: Structure: {self.current_structure}, Time: {execution_time:.3f}ms, Used structures: {self.used_structures}")
        except Exception as e:
            print(f"Error in search operation for key {key}: {e}")

        return result

    def get_performance_metrics(self):
        """
        Get the current performance metrics for all structures.
        Returns a deep copy to prevent any reference issues.
        """
        # Ensure we're tracking metrics for all structures that have been used
        for structure in self.used_structures:
            if structure not in self.performance_metrics:
                self.performance_metrics[structure] = {"insert": [], "search": [], "update": [], "delete": []}
        
        # Debug - print current metrics when accessed
        for structure in self.performance_metrics:
            if structure in self.used_structures:
                metrics = self.performance_metrics[structure]
                op_counts = {op: len(times) for op, times in metrics.items()}
                print(f"Structure {structure} metrics counts: {op_counts}")
        
        # Return a deep copy to prevent reference issues
        return copy.deepcopy(self.performance_metrics)

    def get_performance_summary(self):
        """Calculate and return performance summary for each structure"""
        print(f"Calculating performance summary. Used structures: {self.used_structures}")
        summary = {}
        structure_names = {
            "btree": "B+ Tree",
            "avl": "AVL Tree",
            "skip_list": "Skip List"
        }
        
        # Recalculate metrics if there's no data
        if not any(structure in self.used_structures for structure in self.performance_metrics):
            print("No structures have been used yet")
            return {}
        
        for structure in self.performance_metrics:
            # Only process structures that have been used
            if structure in self.used_structures:
                metrics = self.performance_metrics[structure]
                print(f"Processing structure {structure}")
                
                # Skip structures with no operations performed
                has_operations = any(len(metrics[op]) > 0 for op in metrics)
                if not has_operations:
                    print(f"  Skipping {structure} - no operations")
                    continue

                # Calculate averages for all operations with proper error handling
                try:
                    avg_insert = sum(metrics["insert"]) / len(metrics["insert"]) if metrics["insert"] else 0
                except Exception as e:
                    print(f"Error calculating insert average: {e}")
                    avg_insert = 0
                    
                try:
                    avg_search = sum(metrics["search"]) / len(metrics["search"]) if metrics["search"] else 0
                except Exception as e:
                    print(f"Error calculating search average: {e}")
                    avg_search = 0
                    
                try:
                    avg_update = sum(metrics["update"]) / len(metrics["update"]) if metrics["update"] else 0
                except Exception as e:
                    print(f"Error calculating update average: {e}")
                    avg_update = 0
                    
                try:
                    avg_delete = sum(metrics["delete"]) / len(metrics["delete"]) if metrics["delete"] else 0
                except Exception as e:
                    print(f"Error calculating delete average: {e}")
                    avg_delete = 0
                
                print(f"  {structure} insert operations: {len(metrics['insert'])}, avg: {avg_insert:.3f}ms")
                print(f"  {structure} search operations: {len(metrics['search'])}, avg: {avg_search:.3f}ms")
                print(f"  {structure} update operations: {len(metrics['update'])}, avg: {avg_update:.3f}ms")
                print(f"  {structure} delete operations: {len(metrics['delete'])}, avg: {avg_delete:.3f}ms")
                
                # Count how many operations have data
                operation_values = [avg_insert, avg_search, avg_update, avg_delete]
                op_count = sum(1 for op in operation_values if op > 0)
                
                # Calculate overall average only using operations that have been performed
                try:
                    overall_avg = sum(op for op in operation_values if op > 0) / op_count if op_count > 0 else 0
                except Exception as e:
                    print(f"Error calculating overall average: {e}")
                    overall_avg = 0
                    
                print(f"  {structure} overall average: {overall_avg:.3f}ms")

                summary[structure] = {
                    "name": structure_names[structure],
                    "avg_insert": avg_insert,
                    "avg_search": avg_search,
                    "avg_update": avg_update,
                    "avg_delete": avg_delete,
                    "overall_avg": overall_avg
                }

        print(f"Final summary: {summary}")
        return summary

    def get_best_structure(self):
        """Determine the best performing structure based on metrics"""
        # Check if all data structures have been used
        all_structures = {"btree", "avl", "skip_list"}
        
        # Only return a result if all structures have been used
        if not all_structures.issubset(self.used_structures):
            print(f"Not all structures tested yet. Used: {self.used_structures}, Required: {all_structures}")
            return None
        
        # Get performance summary
        summary = self.get_performance_summary()
        
        if len(summary) < 3:  # Must have data for all 3 structures
            print(f"Not enough structures with performance data. Found: {len(summary)}, Expected: 3")
            return None

        # Find structures with performance data (at least one operation recorded)
        structures_with_data = []
        for name, stats in summary.items():
            # At least one operation type should have data
            if stats["avg_insert"] > 0 or stats["avg_search"] > 0 or stats["avg_update"] > 0 or stats["avg_delete"] > 0:
                structures_with_data.append((name, stats))
        
        if len(structures_with_data) < 3:  # Need at least some data for all structures
            print(f"Not all structures have performance data. Found: {len(structures_with_data)}, Expected: 3")
            return None
        
        # Find the best structure (lowest overall average)
        best_structure = min(structures_with_data, key=lambda x: x[1]["overall_avg"] if x[1]["overall_avg"] > 0 else float('inf'))
        print(f"Best structure identified: {best_structure[1]['name']} with avg {best_structure[1]['overall_avg']:.3f}ms")
        return best_structure[1]["name"]

    def get_best_search_structure(self):
        """Determine the best performing structure specifically for search operations"""
        # Check if all data structures have been used for searching
        all_structures = {"btree", "avl", "skip_list"}
        
        # Track which structures have search operations
        structures_with_search = set()
        for structure in all_structures:
            if structure in self.performance_metrics and len(self.performance_metrics[structure]["search"]) > 0:
                structures_with_search.add(structure)
        
        # Only return a result if all structures have been used for searching
        if structures_with_search != all_structures:
            missing = all_structures - structures_with_search
            print(f"Not all structures tested for search. Missing: {missing}")
            return None
        
        # Calculate average search time for each structure
        search_performance = {}
        for structure in all_structures:
            search_times = self.performance_metrics[structure]["search"]
            if search_times:
                avg_search_time = sum(search_times) / len(search_times)
                search_performance[structure] = {
                    "name": {"btree": "B+ Tree", "avl": "AVL Tree", "skip_list": "Skip List"}[structure],
                    "avg_search_time": avg_search_time
                }
        
        # Find the best structure (lowest average search time)
        if search_performance:
            best_structure = min(search_performance.items(), key=lambda x: x[1]["avg_search_time"])
            print(f"Best search structure: {best_structure[1]['name']} with avg time {best_structure[1]['avg_search_time']:.3f}ms")
            return best_structure[1]["name"]
        
        return None

    def get_all_data(self):
        """Return all key-value pairs in the database"""
        # Create a sorted list of tuples (key, value) for easier display
        # Convert numeric keys to strings for consistent sorting
        sorted_data = sorted(self.data.items(), key=lambda x: str(x[0]))
        return sorted_data

    def clear(self):
        """Clear all data from the database"""
        # Clear main data structure
        self.data.clear()
        
        # Reset all data structures
        self.btree = BPlusTree(order=4)
        self.avl_tree = AVLTree()
        self.skip_list = SkipList()
        
        # Reset performance metrics
        self.performance_metrics = {
            "btree": {"insert": [], "search": [], "update": [], "delete": []},
            "avl": {"insert": [], "search": [], "update": [], "delete": []},
            "skip_list": {"insert": [], "search": [], "update": [], "delete": []}
        }
        
        # Reset WAL by recreating it and clearing the file
        self.wal = WAL()
        try:
            with open(self.wal.filename, 'w') as f:
                f.truncate(0)  # Clear the file contents
        except Exception as e:
            print(f"Error clearing WAL file: {e}")
            
        # Log the clear operation in the fresh WAL
        self.wal.log_operation("clear", None, None)
