import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { MetricCard } from '../components/ui/MetricCard';

describe('UI Component Suite', () => {
  it('renders StatusBadge with correct variant and text', () => {
    render(<StatusBadge status="VERIFIED" />);
    expect(screen.getByText('VERIFIED')).toBeInTheDocument();
  });

  it('renders MetricCard with title, value, and subtitle', () => {
    render(
      <MetricCard
        title="Total Repairs"
        value={42}
        subtitle="Active tests passing"
      />
    );
    expect(screen.getByText('Total Repairs')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('Active tests passing')).toBeInTheDocument();
  });
});
