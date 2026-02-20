"""
DiffEngine: Visual Proof of PII Redaction

Compares original resume text against redacted text to produce
a structured diff that the frontend can render with red/green highlighting.

Uses Google's diff-match-patch library for semantic text comparison.
"""

from typing import List, Dict, Any
from diff_match_patch import diff_match_patch


class DiffEngine:
    """
    Compares original vs redacted text and produces UI-friendly diff output.
    
    Output format:
    [
        {"type": "equal", "text": "I have "},
        {"type": "delete", "text": "John Smith"},  # Red - removed PII
        {"type": "insert", "text": "[CANDIDATE]"},  # Green - placeholder
        {"type": "equal", "text": " and I work at..."}
    ]
    """
    
    def __init__(self):
        self.dmp = diff_match_patch()
        # Tune diff sensitivity
        self.dmp.Diff_Timeout = 2.0  # 2 second timeout for large texts
        self.dmp.Diff_EditCost = 4   # Higher = fewer small edits
    
    def compute_diff(self, original_text: str, redacted_text: str) -> List[Dict[str, str]]:
        """
        Compute semantic diff between original and redacted text.
        
        Args:
            original_text: The raw resume text with PII
            redacted_text: The sanitized text with placeholders
            
        Returns:
            List of diff operations in UI-friendly format:
            [{"type": "equal|insert|delete", "text": "..."}]
        """
        
        if not original_text and not redacted_text:
            return []
        
        if not original_text:
            return [{"type": "insert", "text": redacted_text}]
        
        if not redacted_text:
            return [{"type": "delete", "text": original_text}]
        
        # Compute the raw diff
        diffs = self.dmp.diff_main(original_text, redacted_text)
        
        # Clean up the diff for better semantic grouping
        self.dmp.diff_cleanupSemantic(diffs)
        
        # Convert to UI-friendly format
        return self._format_for_frontend(diffs)
    
    def _format_for_frontend(self, raw_diffs: List[tuple]) -> List[Dict[str, str]]:
        """
        Convert diff-match-patch output to clean JSON structure.
        
        Raw format: [(0, "equal text"), (-1, "deleted"), (1, "inserted")]
        Output format: [{"type": "equal", "text": "..."}, ...]
        """
        
        type_map = {
            0: "equal",
            -1: "delete",  # Was in original, removed (RED)
            1: "insert"    # Added in redacted version (GREEN)
        }
        
        formatted = []
        
        for op_code, text in raw_diffs:
            if not text:
                continue
                
            formatted.append({
                "type": type_map.get(op_code, "equal"),
                "text": text
            })
        
        return formatted
    
    def compute_diff_summary(self, original_text: str, redacted_text: str) -> Dict[str, Any]:
        """
        Compute diff with additional statistics for the audit trail.
        
        Returns:
            {
                "diff": [...],  # The diff operations
                "stats": {
                    "total_changes": int,
                    "deletions": int,  # PII items removed
                    "insertions": int,  # Placeholders added
                    "unchanged_chars": int,
                    "redaction_rate": float  # % of text changed
                },
                "pii_items_removed": [...]  # List of deleted text segments
            }
        """
        
        diff = self.compute_diff(original_text, redacted_text)
        
        # Calculate statistics
        deletions = []
        insertions = []
        equal_chars = 0
        
        for item in diff:
            if item["type"] == "delete":
                deletions.append(item["text"])
            elif item["type"] == "insert":
                insertions.append(item["text"])
            else:  # equal
                equal_chars += len(item["text"])
        
        total_original_chars = len(original_text) if original_text else 1
        deleted_chars = sum(len(d) for d in deletions)
        redaction_rate = (deleted_chars / total_original_chars) * 100
        
        return {
            "diff": diff,
            "stats": {
                "total_changes": len(deletions) + len(insertions),
                "deletions": len(deletions),
                "insertions": len(insertions),
                "unchanged_chars": equal_chars,
                "deleted_chars": deleted_chars,
                "redaction_rate": round(redaction_rate, 2)
            },
            "pii_items_removed": deletions,
            "placeholders_added": insertions
        }
    
    def generate_html_preview(self, original_text: str, redacted_text: str) -> str:
        """
        Generate an HTML representation with color highlighting.
        Useful for debugging or server-side rendering.
        
        RED = Removed PII
        GREEN = Added placeholder
        """
        
        diff = self.compute_diff(original_text, redacted_text)
        
        html_parts = []
        for item in diff:
            text = item["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text = text.replace("\n", "<br>")
            
            if item["type"] == "delete":
                html_parts.append(f'<span class="diff-delete" style="background-color: #ffcccc; text-decoration: line-through; color: #cc0000;">{text}</span>')
            elif item["type"] == "insert":
                html_parts.append(f'<span class="diff-insert" style="background-color: #ccffcc; color: #006600;">{text}</span>')
            else:
                html_parts.append(f'<span class="diff-equal">{text}</span>')
        
        return "".join(html_parts)


# Quick test
if __name__ == "__main__":
    engine = DiffEngine()
    
    original = """John Smith
Email: john.smith@email.com
Phone: 555-123-4567

I have 5 years of Python experience working at TechCorp.
My manager Jane Doe can confirm my work on the ML pipeline.
"""
    
    redacted = """[CANDIDATE]
Email: [EMAIL_REDACTED]
Phone: [PHONE_REDACTED]

I have 5 years of Python experience working at [COMPANY].
My manager [NAME_REDACTED] can confirm my work on the ML pipeline.
"""
    
    print("="*60)
    print("DIFF ENGINE TEST")
    print("="*60)
    
    # Test basic diff
    result = engine.compute_diff_summary(original, redacted)
    
    print(f"\n📊 Statistics:")
    print(f"   Total changes: {result['stats']['total_changes']}")
    print(f"   PII items removed: {result['stats']['deletions']}")
    print(f"   Placeholders added: {result['stats']['insertions']}")
    print(f"   Redaction rate: {result['stats']['redaction_rate']}%")
    
    print(f"\n🔴 PII Removed:")
    for item in result['pii_items_removed']:
        print(f"   - \"{item.strip()}\"")
    
    print(f"\n🟢 Placeholders Added:")
    for item in result['placeholders_added']:
        print(f"   + \"{item.strip()}\"")
    
    print("\n📄 Diff Operations:")
    for item in result['diff'][:10]:  # First 10
        symbol = "=" if item["type"] == "equal" else ("-" if item["type"] == "delete" else "+")
        text_preview = item["text"][:50].replace("\n", "\\n")
        print(f"   [{symbol}] {text_preview}...")
    
    print("\n🎨 HTML Preview:")
    html = engine.generate_html_preview(original, redacted)
    print(html[:500] + "...")
