#!/usr/bin/env python3
"""
Ingetrans Data Propagation System
Replicates validated Ingetrans parameters across all databases, repositories, and applications
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IngetransDataPropagator:
    """Propagates Ingetrans data across systems"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize propagator"""
        if repo_root is None:
            repo_root = Path(__file__).parent.parent
        self.repo_root = repo_root
        self.propagation_log = []
        self.propagated_files = []
        self.failed_operations = []
    
    def load_ingetrans_config(self) -> Dict:
        """Load the master Ingetrans configuration"""
        config_file = self.repo_root / 'config' / 'ingetrans_parameters.json'
        logger.info(f"Loading master configuration from: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("Master configuration loaded successfully")
            return config
        except FileNotFoundError:
            error_msg = f"Master configuration file not found: {config_file}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return {}
    
    def propagate_to_data_directory(self, config: Dict) -> bool:
        """Propagate data to the data directory"""
        logger.info("Propagating data to data directory...")
        
        data_dir = self.repo_root / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create ingetrans_parameters.json in data directory
        dest_file = data_dir / 'ingetrans_parameters.json'
        try:
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Propagated to: {dest_file}")
            self.propagated_files.append(str(dest_file))
            return True
        except Exception as e:
            error_msg = f"Failed to propagate to data directory: {str(e)}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return False
    
    def propagate_to_ai_factory_v2(self, config: Dict) -> bool:
        """Propagate data to ai-factory-v2 module"""
        logger.info("Propagating data to ai-factory-v2...")
        
        ai_factory_dir = self.repo_root / 'ai-factory-v2' / 'config'
        ai_factory_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = ai_factory_dir / 'ingetrans_parameters.json'
        try:
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Propagated to: {dest_file}")
            self.propagated_files.append(str(dest_file))
            return True
        except Exception as e:
            error_msg = f"Failed to propagate to ai-factory-v2: {str(e)}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return False
    
    def propagate_to_api(self, config: Dict) -> bool:
        """Propagate data to API module"""
        logger.info("Propagating data to API module...")
        
        api_dir = self.repo_root / 'api' / 'config'
        api_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = api_dir / 'ingetrans_parameters.json'
        try:
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Propagated to: {dest_file}")
            self.propagated_files.append(str(dest_file))
            return True
        except Exception as e:
            error_msg = f"Failed to propagate to API module: {str(e)}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return False
    
    def propagate_to_orchestrator(self, config: Dict) -> bool:
        """Propagate data to orchestrator"""
        logger.info("Propagating data to orchestrator...")
        
        orch_dir = self.repo_root / 'orchestrator' / 'config'
        orch_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = orch_dir / 'ingetrans_parameters.json'
        try:
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Propagated to: {dest_file}")
            self.propagated_files.append(str(dest_file))
            return True
        except Exception as e:
            error_msg = f"Failed to propagate to orchestrator: {str(e)}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return False
    
    def propagate_to_agents(self, config: Dict) -> bool:
        """Propagate data to agents directory"""
        logger.info("Propagating data to agents...")
        
        agents_dir = self.repo_root / 'agents' / 'config'
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = agents_dir / 'ingetrans_parameters.json'
        try:
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Propagated to: {dest_file}")
            self.propagated_files.append(str(dest_file))
            return True
        except Exception as e:
            error_msg = f"Failed to propagate to agents: {str(e)}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return False
    
    def propagate_to_config_registry(self, config: Dict) -> bool:
        """Add Ingetrans to central config registry"""
        logger.info("Updating central configuration registry...")
        
        registry_file = self.repo_root / 'config' / 'systems_registry.json'
        
        try:
            # Load existing registry or create new one
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            else:
                registry = {'systems': []}
            
            # Check if Ingetrans already registered
            ingetrans_entry = {
                'system_name': 'Ingetrans',
                'system_type': 'Rail-guided transfer carriage',
                'version': config.get('version', '1.0.0'),
                'validation_status': config.get('validation_status', 'validated'),
                'approval_status': config.get('metadata', {}).get('approval_status', 'approved'),
                'last_updated': datetime.now().isoformat(),
                'config_file': 'config/ingetrans_parameters.json'
            }
            
            # Remove old entry if exists
            registry['systems'] = [s for s in registry.get('systems', []) 
                                  if s.get('system_name') != 'Ingetrans']
            
            # Add new entry
            registry['systems'].append(ingetrans_entry)
            
            # Save updated registry
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated registry: {registry_file}")
            self.propagated_files.append(str(registry_file))
            return True
        except Exception as e:
            error_msg = f"Failed to update configuration registry: {str(e)}"
            logger.error(error_msg)
            self.failed_operations.append(error_msg)
            return False
    
    def copy_schema_to_database_scripts(self) -> bool:
        """Copy SQL schema to database scripts directory"""
        logger.info("Copying database schema...")
        
        source_schema = self.repo_root / 'ai-factory-v2' / 'db' / 'ingetrans_schema.sql'
        
        # Copy to multiple locations
        target_locations = [
            self.repo_root / 'ai-factory-v2' / 'db' / 'migrations' / 'ingetrans_schema.sql',
            self.repo_root / 'api' / 'db' / 'ingetrans_schema.sql',
            self.repo_root / 'orchestrator' / 'db' / 'ingetrans_schema.sql'
        ]
        
        success = True
        for target in target_locations:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_schema, target)
                logger.info(f"Copied schema to: {target}")
                self.propagated_files.append(str(target))
            except Exception as e:
                error_msg = f"Failed to copy schema to {target}: {str(e)}"
                logger.error(error_msg)
                self.failed_operations.append(error_msg)
                success = False
        
        return success
    
    def create_propagation_manifest(self) -> bool:
        """Create manifest of all propagated files"""
        logger.info("Creating propagation manifest...")
        
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'system': 'Ingetrans',
            'operation': 'data_propagation',
            'propagated_files': self.propagated_files,
            'failed_operations': self.failed_operations,
            'status': 'success' if not self.failed_operations else 'partial_failure',
            'total_propagated': len(self.propagated_files),
            'total_failed': len(self.failed_operations)
        }
        
        manifest_file = self.repo_root / 'data' / 'ingetrans_propagation_manifest.json'
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            logger.info(f"Manifest saved to: {manifest_file}")
            return True
        except Exception as e:
            error_msg = f"Failed to create propagation manifest: {str(e)}"
            logger.error(error_msg)
            return False
    
    def propagate_all(self) -> bool:
        """Execute complete propagation of Ingetrans data"""
        logger.info("=" * 70)
        logger.info("STARTING INGETRANS DATA PROPAGATION")
        logger.info("=" * 70)
        
        # Load master configuration
        config = self.load_ingetrans_config()
        if not config:
            logger.error("Failed to load master configuration")
            return False
        
        # Propagate to all locations
        all_success = True
        all_success &= self.propagate_to_data_directory(config)
        all_success &= self.propagate_to_ai_factory_v2(config)
        all_success &= self.propagate_to_api(config)
        all_success &= self.propagate_to_orchestrator(config)
        all_success &= self.propagate_to_agents(config)
        all_success &= self.propagate_to_config_registry(config)
        all_success &= self.copy_schema_to_database_scripts()
        
        # Create manifest
        self.create_propagation_manifest()
        
        logger.info("=" * 70)
        logger.info("PROPAGATION COMPLETE")
        logger.info("=" * 70)
        
        return all_success


def main():
    """Main entry point"""
    propagator = IngetransDataPropagator()
    success = propagator.propagate_all()
    
    # Print summary
    print("\n" + "="*70)
    print("INGETRANS DATA PROPAGATION REPORT")
    print("="*70)
    print(f"Status: {'SUCCESS' if success else 'PARTIAL FAILURE'}")
    print(f"Files propagated: {len(propagator.propagated_files)}")
    print(f"Failed operations: {len(propagator.failed_operations)}")
    
    if propagator.propagated_files:
        print("\nPropagated Files:")
        for file in propagator.propagated_files:
            print(f"  [OK] {file}")
    
    if propagator.failed_operations:
        print("\nFailed Operations:")
        for error in propagator.failed_operations:
            print(f"  [ERROR] {error}")
    
    print("\n" + "="*70)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
