import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CompareCandidates from '../src/components/CompareCandidates';
import '@testing-library/jest-dom';

describe('CompareCandidates Component', () => {
  beforeEach(() => {
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
    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    expect(input1).toBeInTheDocument();
    expect(input2).toBeInTheDocument();
  });

  it('should show inline error when Compare button clicked with empty fields', async () => {
    render(<CompareCandidates />);

    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);

    await waitFor(() => {
      expect(screen.getByText('Please enter both candidate IDs')).toBeInTheDocument();
    });
  });

  it('should show inline error when only one field is filled', async () => {
    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    fireEvent.change(input1, { target: { value: 'cand_123' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText('Please enter both candidate IDs')).toBeInTheDocument();
    });
  });

  it('should show error when same ID is entered twice', async () => {
    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'CAND-001' } });
    fireEvent.change(input2, { target: { value: 'CAND-001' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText(/Cannot compare a candidate with themselves/i)).toBeInTheDocument();
    });
  });

  it('should disable Compare button during loading', async () => {
    global.fetch = vi.fn(() => new Promise(() => {})); // Never resolves

    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'cand_123' } });
    fireEvent.change(input2, { target: { value: 'cand_456' } });

    const compareButton = screen.getByText('Compare Now');
    fireEvent.click(compareButton);

    await waitFor(() => {
      expect(screen.getByText('Comparing...')).toBeInTheDocument();
      expect(compareButton).toBeDisabled();
    });
  });

  it('should call API with GET and correct query params when both IDs are provided', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({
          candidate1: { name: 'John', trust_score: 85 },
          candidate2: { name: 'Divya', trust_score: 90 },
          winner: 'Divya'
        })
      })
    );

    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'cand_123' } });
    fireEvent.change(input2, { target: { value: 'cand_456' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      // Component uses GET with query params: candidate_a and candidate_b
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/compare?'),
        expect.objectContaining({
          method: 'GET'
        })
      );
      const calledUrl = global.fetch.mock.calls[0][0];
      expect(calledUrl).toContain('candidate_a=cand_123');
      expect(calledUrl).toContain('candidate_b=cand_456');
    });
  });

  it('should display inline error on 404 API response', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404
      })
    );

    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'invalid_id' } });
    fireEvent.change(input2, { target: { value: 'cand_456' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText('One or both candidate IDs not found')).toBeInTheDocument();
    });
  });

  it('should display inline error on non-404 API failure', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500
      })
    );

    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'cand_123' } });
    fireEvent.change(input2, { target: { value: 'cand_456' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText(/Failed to compare candidates/i)).toBeInTheDocument();
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
            name: 'Divya Smith',
            role: 'Lead Dev',
            trust_score: 92,
            experience: 7,
            skills_match: 88
          },
          winner: 'Divya Smith'
        })
      })
    );

    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'cand_123' } });
    fireEvent.change(input2, { target: { value: 'cand_456' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      const divyaElements = screen.getAllByText('Divya Smith');
      expect(divyaElements.length).toBeGreaterThan(0);
      expect(screen.getByText('Recommended Candidate')).toBeInTheDocument();
    });
  });

  it('should show inline error when inputs are only whitespace', async () => {
    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: '   ' } });
    fireEvent.change(input2, { target: { value: '   ' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText('Please enter both candidate IDs')).toBeInTheDocument();
    });
  });

  it('should handle network errors gracefully with inline error', async () => {
    global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

    render(<CompareCandidates />);

    const input1 = screen.getByPlaceholderText('e.g., CAND-A1B2');
    const input2 = screen.getByPlaceholderText('e.g., CAND-E5F6');
    fireEvent.change(input1, { target: { value: 'cand_123' } });
    fireEvent.change(input2, { target: { value: 'cand_456' } });

    fireEvent.click(screen.getByText('Compare Now'));

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });
  });
});
