#!/usr/bin/env python3
"""
Ingetrans Data Validation Module
Validates all Ingetrans technical parameters across databases, repositories, and applications
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IngetransDataValidator:
    """Validates Ingetrans system parameters"""
    
    # Expected parameter specifications
    EXPECTED_PARAMETERS = {
        'transfer_speed': {
            'unit': 'm/min',
            'min': 80,
            'max': 100,
            'type': 'numeric_range'
        },
        'track_speed': {
            'unit': 'm/min',
            'min': 12,
            'max': 19,
            'type': 'numeric_range'
        },
        'acceleration_deceleration': {
            'unit': 'seconds',
            'value': 1.5,
            'type': 'numeric'
        },
        'pickup_dropoff': {
            'unit': 'seconds per interface',
            'value': 6,
            'type': 'numeric'
        },
        'reel_diameter': {
            'unit': 'mm',
            'max': 1500,
            'type': 'numeric'
        },
        'reel_width_length': {
            'unit': 'mm',
            'max': 2800,
            'type': 'numeric'
        },
        'reel_weight': {
            'unit': 'kg',
            'max': 3500,
            'type': 'numeric'
        }
    }
    
    REQUIRED_SAFETY_COMPONENTS = [
        'Safety PLC functions',
        'Area scanners',
        'Interlocks',
        'Emergency stops',
        'Protected access'
    ]
    
    REQUIRED_CONTROL_SPECIFICATIONS = {
        'architecture': 'Industrial PLC/HMI architecture',
        'communication': 'PROFINET/industrial communications'
    }
    
    def __init__(self, data_dir: Path = None):
        """Initialize validator with data directory"""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / 'config'
        self.data_dir = data_dir
        self.validation_results = []
        self.errors = []
        self.warnings = []
    
    def validate_json_file(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Validate Ingetrans JSON configuration file"""
        logger.info(f"Validating JSON file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            error_msg = f"Configuration file not found: {file_path}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False, {}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {file_path}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False, {}
        
        # Validate required top-level keys
        required_keys = ['system_name', 'parameters', 'metadata']
        for key in required_keys:
            if key not in data:
                warning = f"Missing recommended key: {key}"
                logger.warning(warning)
                self.warnings.append(warning)
        
        # Validate system name
        if data.get('system_name') != 'Ingetrans':
            warning = f"Expected system_name='Ingetrans', got '{data.get('system_name')}'"
            logger.warning(warning)
            self.warnings.append(warning)
        
        # Validate parameters
        if 'parameters' in data:
            params_valid, param_results = self._validate_parameters(data['parameters'])
            if not params_valid:
                return False, {'validation': 'failed', 'details': param_results}
        
        # Validate metadata
        if 'metadata' in data:
            meta_valid, meta_results = self._validate_metadata(data['metadata'])
            if not meta_valid:
                return False, {'validation': 'failed', 'details': meta_results}
        
        logger.info("JSON file validation passed")
        return True, {'validation': 'passed', 'file': str(file_path)}
    
    def _validate_parameters(self, parameters: Dict) -> Tuple[bool, Dict]:
        """Validate parameter specifications"""
        logger.info("Validating parameters...")
        issues = []
        
        # Check transfer_speed
        if 'transfer_speed' in parameters:
            ts = parameters['transfer_speed']
            if ts.get('min_value') != 80:
                issues.append(f"transfer_speed.min_value: expected 80, got {ts.get('min_value')}")
            if ts.get('max_value') != 100:
                issues.append(f"transfer_speed.max_value: expected 100, got {ts.get('max_value')}")
            if ts.get('unit') != 'm/min':
                issues.append(f"transfer_speed.unit: expected 'm/min', got '{ts.get('unit')}'")
        else:
            issues.append("Missing transfer_speed parameter")
        
        # Check track_speed
        if 'track_speed' in parameters:
            ts = parameters['track_speed']
            if ts.get('min_value') != 12:
                issues.append(f"track_speed.min_value: expected 12, got {ts.get('min_value')}")
            if ts.get('max_value') != 19:
                issues.append(f"track_speed.max_value: expected 19, got {ts.get('max_value')}")
            if ts.get('unit') != 'm/min':
                issues.append(f"track_speed.unit: expected 'm/min', got '{ts.get('unit')}'")
        else:
            issues.append("Missing track_speed parameter")
        
        # Check acceleration_deceleration
        if 'acceleration_deceleration' in parameters:
            ad = parameters['acceleration_deceleration']
            if ad.get('value') != 1.5:
                issues.append(f"acceleration_deceleration.value: expected 1.5, got {ad.get('value')}")
            if ad.get('unit') != 'seconds':
                issues.append(f"acceleration_deceleration.unit: expected 'seconds', got '{ad.get('unit')}'")
        else:
            issues.append("Missing acceleration_deceleration parameter")
        
        # Check pickup_dropoff
        if 'pickup_dropoff' in parameters:
            pd = parameters['pickup_dropoff']
            if pd.get('value') != 6:
                issues.append(f"pickup_dropoff.value: expected 6, got {pd.get('value')}")
            if pd.get('unit') != 'seconds per interface':
                issues.append(f"pickup_dropoff.unit: expected 'seconds per interface', got '{pd.get('unit')}'")
        else:
            issues.append("Missing pickup_dropoff parameter")
        
        # Check reel_envelope
        if 'reel_envelope' in parameters:
            re = parameters['reel_envelope']
            if re.get('diameter', {}).get('value') != 1500:
                issues.append(f"reel_envelope.diameter: expected 1500mm, got {re.get('diameter', {}).get('value')}")
            if re.get('width_length', {}).get('value') != 2800:
                issues.append(f"reel_envelope.width_length: expected 2800mm, got {re.get('width_length', {}).get('value')}")
            if re.get('weight', {}).get('value') != 3500:
                issues.append(f"reel_envelope.weight: expected 3500kg, got {re.get('weight', {}).get('value')}")
        else:
            issues.append("Missing reel_envelope parameter")
        
        # Check controls
        if 'controls' not in parameters:
            issues.append("Missing controls specification")
        
        # Check safety
        if 'safety' not in parameters:
            issues.append("Missing safety specification")
        else:
            safety = parameters['safety']
            components = safety.get('components', [])
            for required in self.REQUIRED_SAFETY_COMPONENTS:
                if required not in components:
                    issues.append(f"Missing safety component: {required}")
        
        if issues:
            for issue in issues:
                logger.error(f"  - {issue}")
            self.errors.extend(issues)
            return False, {'issues': issues}
        
        logger.info("All parameters validated successfully")
        return True, {'status': 'passed'}
    
    def _validate_metadata(self, metadata: Dict) -> Tuple[bool, Dict]:
        """Validate metadata"""
        logger.info("Validating metadata...")
        issues = []
        
        required_meta_keys = ['validation_status', 'approval_status', 'revision']
        for key in required_meta_keys:
            if key not in metadata:
                issues.append(f"Missing metadata key: {key}")
        
        # Check validation status
        validation_status = metadata.get('validation_status', '')
        if validation_status.lower() != 'approved':
            warning = f"Unexpected validation_status: {validation_status}. Expected 'approved'"
            logger.warning(warning)
            self.warnings.append(warning)
        
        # Check approval status
        approval_status = metadata.get('approval_status', '')
        if approval_status.lower() != 'approved':
            warning = f"Unexpected approval_status: {approval_status}. Expected 'approved'"
            logger.warning(warning)
            self.warnings.append(warning)
        
        if issues:
            for issue in issues:
                logger.error(f"  - {issue}")
            self.errors.extend(issues)
            return False, {'issues': issues}
        
        logger.info("Metadata validated successfully")
        return True, {'status': 'passed'}
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': 'Ingetrans',
            'validation_status': 'passed' if not self.errors else 'failed',
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'results': self.validation_results
        }
        return report
    
    def save_validation_report(self, output_path: Path = None):
        """Save validation report to JSON file"""
        if output_path is None:
            output_path = Path(__file__).parent.parent / 'data' / 'ingetrans_validation_report.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_validation_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validation report saved to: {output_path}")
        return output_path
    
    def validate_all(self) -> bool:
        """Validate all Ingetrans data sources"""
        logger.info("Starting comprehensive Ingetrans data validation...")
        
        # Validate JSON configuration
        json_file = self.data_dir / 'ingetrans_parameters.json'
        json_valid, json_result = self.validate_json_file(json_file)
        self.validation_results.append({
            'source': 'JSON configuration',
            'file': str(json_file),
            'valid': json_valid,
            'result': json_result
        })
        
        # Generate and save report
        report_path = self.save_validation_report()
        
        if self.errors:
            logger.error(f"Validation completed with {len(self.errors)} errors")
            return False
        else:
            logger.info("Validation completed successfully!")
            return True


def main():
    """Main entry point"""
    validator = IngetransDataValidator()
    success = validator.validate_all()
    
    # Print summary
    print("\n" + "="*60)
    print("INGETRANS DATA VALIDATION REPORT")
    print("="*60)
    print(f"Status: {'PASSED' if success else 'FAILED'}")
    print(f"Errors: {len(validator.errors)}")
    print(f"Warnings: {len(validator.warnings)}")
    
    if validator.errors:
        print("\nErrors:")
        for error in validator.errors:
            print(f"  [!] {error}")
    
    if validator.warnings:
        print("\nWarnings:")
        for warning in validator.warnings:
            print(f"  [W] {warning}")
    
    print("\n" + "="*60)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
