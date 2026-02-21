import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TrustPacketVisualization from '../src/components/TrustPacketVisualization';
import '@testing-library/jest-dom';

describe('TrustPacketVisualization Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('should render without crashing', () => {
    render(<TrustPacketVisualization />);
    expect(screen.getByText('Trust Packet Visualization')).toBeInTheDocument();
  });

  it('should have an input field for candidate ID', () => {
    render(<TrustPacketVisualization />);
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    expect(input).toBeInTheDocument();
  });

  it('should have a "Load Trust Packet" button', () => {
    render(<TrustPacketVisualization />);
    expect(screen.getByText('Load Trust Packet')).toBeInTheDocument();
  });

  it('should show inline error when Load button clicked with empty ID', async () => {
    render(<TrustPacketVisualization />);

    const loadButton = screen.getByText('Load Trust Packet');
    fireEvent.click(loadButton);

    await waitFor(() => {
      expect(screen.getByText('Please enter a candidate ID')).toBeInTheDocument();
    });
  });

  it('should show inline error when input is only whitespace', async () => {
    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: '   ' } });

    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(screen.getByText('Please enter a candidate ID')).toBeInTheDocument();
    });
  });

  it('should show "Loading..." and disable button while fetching', async () => {
    global.fetch = vi.fn(() => new Promise(() => {})); // Never resolves

    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'CAND-001' } });

    const loadButton = screen.getByText('Load Trust Packet');
    fireEvent.click(loadButton);

    await waitFor(() => {
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.getByText('Loading...')).toBeDisabled();
    });
  });

  it('should call the enhanced trust-packet API with correct candidate ID', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          candidate_id: 'CAND-001',
          credentials: [],
          blockchain: null,
          verification_summary: {}
        })
      })
    );

    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'CAND-001' } });
    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/trust-packet/CAND-001/enhanced')
      );
    });
  });

  it('should trigger fetch on Enter key press', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          candidate_id: 'CAND-001',
          credentials: [],
          blockchain: null,
          verification_summary: {}
        })
      })
    );

    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'CAND-001' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/trust-packet/CAND-001/enhanced')
      );
    });
  });

  it('should display inline error with API detail message on failure', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Candidate not found' })
      })
    );

    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'INVALID' } });
    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(screen.getByText('Candidate not found')).toBeInTheDocument();
    });
  });

  it('should display fallback error message on non-JSON API failure', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: async () => { throw new Error('Not JSON'); }
      })
    );

    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'CAND-001' } });
    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(screen.getByText(/Error 500/)).toBeInTheDocument();
    });
  });

  it('should display network error message on fetch rejection', async () => {
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

    render(<TrustPacketVisualization />);

    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'CAND-001' } });
    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(screen.getByText('Network error. Please check your connection.')).toBeInTheDocument();
    });
  });

  it('should reset error state on new search', async () => {
    // First call fails
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' })
      })
    );

    render(<TrustPacketVisualization />);
    const input = screen.getByPlaceholderText(/Enter Candidate ID/i);
    fireEvent.change(input, { target: { value: 'BAD' } });
    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(screen.getByText('Not found')).toBeInTheDocument();
    });

    // Second call succeeds — error should be cleared
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          candidate_id: 'CAND-001',
          credentials: [],
          blockchain: null,
          verification_summary: {}
        })
      })
    );

    fireEvent.change(input, { target: { value: 'CAND-001' } });
    fireEvent.click(screen.getByText('Load Trust Packet'));

    await waitFor(() => {
      expect(screen.queryByText('Not found')).not.toBeInTheDocument();
    });
  });
});
