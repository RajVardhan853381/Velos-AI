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

    // Track download calls
    const mockClick = vi.fn();
    let capturedDownload = '';
    
    // Mock createElement to only mock 'a' elements
    const originalCreateElement = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tagName) => {
      if (tagName === 'a') {
        const link = originalCreateElement('a');
        link.click = mockClick;
        Object.defineProperty(link, 'download', {
          set: (value) => { capturedDownload = value; },
          get: () => capturedDownload
        });
        return link;
      }
      return originalCreateElement(tagName);
    });

    render(<TrustPacket />);
    
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'cand_123' } });
    fireEvent.click(screen.getByText('Fetch Packet'));
    
    await waitFor(() => screen.getByText('Download Dossier'));
    fireEvent.click(screen.getByText('Download Dossier'));
    
    await waitFor(() => {
      expect(mockClick).toHaveBeenCalled();
      expect(capturedDownload).toBe('cand_123_dossier.json');
    });
  });
});
