# Senior Full Stack QA Engineer - Code Analysis Report

**Date**: December 18, 2025  
**Project**: Velos AI - TrustFlow Platform  
**Analyzed By**: Senior QA Engineer

---

## 🐛 CRITICAL BUGS IDENTIFIED

### Bug #1: GodMode Component - API Endpoint Mismatch (SEVERITY: HIGH)

**Location**: `/velos-frontend/src/components/GodMode.jsx` Line 79-91

**Issue**: 
- Frontend requests `/api/insights`, `/api/agents`, `/api/health`
- Backend ONLY has `/api/insights` endpoint (returns different structure)
- Backend has `/health` (not `/api/health`)
- `/api/agents` exists but returns wrong data structure for God Mode

**Root Cause**:
```javascript
// Frontend expects:
{ bias_alerts: 0, fraud_cases: 0, avg_processing_time: 0, total_candidates: 0 }

// Backend /api/insights returns:
{ insights: [{ type: "info", message: "..." }] }  // Wrong structure!
```

**Fix Required**: Backend needs to return metrics, not insight messages.

---

### Bug #2: GodMode Component - Fallback Data Structure Mismatch (SEVERITY: MEDIUM)

**Location**: `/velos-frontend/src/components/GodMode.jsx` Line 109-114

**Issue**: 
- Agents array expects: `{ name, role, status, processed, successRate, avgTime }`
- Backend `/api/agents` returns: `{ id, name, code, description, status, stats, color }`
- No mapping between backend `stats` object and frontend properties

**Impact**: Agent cards display "0" for all metrics even when backend has data.

---

### Bug #3: Health Endpoint Path Mismatch (SEVERITY: HIGH)

**Location**: Frontend requests `/api/health`, Backend exposes `/health`

**Issue**: 404 error causes fallback to `{ status: 'unknown', uptime: 0, memory_usage: 0 }`

---

### Bug #4: CompareCandidates - No Input Validation (SEVERITY: MEDIUM)

**Location**: `/velos-frontend/src/components/CompareCandidates.jsx` Line 84-88

**Issue**: 
- Only checks if IDs are empty with `.trim()`
- No validation for ID format (e.g., should start with "cand_")
- No check if both IDs are identical
- Alert is non-blocking, poor UX

---

### Bug #5: TrustPacket - Missing Error Handling for Invalid IDs (SEVERITY: MEDIUM)

**Location**: `/velos-frontend/src/components/TrustPacket.jsx` Line 34-47

**Issue**:
- Only shows generic alert on failure
- No distinction between "not found" vs "server error"
- No loading state cleanup on error
- Trust packet state not cleared on error

---

### Bug #6: BatchUpload - Race Condition in Progress Bar (SEVERITY: LOW)

**Location**: `/velos-frontend/src/components/BatchUpload.jsx` Line 59-64

**Issue**:
- Progress interval not cleared if component unmounts during upload
- Can cause memory leak
- Progress can exceed 100% in edge cases

---

## 🔧 DEBUG SCRIPT - Mock Data Injection

**File**: `/velos-frontend/src/components/GodMode.jsx`

Add this function to inject mock data for UI testing:

```javascript
// ADD THIS FUNCTION AFTER LINE 76 (after fetchGodModeData function)

const injectMockData = () => {
  console.log("🧪 Injecting mock data for testing...");
  
  setInsights({
    bias_alerts: 3,
    fraud_cases: 2,
    avg_processing_time: 2.4,
    total_candidates: 127
  });

  setAgents([
    {
      name: 'Gatekeeper',
      role: 'Entry Filter',
      status: 'active',
      processed: 45,
      successRate: 89,
      avgTime: 1.2
    },
    {
      name: 'Validator',
      role: 'Verification',
      status: 'active',
      processed: 38,
      successRate: 95,
      avgTime: 2.8
    },
    {
      name: 'Inquisitor',
      role: 'Deep Analysis',
      status: 'active',
      processed: 34,
      successRate: 92,
      avgTime: 3.5
    }
  ]);

  setHealth({
    status: 'healthy',
    uptime: 14523, // 4 hours in seconds
    memory_usage: 67.3
  });

  setLoading(false);
  console.log("✅ Mock data injected successfully");
};

// REPLACE LINE 74-75 with:
useEffect(() => {
  // Toggle between real and mock data
  const USE_MOCK_DATA = true; // Set to false for real API calls
  
  if (USE_MOCK_DATA) {
    injectMockData();
  } else {
    fetchGodModeData();
    const interval = setInterval(fetchGodModeData, 5000);
    return () => clearInterval(interval);
  }
}, []);
```

**Usage**: Set `USE_MOCK_DATA = true` to test UI rendering without backend.

---

## 🧪 UNIT TEST FILES

### Test File 1: CompareCandidates.test.jsx

**Location**: `/velos-frontend/tests/CompareCandidates.test.jsx`

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CompareCandidates from '../src/components/CompareCandidates';
import '@testing-library/jest-dom';

describe('CompareCandidates Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('should render without crashing', () => {
    render(<CompareCandidates />);
    expect(screen.getByText('Compare Candidates')).toBeInTheDocument();
  });

  it('should display placeholder text when no comparison is made', () => {
    render(<CompareCandidates />);
    expect(screen.getByText('Enter two candidate IDs to start comparison')).toBeInTheDocument();
  });

  it('should have two input fields for candidate IDs', () => {
    render(<CompareCandidates />);
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    expect(inputs).toHaveLength(2);
  });

  it('should show alert when Compare button clicked with empty fields', async () => {
    window.alert = vi.fn();
    render(<CompareCandidates />);
    
    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);
    
    expect(window.alert).toHaveBeenCalledWith('Please enter both candidate IDs');
  });

  it('should show alert when only one field is filled', async () => {
    window.alert = vi.fn();
    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'cand_123' } });
    
    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);
    
    expect(window.alert).toHaveBeenCalledWith('Please enter both candidate IDs');
  });

  it('should disable Compare button during loading', async () => {
    global.fetch = vi.fn(() => new Promise(() => {})); // Never resolves
    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'cand_123' } });
    fireEvent.change(inputs[1], { target: { value: 'cand_456' } });
    
    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);
    
    await waitFor(() => {
      expect(screen.getByText('Comparing...')).toBeInTheDocument();
      expect(compareButton).toBeDisabled();
    });
  });

  it('should call API with correct payload when both IDs are provided', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          candidate1: { name: 'John', trust_score: 85 },
          candidate2: { name: 'Jane', trust_score: 90 },
          winner: 'Jane'
        })
      })
    );

    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'cand_123' } });
    fireEvent.change(inputs[1], { target: { value: 'cand_456' } });
    
    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/compare',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            candidate1_id: 'cand_123',
            candidate2_id: 'cand_456'
          })
        })
      );
    });
  });

  it('should display error alert when API returns error', async () => {
    window.alert = vi.fn();
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404
      })
    );

    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'invalid_id' } });
    fireEvent.change(inputs[1], { target: { value: 'cand_456' } });
    
    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to compare candidates');
    });
  });

  it('should render comparison results when API succeeds', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          candidate1: {
            name: 'John Doe',
            role: 'Senior Dev',
            trust_score: 85,
            experience: 5,
            skills_match: 78
          },
          candidate2: {
            name: 'Jane Smith',
            role: 'Lead Dev',
            trust_score: 92,
            experience: 7,
            skills_match: 88
          },
          winner: 'Jane Smith'
        })
      })
    );

    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'cand_123' } });
    fireEvent.change(inputs[1], { target: { value: 'cand_456' } });
    
    fireEvent.click(screen.getByText('Compare Now'));
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Recommended Candidate')).toBeInTheDocument();
    });
  });

  it('should trim whitespace from input IDs', async () => {
    window.alert = vi.fn();
    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: '   ' } }); // Only spaces
    fireEvent.change(inputs[1], { target: { value: '   ' } });
    
    fireEvent.click(screen.getByText('Compare Now'));
    
    expect(window.alert).toHaveBeenCalledWith('Please enter both candidate IDs');
  });

  it('should handle network errors gracefully', async () => {
    window.alert = vi.fn();
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

    render(<CompareCandidates />);
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'cand_123' } });
    fireEvent.change(inputs[1], { target: { value: 'cand_456' } });
    
    fireEvent.click(screen.getByText('Compare Now'));
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to compare candidates');
    });
  });
});
```

---

### Test File 2: TrustPacket.test.jsx

**Location**: `/velos-frontend/tests/TrustPacket.test.jsx`

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TrustPacket from '../src/components/TrustPacket';
import '@testing-library/jest-dom';

describe('TrustPacket Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('should render without crashing', () => {
    render(<TrustPacket />);
    expect(screen.getByText('Trust Packet Viewer')).toBeInTheDocument();
  });

  it('should display placeholder text when no packet is loaded', () => {
    render(<TrustPacket />);
    expect(screen.getByText('Enter a candidate ID to view trust packet')).toBeInTheDocument();
  });

  it('should have input field for candidate ID', () => {
    render(<TrustPacket />);
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    expect(input).toBeInTheDocument();
  });

  it('should show alert when Fetch button clicked with empty ID', async () => {
    window.alert = vi.fn();
    render(<TrustPacket />);
    
    const fetchButton = screen.getByText('Fetch Packet');
    fireEvent.click(fetchButton);
    
    expect(window.alert).toHaveBeenCalledWith('Please enter a candidate ID');
  });

  it('should show alert when input is only whitespace', async () => {
    window.alert = vi.fn();
    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: '   ' } });
    
    const fetchButton = screen.getByText('Fetch Packet');
    fireEvent.click(fetchButton);
    
    expect(window.alert).toHaveBeenCalledWith('Please enter a candidate ID');
  });

  it('should disable Fetch button during loading', async () => {
    global.fetch = vi.fn(() => new Promise(() => {})); // Never resolves
    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    
    const fetchButton = screen.getByText('Fetch Packet');
    fireEvent.click(fetchButton);
    
    await waitFor(() => {
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(fetchButton).toBeDisabled();
    });
  });

  it('should trigger fetch on Enter key press', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          transaction_hash: '0xabc123',
          block_number: 12345
        })
      })
    );

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/trust-packet/cand_123'
      );
    });
  });

  it('should display error alert when candidate not found (404)', async () => {
    window.alert = vi.fn();
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404
      })
    );

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'invalid_id' } });
    
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Trust packet not found');
    });
  });

  it('should display generic error alert on network failure', async () => {
    window.alert = vi.fn();
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to fetch trust packet');
    });
  });

  it('should render trust packet data when API succeeds', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          transaction_hash: '0xabc123def456',
          block_number: 98765,
          timestamp: '2025-12-18T14:10:00',
          merkle_root: '0x789xyz',
          pii_diff: {
            email: { original: 'john@example.com', redacted: 'j***@***.com' },
            phone: { original: '+1234567890', redacted: '+12*****890' }
          }
        })
      })
    );

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => {
      expect(screen.getByText('Blockchain Transaction')).toBeInTheDocument();
      expect(screen.getByText('0xabc123def456')).toBeInTheDocument();
      expect(screen.getByText('98765')).toBeInTheDocument();
    });
  });

  it('should render PII diff section when available', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          transaction_hash: '0xabc',
          pii_diff: {
            email: { original: 'test@example.com', redacted: 't***@***.com' }
          }
        })
      })
    );

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => {
      expect(screen.getByText('PII Redaction Proof')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      expect(screen.getByText('t***@***.com')).toBeInTheDocument();
    });
  });

  it('should call verify integrity API when button clicked', async () => {
    // First load a trust packet
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ transaction_hash: '0xabc' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ verified: true })
      });

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => screen.getByText('Verify Integrity'));
    
    const verifyButton = screen.getByText('Verify Integrity');
    fireEvent.click(verifyButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/verify-integrity',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ candidate_id: 'cand_123' })
        })
      );
    });
  });

  it('should display verification success message when verified', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ transaction_hash: '0xabc' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ verified: true })
      });

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => screen.getByText('Verify Integrity'));
    fireEvent.click(screen.getByText('Verify Integrity'));
    
    await waitFor(() => {
      expect(screen.getByText('Integrity Verified')).toBeInTheDocument();
      expect(screen.getByText('All data matches blockchain records')).toBeInTheDocument();
    });
  });

  it('should display verification failure message when not verified', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ transaction_hash: '0xabc' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ verified: false })
      });

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => screen.getByText('Verify Integrity'));
    fireEvent.click(screen.getByText('Verify Integrity'));
    
    await waitFor(() => {
      expect(screen.getByText('Verification Failed')).toBeInTheDocument();
      expect(screen.getByText('Data tampering detected')).toBeInTheDocument();
    });
  });

  it('should trigger download when Download Dossier button clicked', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ transaction_hash: '0xabc' })
      })
      .mockResolvedValueOnce({
        ok: true,
        blob: async () => new Blob(['test'], { type: 'application/json' })
      });

    // Mock URL methods
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();

    // Mock DOM element
    const mockLink = {
      click: vi.fn(),
      href: '',
      download: ''
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink);

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => screen.getByText('Download Dossier'));
    fireEvent.click(screen.getByText('Download Dossier'));
    
    await waitFor(() => {
      expect(mockLink.click).toHaveBeenCalled();
      expect(mockLink.download).toBe('cand_123_dossier.json');
    });
  });
});
```

---

## ⚠️ EDGE CASE ANALYSIS

### Edge Cases for Batch Upload Component

#### Edge Case #1: **Corrupted ZIP File**

**Scenario**: User uploads a ZIP file that is corrupted or has invalid internal structure.

**Current Behavior**: 
- Frontend accepts the file (only checks `.zip` extension)
- Sends to backend
- Backend may crash or return 500 error
- Frontend shows generic "Upload failed" alert

**Potential Impact**: 
- Server crashes if unhandled exception
- Poor user experience (no specific error message)
- Uploaded file may remain in temp storage

**Recommended Fix**:
```javascript
// Backend: Add ZIP validation before processing
import zipfile

try:
    with zipfile.ZipFile(file) as z:
        if z.testzip() is not None:
            raise HTTPException(400, "Corrupted ZIP file")
except zipfile.BadZipFile:
    raise HTTPException(400, "Invalid ZIP file format")
```

---

#### Edge Case #2: **ZIP Bomb / Large File Attack**

**Scenario**: Attacker uploads a small ZIP file that expands to gigabytes (decompression bomb).

**Current Behavior**:
- No file size limit check before extraction
- Server memory exhaustion
- Denial of Service (DoS)

**Potential Impact**:
- Server crashes
- Affects all users
- Cloud hosting costs spike

**Recommended Fix**:
```python
# Backend: Add size limits
MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50MB
MAX_EXTRACTED_SIZE = 200 * 1024 * 1024  # 200MB

# Check uploaded file size
if file.size > MAX_ZIP_SIZE:
    raise HTTPException(413, "ZIP file too large")

# Check extracted size before full extraction
total_size = sum(info.file_size for info in zipfile.ZipFile(file).infolist())
if total_size > MAX_EXTRACTED_SIZE:
    raise HTTPException(413, "Extracted content exceeds limit")
```

---

#### Edge Case #3: **Non-Resume Files in ZIP**

**Scenario**: ZIP contains images, executables, or other non-PDF/DOCX files.

**Current Behavior**:
- Frontend doesn't validate file contents
- Backend may attempt to parse invalid files
- Errors in batch results, but no clear indication

**Potential Impact**:
- Wasted processing time
- Misleading success/failure counts
- Security risk (executable files)

**Recommended Fix**:
```python
# Backend: Filter and validate file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
}

valid_files = []
for file in extracted_files:
    ext = Path(file).suffix.lower()
    mime = magic.from_file(file, mime=True)
    
    if ext in ALLOWED_EXTENSIONS and mime in ALLOWED_MIME_TYPES:
        valid_files.append(file)
    else:
        log_warning(f"Skipped invalid file: {file}")

# Return summary with skipped files count
return {
    "processed": len(valid_files),
    "skipped": len(extracted_files) - len(valid_files),
    "results": [...],
    "skipped_files": [...]
}
```

---

### Edge Cases for Trust Packet Component

#### Edge Case #4: **Special Characters in Candidate ID**

**Scenario**: User enters ID with special characters: `cand_123<script>alert('xss')</script>`

**Current Behavior**:
- No input sanitization
- Sent directly to API
- Could cause XSS if reflected in error messages

**Recommended Fix**:
```javascript
// Frontend: Sanitize and validate input
const sanitizeCandidateId = (id) => {
  return id.trim().replace(/[^a-zA-Z0-9_-]/g, '');
};

const validateCandidateId = (id) => {
  const pattern = /^cand_[a-zA-Z0-9]{3,20}$/;
  return pattern.test(id);
};

// Use before API call
const sanitized = sanitizeCandidateId(candidateId);
if (!validateCandidateId(sanitized)) {
  alert('Invalid candidate ID format. Expected: cand_XXX');
  return;
}
```

---

#### Edge Case #5: **Blockchain Verification Timeout**

**Scenario**: Blockchain node is slow/down, verification takes >30 seconds.

**Current Behavior**:
- No timeout set on verification request
- User waits indefinitely
- Button shows "Verifying..." forever

**Recommended Fix**:
```javascript
// Frontend: Add timeout to verify request
const verifyIntegrity = async () => {
  if (!candidateId.trim()) return;
  
  setVerifying(true);
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
  
  try {
    const response = await fetch('http://localhost:8000/api/verify-integrity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_id: candidateId }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      setVerified(data.verified);
    }
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      alert('Verification timeout. Blockchain node may be unavailable.');
    } else {
      console.error('Failed to verify integrity:', error);
    }
  } finally {
    setVerifying(false);
  }
};
```

---

#### Edge Case #6: **Race Condition on Rapid Downloads**

**Scenario**: User clicks "Download Dossier" multiple times rapidly.

**Current Behavior**:
- Multiple simultaneous downloads triggered
- Multiple API calls
- Browser may block or queue downloads

**Recommended Fix**:
```javascript
// Frontend: Debounce download function
const [isDownloading, setIsDownloading] = useState(false);

const downloadDossier = async () => {
  if (!candidateId.trim() || isDownloading) return;
  
  setIsDownloading(true);
  
  try {
    const response = await fetch(`http://localhost:8000/api/candidate-dossier/${candidateId}`);
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${candidateId}_dossier.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('Failed to download dossier:', error);
    alert('Download failed. Please try again.');
  } finally {
    setTimeout(() => setIsDownloading(false), 1000); // Prevent rapid re-clicks
  }
};

// Update button
<button 
  onClick={downloadDossier} 
  disabled={isDownloading}
  className="..."
>
  {isDownloading ? 'Downloading...' : 'Download Dossier'}
</button>
```

---

## 📋 TESTING SETUP INSTRUCTIONS

### Install Testing Dependencies

```bash
cd /media/raj/Raj/Hackathon/trustflow/velos-frontend

npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### Create Vitest Config

**File**: `vite.config.js` (add test configuration)

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
  },
})
```

### Create Test Setup File

**File**: `tests/setup.js`

```javascript
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

### Add Test Scripts to package.json

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### Run Tests

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

---

## 🎯 PRIORITY RECOMMENDATIONS

### Immediate Actions (P0 - Critical)

1. **Fix Backend `/api/insights` Endpoint** - Return correct structure with numeric metrics
2. **Fix Health Endpoint Path** - Change `/health` to `/api/health` OR update frontend to use `/health`
3. **Add Input Validation** - Sanitize all user inputs before API calls (XSS prevention)

### High Priority (P1)

4. **Implement Backend `/api/agents` Mapping** - Map `stats` object to expected frontend properties
5. **Add Error Boundaries** - Wrap components in ErrorBoundary to prevent full app crashes
6. **Add File Size Limits** - Prevent ZIP bomb attacks in batch upload

### Medium Priority (P2)

7. **Improve Error Messages** - Replace generic alerts with user-friendly notifications
8. **Add Loading States** - Ensure all async operations show proper loading UI
9. **Add Request Timeouts** - Prevent indefinite waiting on slow API calls

### Low Priority (P3)

10. **Add E2E Tests** - Use Playwright/Cypress for full user flow testing
11. **Add Performance Monitoring** - Track component render times and API latency
12. **Add Accessibility Tests** - Ensure WCAG compliance

---

## 📊 TEST COVERAGE GOALS

- **Unit Tests**: 80% coverage minimum
- **Integration Tests**: Critical user flows (verify candidate, compare, batch upload)
- **E2E Tests**: Happy path + error scenarios for each feature

---

## 🚀 CONCLUSION

The application has **6 critical bugs** primarily related to:
1. API endpoint mismatches between frontend and backend
2. Missing input validation and sanitization
3. Inadequate error handling

The provided mock data injection, unit tests, and edge case analysis should help rapidly identify and fix these issues. Priority should be given to fixing the God Mode data flow as it's currently completely broken.

**Estimated Fix Time**: 4-6 hours for all P0 issues.

---

**Report Generated**: December 18, 2025  
**Next Review**: After implementing P0 fixes
