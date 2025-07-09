import type { Project } from '../types';
import { ProjectStatus, Priority } from '../types';

export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Website Redesign',
    description: 'Complete overhaul of the company website with modern design principles and improved user experience. This includes updating the design system, implementing responsive layouts, and optimizing performance.',
    status: ProjectStatus.ACTIVE,
    priority: Priority.HIGH,
    tags: ['frontend', 'design', 'ux'],
    due_date: '2024-03-15',
    start_date: '2024-01-10',
    motion_project_link: 'https://motion.com/project/123',
    linear_project_link: null,
    notion_page_link: 'https://notion.so/page/456',
    gitlab_project_link: null
  },
  {
    id: '2',
    name: 'API Integration',
    description: 'Integrate third-party APIs for payment processing and user authentication.',
    status: ProjectStatus.PLANNING,
    priority: Priority.MEDIUM,
    tags: ['backend', 'api'],
    due_date: '2024-04-01',
    start_date: '2024-03-01',
    motion_project_link: null,
    linear_project_link: 'https://linear.app/project/789',
    notion_page_link: null,
    gitlab_project_link: 'https://gitlab.com/project/101'
  }
];