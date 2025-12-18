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
          candidate2: { name: 'Divya', trust_score: 90 },
          winner: 'Divya'
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
    
    const inputs = screen.getAllByPlaceholderText(/Candidate \d ID/i);
    fireEvent.change(inputs[0], { target: { value: 'cand_123' } });
    fireEvent.change(inputs[1], { target: { value: 'cand_456' } });
    
    fireEvent.click(screen.getByText('Compare Now'));
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      // Use getAllByText since 'Divya Smith' appears in multiple places (winner card + candidate card)
      const divyaElements = screen.getAllByText('Divya Smith');
      expect(divyaElements.length).toBeGreaterThan(0);
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
