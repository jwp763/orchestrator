import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NaturalLanguageEditor } from './NaturalLanguageEditor';
import { getPlannerService } from '../../services/plannerService';
import type { Project, Task } from '../../types';
import type { ProviderInfo } from '../../types/api';

// Mock the planner service
vi.mock('../../services/plannerService');

describe('NaturalLanguageEditor', () => {
  const mockOnApplyChanges = vi.fn();
  const mockProject: Project = {
    id: 'proj-1',
    name: 'Test Project',
    description: 'A test project',
    status: 'ACTIVE',
    priority: 'MEDIUM',
    tags: [],
    due_date: '2025-12-31',
    start_date: '2025-01-01',
    motion_project_link: null,
    linear_project_link: null,
    notion_page_link: null,
    gitlab_project_link: null,
  };

  const mockProviders: ProviderInfo[] = [
    {
      name: 'openai',
      display_name: 'OpenAI',
      models: [
        {
          name: 'gpt-4',
          display_name: 'GPT-4',
          is_default: true,
        },
      ],
      is_available: true,
      is_default: false,
    },
    {
      name: 'anthropic',
      display_name: 'Anthropic',
      models: [
        {
          name: 'claude-3',
          display_name: 'Claude 3',
          is_default: true,
        },
      ],
      is_available: false,
      is_default: true,
    },
  ];

  let mockPlannerService: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockPlannerService = {
      getProviders: vi.fn(),
      generatePlan: vi.fn(),
    };
    vi.mocked(getPlannerService).mockReturnValue(mockPlannerService);
  });

  describe('Provider Loading', () => {
    it('should show loading state initially', () => {
      mockPlannerService.getProviders.mockReturnValue(new Promise(() => {})); // Never resolves

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      expect(screen.getByText('Loading providers...')).toBeInTheDocument();
    });

    it('should display providers after loading', async () => {
      mockPlannerService.getProviders.mockResolvedValue({
        success: true,
        data: { providers: mockProviders },
      });

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      await waitFor(() => {
        // Anthropic is default provider
        expect(screen.getByRole('button', { name: /Anthropic/i })).toBeInTheDocument();
      });
    });

    it('should show error message when provider loading fails', async () => {
      mockPlannerService.getProviders.mockResolvedValue({
        success: false,
        error: 'Failed to load providers',
      });

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Failed to load providers')).toBeInTheDocument();
      });
    });
  });

  describe('Provider Selection', () => {
    it('should allow changing providers', async () => {
      mockPlannerService.getProviders.mockResolvedValue({
        success: true,
        data: { providers: mockProviders },
      });

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      await waitFor(() => {
        expect(screen.getByTestId('provider-dropdown-button')).toBeInTheDocument();
      });

      // Open dropdown
      fireEvent.click(screen.getByTestId('provider-dropdown-button'));

      // Select OpenAI
      fireEvent.click(screen.getByTestId('provider-option-openai'));

      // Check that OpenAI is now shown
      expect(screen.getByRole('button', { name: /OpenAI/i })).toBeInTheDocument();
    });
  });

  describe('Generation', () => {
    it('should generate plan when clicking generate', async () => {
      const user = userEvent.setup();
      
      mockPlannerService.getProviders.mockResolvedValue({
        success: true,
        data: { providers: mockProviders },
      });

      mockPlannerService.generatePlan.mockResolvedValue({
        success: true,
        data: {
          success: true,
          project: {
            name: 'Test Generated Project',
            description: 'A generated project',
            status: 'planning',
            priority: 'medium',
            tags: [],
          },
          tasks: [],
        },
      });

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      // Wait for providers to load
      await waitFor(() => {
        expect(screen.getByTestId('provider-dropdown-button')).toBeInTheDocument();
      });

      // Select OpenAI (which is available)
      fireEvent.click(screen.getByTestId('provider-dropdown-button'));
      fireEvent.click(screen.getByTestId('provider-option-openai'));

      // Type in textarea
      const textarea = screen.getByPlaceholderText(/Describe your project idea/i);
      await user.type(textarea, 'Create a test project');

      // Click generate
      const generateButton = screen.getByRole('button', { name: /Generate Changes/i });
      await user.click(generateButton);

      // Wait for generation to complete - look for the display text or the value
      await waitFor(() => {
        expect(screen.getByText(/Test Generated Project/)).toBeInTheDocument();
      });

      expect(mockPlannerService.generatePlan).toHaveBeenCalledWith({
        idea: 'Create a test project',
        config: expect.objectContaining({
          provider: 'openai',
        }),
        context: expect.any(Object),
      });
    });

    it('should show error when generation fails', async () => {
      const user = userEvent.setup();
      
      mockPlannerService.getProviders.mockResolvedValue({
        success: true,
        data: { providers: mockProviders },
      });

      mockPlannerService.generatePlan.mockResolvedValue({
        success: false,
        error: 'Generation failed',
      });

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      await waitFor(() => {
        expect(screen.getByTestId('provider-dropdown-button')).toBeInTheDocument();
      });

      // Select OpenAI
      fireEvent.click(screen.getByTestId('provider-dropdown-button'));
      fireEvent.click(screen.getByTestId('provider-option-openai'));

      const textarea = screen.getByPlaceholderText(/Describe your project idea/i);
      await user.type(textarea, 'Test');

      const generateButton = screen.getByRole('button', { name: /Generate Changes/i });
      await user.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Generation failed')).toBeInTheDocument();
      });
    });
  });

  describe('Change Application', () => {
    it('should call onApplyChanges when applying changes', async () => {
      const user = userEvent.setup();
      
      mockPlannerService.getProviders.mockResolvedValue({
        success: true,
        data: { providers: mockProviders },
      });

      mockPlannerService.generatePlan.mockResolvedValue({
        success: true,
        data: {
          success: true,
          project: { name: 'Test Project' },
          tasks: [],
        },
      });

      render(
        <NaturalLanguageEditor
          selectedProject={mockProject}
          selectedTask={null}
          onApplyChanges={mockOnApplyChanges}
        />
      );

      await waitFor(() => {
        expect(screen.getByTestId('provider-dropdown-button')).toBeInTheDocument();
      });

      // Select OpenAI and generate
      fireEvent.click(screen.getByTestId('provider-dropdown-button'));
      fireEvent.click(screen.getByTestId('provider-option-openai'));

      const textarea = screen.getByPlaceholderText(/Describe your project idea/i);
      await user.type(textarea, 'Test');

      const generateButton = screen.getByRole('button', { name: /Generate Changes/i });
      await user.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Apply All')).toBeInTheDocument();
      });

      // Apply all changes
      const applyAllButton = screen.getByText('Apply All');
      await user.click(applyAllButton);

      expect(mockOnApplyChanges).toHaveBeenCalledWith([
        expect.objectContaining({
          type: 'project',
          field: 'name',
          newValue: 'Test Project',
          oldValue: null,
          display: 'Create project: Test Project',
        }),
      ]);
    });
  });
});