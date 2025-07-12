#!/usr/bin/env python3
"""
Rule analysis utilities for detecting unused, duplicate, shadowed, and overlapping rules.
"""

import logging
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import ipaddress
import re

logger = logging.getLogger(__name__)

@dataclass
class RuleAnalysisResult:
    """Result of rule analysis containing all detected issues."""
    unused_rules: List[Dict[str, Any]]
    duplicate_rules: List[Dict[str, Any]]
    shadowed_rules: List[Dict[str, Any]]
    overlapping_rules: List[Dict[str, Any]]

def analyze_rules(rules: List[Dict[str, Any]]) -> RuleAnalysisResult:
    """
    Analyze firewall rules to detect various issues.
    
    Args:
        rules: List of rule dictionaries from database
        
    Returns:
        RuleAnalysisResult containing all detected issues
    """
    logger.info(f"Starting rule analysis for {len(rules)} rules")
    
    # Sort rules by position to maintain order for shadowing analysis
    sorted_rules = sorted(rules, key=lambda r: r.get('position', 0))
    
    # Detect different types of issues
    unused_rules = detect_unused_rules(sorted_rules)
    duplicate_rules = detect_duplicate_rules(sorted_rules)
    shadowed_rules = detect_shadowed_rules(sorted_rules)
    overlapping_rules = detect_overlapping_rules(sorted_rules)
    
    logger.info(f"Rule analysis completed: {len(unused_rules)} unused, {len(duplicate_rules)} duplicate, "
                f"{len(shadowed_rules)} shadowed, {len(overlapping_rules)} overlapping")
    
    return RuleAnalysisResult(
        unused_rules=unused_rules,
        duplicate_rules=duplicate_rules,
        shadowed_rules=shadowed_rules,
        overlapping_rules=overlapping_rules
    )

def detect_unused_rules(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect unused rules based on various criteria.
    
    Args:
        rules: List of rule dictionaries
        
    Returns:
        List of unused rule dictionaries with analysis details
    """
    unused_rules = []
    
    for rule in rules:
        reasons = []
        
        # Check if rule is disabled
        if rule.get('is_disabled', False):
            reasons.append("Rule is disabled")
        
        # Check for deny/drop rules that might be unused
        if rule.get('action', '').lower() in ['deny', 'drop']:
            # Deny rules at the end are often unused catch-alls
            if rule.get('position', 0) > len(rules) * 0.8:  # Last 20% of rules
                if (rule.get('src', '').lower() == 'any' and 
                    rule.get('dst', '').lower() == 'any' and
                    rule.get('service', '').lower() == 'any'):
                    reasons.append("Catch-all deny rule at end of ruleset")
        
        # Check for rules with impossible conditions
        if _has_impossible_conditions(rule):
            reasons.append("Rule has impossible or contradictory conditions")
        
        # Check for rules that are never reached due to position
        if _is_unreachable_rule(rule, rules):
            reasons.append("Rule is unreachable due to position and broader rules above")
        
        if reasons:
            unused_rule = {
                'id': rule.get('id'),
                'name': rule.get('rule_name', 'Unknown'),
                'position': rule.get('position', 0),
                'action': rule.get('action', 'unknown'),
                'type': 'unused_rule',
                'severity': 'medium' if rule.get('is_disabled') else 'high',
                'reasons': reasons,
                'description': f"Rule '{rule.get('rule_name', 'Unknown')}' appears to be unused: {'; '.join(reasons)}",
                'recommendation': _get_unused_rule_recommendation(rule, reasons)
            }
            unused_rules.append(unused_rule)
    
    return unused_rules

def detect_duplicate_rules(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect duplicate rules with identical or functionally equivalent configurations.
    
    Args:
        rules: List of rule dictionaries
        
    Returns:
        List of duplicate rule groups
    """
    duplicate_rules = []
    seen_rules = {}
    
    for rule in rules:
        # Create a signature for the rule based on key attributes
        signature = _create_rule_signature(rule)
        
        if signature in seen_rules:
            # Found a duplicate
            original_rule = seen_rules[signature]
            
            duplicate_group = {
                'type': 'duplicate_rules',
                'severity': 'medium',
                'original_rule': {
                    'id': original_rule.get('id'),
                    'name': original_rule.get('rule_name', 'Unknown'),
                    'position': original_rule.get('position', 0)
                },
                'duplicate_rule': {
                    'id': rule.get('id'),
                    'name': rule.get('rule_name', 'Unknown'),
                    'position': rule.get('position', 0)
                },
                'description': f"Rule '{rule.get('rule_name', 'Unknown')}' is identical to rule '{original_rule.get('rule_name', 'Unknown')}'",
                'recommendation': f"Consider removing duplicate rule '{rule.get('rule_name', 'Unknown')}' at position {rule.get('position', 0)}"
            }
            duplicate_rules.append(duplicate_group)
        else:
            seen_rules[signature] = rule
    
    return duplicate_rules

def detect_shadowed_rules(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect rules that are shadowed by broader rules with higher precedence.
    
    Args:
        rules: List of rule dictionaries (should be sorted by position)
        
    Returns:
        List of shadowed rule dictionaries
    """
    shadowed_rules = []
    
    for i, rule in enumerate(rules):
        # Check if this rule is shadowed by any rule above it
        for j, higher_rule in enumerate(rules[:i]):
            if _is_rule_shadowed_by(rule, higher_rule):
                shadowed_rule = {
                    'id': rule.get('id'),
                    'name': rule.get('rule_name', 'Unknown'),
                    'position': rule.get('position', 0),
                    'type': 'shadowed_rule',
                    'severity': 'high',
                    'shadowed_by': {
                        'id': higher_rule.get('id'),
                        'name': higher_rule.get('rule_name', 'Unknown'),
                        'position': higher_rule.get('position', 0)
                    },
                    'description': f"Rule '{rule.get('rule_name', 'Unknown')}' is shadowed by rule '{higher_rule.get('rule_name', 'Unknown')}' at position {higher_rule.get('position', 0)}",
                    'recommendation': f"Consider reordering or removing shadowed rule '{rule.get('rule_name', 'Unknown')}'"
                }
                shadowed_rules.append(shadowed_rule)
                break  # Rule can only be shadowed by one rule (the first broader one)
    
    return shadowed_rules

def detect_overlapping_rules(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect rules with overlapping traffic scope that might cause confusion.
    
    Args:
        rules: List of rule dictionaries
        
    Returns:
        List of overlapping rule groups
    """
    overlapping_rules = []
    
    for i, rule1 in enumerate(rules):
        for j, rule2 in enumerate(rules[i+1:], i+1):
            if _rules_overlap(rule1, rule2):
                overlap_group = {
                    'type': 'overlapping_rules',
                    'severity': 'medium',
                    'rule1': {
                        'id': rule1.get('id'),
                        'name': rule1.get('rule_name', 'Unknown'),
                        'position': rule1.get('position', 0)
                    },
                    'rule2': {
                        'id': rule2.get('id'),
                        'name': rule2.get('rule_name', 'Unknown'),
                        'position': rule2.get('position', 0)
                    },
                    'description': f"Rules '{rule1.get('rule_name', 'Unknown')}' and '{rule2.get('rule_name', 'Unknown')}' have overlapping traffic scope",
                    'recommendation': "Review rules for potential consolidation or clarification of intent"
                }
                overlapping_rules.append(overlap_group)
    
    return overlapping_rules

def _create_rule_signature(rule: Dict[str, Any]) -> str:
    """Create a unique signature for a rule based on its key attributes."""
    return f"{rule.get('src_zone', '')}-{rule.get('dst_zone', '')}-{rule.get('src', '')}-{rule.get('dst', '')}-{rule.get('service', '')}-{rule.get('action', '')}"

def _has_impossible_conditions(rule: Dict[str, Any]) -> bool:
    """Check if a rule has impossible or contradictory conditions."""
    # Example: Check for obviously impossible IP ranges or contradictory zones
    # This is a simplified check - could be expanded with more sophisticated logic
    
    src = rule.get('src', '').lower()
    dst = rule.get('dst', '').lower()
    
    # Check for same source and destination in different zones (simplified check)
    if (src != 'any' and dst != 'any' and src == dst and 
        rule.get('src_zone', '') != rule.get('dst_zone', '')):
        return True
    
    return False

def _is_unreachable_rule(rule: Dict[str, Any], all_rules: List[Dict[str, Any]]) -> bool:
    """Check if a rule is unreachable due to broader rules above it."""
    rule_position = rule.get('position', 0)
    
    # Check rules with lower position numbers (higher precedence)
    for other_rule in all_rules:
        if (other_rule.get('position', 0) < rule_position and 
            _is_rule_completely_covered_by(rule, other_rule)):
            return True
    
    return False

def _is_rule_shadowed_by(rule: Dict[str, Any], higher_rule: Dict[str, Any]) -> bool:
    """Check if a rule is completely shadowed by a higher precedence rule."""
    # Simplified shadowing check - could be made more sophisticated
    
    # If higher rule has same or broader scope and same action, it shadows
    if (higher_rule.get('action', '') == rule.get('action', '') and
        _is_scope_broader_or_equal(higher_rule, rule)):
        return True
    
    # If higher rule denies traffic that this rule would allow, it shadows
    if (higher_rule.get('action', '').lower() in ['deny', 'drop'] and
        rule.get('action', '').lower() == 'allow' and
        _is_scope_broader_or_equal(higher_rule, rule)):
        return True
    
    return False

def _is_rule_completely_covered_by(rule: Dict[str, Any], covering_rule: Dict[str, Any]) -> bool:
    """Check if a rule is completely covered by another rule."""
    return _is_scope_broader_or_equal(covering_rule, rule)

def _rules_overlap(rule1: Dict[str, Any], rule2: Dict[str, Any]) -> bool:
    """Check if two rules have overlapping traffic scope."""
    # Simplified overlap check - could be made more sophisticated
    
    # Check if zones overlap
    if not _zones_overlap(rule1, rule2):
        return False
    
    # Check if addresses overlap
    if not _addresses_overlap(rule1.get('src', ''), rule2.get('src', '')) or \
       not _addresses_overlap(rule1.get('dst', ''), rule2.get('dst', '')):
        return False
    
    # Check if services overlap
    if not _services_overlap(rule1.get('service', ''), rule2.get('service', '')):
        return False
    
    return True

def _is_scope_broader_or_equal(broader_rule: Dict[str, Any], narrower_rule: Dict[str, Any]) -> bool:
    """Check if one rule's scope is broader than or equal to another's."""
    # Simplified scope comparison - could be made more sophisticated
    
    # Check zones
    if not _zone_covers(broader_rule.get('src_zone', ''), narrower_rule.get('src_zone', '')) or \
       not _zone_covers(broader_rule.get('dst_zone', ''), narrower_rule.get('dst_zone', '')):
        return False
    
    # Check addresses
    if not _address_covers(broader_rule.get('src', ''), narrower_rule.get('src', '')) or \
       not _address_covers(broader_rule.get('dst', ''), narrower_rule.get('dst', '')):
        return False
    
    # Check services
    if not _service_covers(broader_rule.get('service', ''), narrower_rule.get('service', '')):
        return False
    
    return True

def _zones_overlap(rule1: Dict[str, Any], rule2: Dict[str, Any]) -> bool:
    """Check if zones in two rules overlap."""
    # Simplified - assumes 'any' covers all zones
    src1, dst1 = rule1.get('src_zone', '').lower(), rule1.get('dst_zone', '').lower()
    src2, dst2 = rule2.get('src_zone', '').lower(), rule2.get('dst_zone', '').lower()
    
    return ((src1 == 'any' or src2 == 'any' or src1 == src2) and
            (dst1 == 'any' or dst2 == 'any' or dst1 == dst2))

def _addresses_overlap(addr1: str, addr2: str) -> bool:
    """Check if two address specifications overlap."""
    # Simplified - assumes 'any' covers all addresses
    addr1, addr2 = addr1.lower(), addr2.lower()
    
    if addr1 == 'any' or addr2 == 'any' or addr1 == addr2:
        return True
    
    # Could add more sophisticated IP range overlap detection here
    return False

def _services_overlap(svc1: str, svc2: str) -> bool:
    """Check if two service specifications overlap."""
    # Simplified - assumes 'any' covers all services
    svc1, svc2 = svc1.lower(), svc2.lower()
    
    return svc1 == 'any' or svc2 == 'any' or svc1 == svc2

def _zone_covers(broader_zone: str, narrower_zone: str) -> bool:
    """Check if one zone covers another."""
    broader_zone, narrower_zone = broader_zone.lower(), narrower_zone.lower()
    return broader_zone == 'any' or broader_zone == narrower_zone

def _address_covers(broader_addr: str, narrower_addr: str) -> bool:
    """Check if one address specification covers another."""
    broader_addr, narrower_addr = broader_addr.lower(), narrower_addr.lower()
    return broader_addr == 'any' or broader_addr == narrower_addr

def _service_covers(broader_svc: str, narrower_svc: str) -> bool:
    """Check if one service specification covers another."""
    broader_svc, narrower_svc = broader_svc.lower(), narrower_svc.lower()
    return broader_svc == 'any' or broader_svc == narrower_svc

def _get_unused_rule_recommendation(rule: Dict[str, Any], reasons: List[str]) -> str:
    """Get a specific recommendation for an unused rule."""
    if rule.get('is_disabled'):
        return f"Consider removing disabled rule '{rule.get('rule_name', 'Unknown')}' if it's no longer needed"
    elif "catch-all deny" in ' '.join(reasons).lower():
        return f"Review if catch-all deny rule '{rule.get('rule_name', 'Unknown')}' is necessary"
    else:
        return f"Review rule '{rule.get('rule_name', 'Unknown')}' for potential removal or modification"
