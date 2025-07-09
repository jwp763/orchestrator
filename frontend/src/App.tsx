import { AlertCircle, Calendar, Check, ChevronDown, ChevronRight, Link, Plus, Tag, User, X } from 'lucide-react';
import { useEffect, useState } from 'react';

// Enums
const ProjectStatus = {
  PLANNING: 'PLANNING',
  ACTIVE: 'ACTIVE',
  ON_HOLD: 'ON_HOLD',
  COMPLETED: 'COMPLETED',
  ARCHIVED: 'ARCHIVED'
};

const Priority = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
  BACKLOG: 'BACKLOG'
};

const TaskStatus = {
  TODO: 'TODO',
  IN_PROGRESS: 'IN_PROGRESS',
  REVIEW: 'REVIEW',
  DONE: 'DONE',
  BLOCKED: 'BLOCKED'
};

// Helper functions
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    PLANNING: 'bg-gray-500',
    ACTIVE: 'bg-green-500',
    ON_HOLD: 'bg-yellow-500',
    COMPLETED: 'bg-blue-500',
    ARCHIVED: 'bg-gray-400',
    TODO: 'bg-gray-500',
    IN_PROGRESS: 'bg-yellow-500',
    REVIEW: 'bg-purple-500',
    DONE: 'bg-green-500',
    BLOCKED: 'bg-red-500'
  };
  return colors[status] || 'bg-gray-400';
};

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    CRITICAL: 'text-red-600 bg-red-50 border-red-200',
    HIGH: 'text-orange-600 bg-orange-50 border-orange-200',
    MEDIUM: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    LOW: 'text-green-600 bg-green-50 border-green-200',
    BACKLOG: 'text-gray-600 bg-gray-50 border-gray-200'
  };
  return colors[priority] || 'text-gray-600 bg-gray-50 border-gray-200';
};

// Sample data
const initialProjects = [
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

const initialTasks = [
  {
    id: '1',
    title: 'Create wireframes',
    description: 'Design low-fidelity wireframes for all major pages',
    project_id: '1',
    status: TaskStatus.IN_PROGRESS,
    priority: Priority.HIGH,
    parent_id: null,
    estimated_minutes: 240,
    actual_minutes: 180,
    dependencies: [],
    due_date: '2024-02-01',
    assignee: 'John Smith',
    tags: ['design', 'ux'],
    labels: [],
    motion_task_id: 'MOT-123',
    linear_issue_id: null,
    notion_task_id: null,
    gitlab_issue_id: null,
    metadata: {}
  },
  {
    id: '2',
    title: 'Implement responsive navigation',
    description: 'Build mobile-friendly navigation component',
    project_id: '1',
    status: TaskStatus.TODO,
    priority: Priority.MEDIUM,
    parent_id: null,
    estimated_minutes: 180,
    actual_minutes: 0,
    dependencies: ['1'],
    due_date: '2024-02-15',
    assignee: null,
    tags: ['frontend', 'component'],
    labels: [],
    motion_task_id: null,
    linear_issue_id: null,
    notion_task_id: null,
    gitlab_issue_id: null,
    metadata: {}
  },
  {
    id: '3',
    title: 'Set up authentication endpoints',
    description: 'Create REST endpoints for user login and registration',
    project_id: '2',
    status: TaskStatus.TODO,
    priority: Priority.HIGH,
    parent_id: null,
    estimated_minutes: 360,
    actual_minutes: 0,
    dependencies: [],
    due_date: '2024-03-01',
    assignee: 'Sarah Chen',
    tags: ['backend', 'auth'],
    labels: [],
    motion_task_id: null,
    linear_issue_id: 'LIN-456',
    notion_task_id: null,
    gitlab_issue_id: 'GL-789',
    metadata: {}
  }
];

// Components
const ProjectSidebar = ({ projects, selectedProject, onSelectProject, onNewProject }) => {
  const getTaskCount = (projectId) => {
    const projectTasks = initialTasks.filter(t => t.project_id === projectId);
    const completedTasks = projectTasks.filter(t => t.status === TaskStatus.DONE).length;
    return `${completedTasks}/${projectTasks.length}`;
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewProject}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {projects.map((project) => (
          <div
            key={project.id}
            onClick={() => onSelectProject(project)}
            className={`p-4 cursor-pointer hover:bg-gray-100 border-b border-gray-100 ${
              selectedProject?.id === project.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-gray-900 truncate flex-1">{project.name}</h3>
              <div className={`w-2 h-2 rounded-full mt-1.5 ${getStatusColor(project.status)}`} />
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">{getTaskCount(project.id)} tasks</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(project.priority)}`}>
                {project.priority}
              </span>
            </div>
            {project.due_date && new Date(project.due_date) < new Date() && (
              <div className="flex items-center gap-1 mt-2 text-red-600 text-xs">
                <AlertCircle className="w-3 h-3" />
                Overdue
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const ProjectDetails = ({ project, onUpdate, isCollapsed, onToggleCollapse }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedProject, setEditedProject] = useState(project);

  useEffect(() => {
    setEditedProject(project);
  }, [project]);

  const handleSave = () => {
    onUpdate(editedProject);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedProject(project);
    setIsEditing(false);
  };

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={onToggleCollapse}
              className="p-1 hover:bg-gray-100 rounded"
            >
              {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? (
                <input
                  type="text"
                  value={editedProject.name}
                  onChange={(e) => setEditedProject({ ...editedProject, name: e.target.value })}
                  className="border border-gray-300 rounded px-2 py-1"
                />
              ) : (
                project.name
              )}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  className="p-2 text-green-600 hover:bg-green-50 rounded"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={handleCancel}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
              >
                Edit
              </button>
            )}
          </div>
        </div>

        {!isCollapsed && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              {isEditing ? (
                <textarea
                  value={editedProject.description}
                  onChange={(e) => setEditedProject({ ...editedProject, description: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  rows={3}
                />
              ) : (
                <p className="text-gray-600">{project.description}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                {isEditing ? (
                  <select
                    value={editedProject.status}
                    onChange={(e) => setEditedProject({ ...editedProject, status: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                  >
                    {Object.values(ProjectStatus).map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                ) : (
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(project.status)}`} />
                    <span>{project.status}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                {isEditing ? (
                  <select
                    value={editedProject.priority}
                    onChange={(e) => setEditedProject({ ...editedProject, priority: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                  >
                    {Object.values(Priority).map(priority => (
                      <option key={priority} value={priority}>{priority}</option>
                    ))}
                  </select>
                ) : (
                  <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(project.priority)}`}>
                    {project.priority}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedProject.start_date || ''}
                    onChange={(e) => setEditedProject({ ...editedProject, start_date: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                  />
                ) : (
                  <span className="text-gray-600">{project.start_date || 'Not set'}</span>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedProject.due_date || ''}
                    onChange={(e) => setEditedProject({ ...editedProject, due_date: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                  />
                ) : (
                  <span className="text-gray-600">{project.due_date || 'Not set'}</span>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
              <div className="flex flex-wrap gap-2">
                {project.tags?.map((tag, index) => (
                  <span key={index} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                    <Tag className="w-3 h-3" />
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">External Links</label>
              <div className="flex flex-wrap gap-2">
                {project.motion_project_link && (
                  <a href={project.motion_project_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100">
                    <Link className="w-3 h-3" />
                    Motion
                  </a>
                )}
                {project.linear_project_link && (
                  <a href={project.linear_project_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-purple-50 text-purple-600 rounded hover:bg-purple-100">
                    <Link className="w-3 h-3" />
                    Linear
                  </a>
                )}
                {project.notion_page_link && (
                  <a href={project.notion_page_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                    <Link className="w-3 h-3" />
                    Notion
                  </a>
                )}
                {project.gitlab_project_link && (
                  <a href={project.gitlab_project_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-orange-50 text-orange-600 rounded hover:bg-orange-100">
                    <Link className="w-3 h-3" />
                    GitLab
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const TaskCard = ({ task, onClick, isSelected }) => {
  const getTimeProgress = () => {
    if (!task.estimated_minutes || !task.actual_minutes) return null;
    const percentage = Math.min((task.actual_minutes / task.estimated_minutes) * 100, 100);
    return percentage;
  };

  return (
    <div
      onClick={onClick}
      className={`p-4 bg-white border rounded-lg cursor-pointer transition-all ${
        isSelected ? 'border-blue-500 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-gray-900 flex-1">{task.title}</h3>
        <div className={`w-2 h-2 rounded-full mt-1.5 ${getStatusColor(task.status)}`} />
      </div>

      <div className="space-y-2">
        {task.description && (
          <p className="text-sm text-gray-600 line-clamp-2">{task.description}</p>
        )}

        <div className="flex items-center gap-4 text-sm">
          {task.assignee && (
            <div className="flex items-center gap-1 text-gray-600">
              <User className="w-3 h-3" />
              <span>{task.assignee}</span>
            </div>
          )}
          {task.due_date && (
            <div className="flex items-center gap-1 text-gray-600">
              <Calendar className="w-3 h-3" />
              <span>{task.due_date}</span>
            </div>
          )}
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(task.priority)}`}>
            {task.priority}
          </span>
        </div>

        {getTimeProgress() !== null && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>{task.actual_minutes}m / {task.estimated_minutes}m</span>
              <span>{Math.round(getTimeProgress())}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full"
                style={{ width: `${getTimeProgress()}%` }}
              />
            </div>
          </div>
        )}

        {task.tags && task.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {task.tags.map((tag, index) => (
              <span key={index} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const TaskDetails = ({ task, onClose, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState(task);

  const handleSave = () => {
    onUpdate(editedTask);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedTask(task);
    setIsEditing(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? (
                <input
                  type="text"
                  value={editedTask.title}
                  onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })}
                  className="w-full border border-gray-300 rounded px-2 py-1"
                />
              ) : (
                task.title
              )}
            </h2>
            <div className="flex items-center gap-2">
              {isEditing ? (
                <>
                  <button
                    onClick={handleSave}
                    className="p-2 text-green-600 hover:bg-green-50 rounded"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleCancel}
                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                  >
                    Edit
                  </button>
                  <button
                    onClick={onClose}
                    className="p-2 text-gray-500 hover:bg-gray-100 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            {isEditing ? (
              <textarea
                value={editedTask.description || ''}
                onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2"
                rows={3}
              />
            ) : (
              <p className="text-gray-600">{task.description || 'No description'}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              {isEditing ? (
                <select
                  value={editedTask.status}
                  onChange={(e) => setEditedTask({ ...editedTask, status: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                >
                  {Object.values(TaskStatus).map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              ) : (
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(task.status)}`} />
                  <span>{task.status}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              {isEditing ? (
                <select
                  value={editedTask.priority}
                  onChange={(e) => setEditedTask({ ...editedTask, priority: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                >
                  {Object.values(Priority).map(priority => (
                    <option key={priority} value={priority}>{priority}</option>
                  ))}
                </select>
              ) : (
                <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editedTask.assignee || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, assignee: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                />
              ) : (
                <span className="text-gray-600">{task.assignee || 'Unassigned'}</span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              {isEditing ? (
                <input
                  type="date"
                  value={editedTask.due_date || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, due_date: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                />
              ) : (
                <span className="text-gray-600">{task.due_date || 'Not set'}</span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Time</label>
              {isEditing ? (
                <input
                  type="number"
                  value={editedTask.estimated_minutes || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, estimated_minutes: parseInt(e.target.value) || null })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="Minutes"
                />
              ) : (
                <span className="text-gray-600">{task.estimated_minutes ? `${task.estimated_minutes} minutes` : 'Not set'}</span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Actual Time</label>
              {isEditing ? (
                <input
                  type="number"
                  value={editedTask.actual_minutes || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, actual_minutes: parseInt(e.target.value) || null })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="Minutes"
                />
              ) : (
                <span className="text-gray-600">{task.actual_minutes ? `${task.actual_minutes} minutes` : 'Not tracked'}</span>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <div className="flex flex-wrap gap-2">
              {task.tags?.map((tag, index) => (
                <span key={index} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                  <Tag className="w-3 h-3" />
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">External Links</label>
            <div className="flex flex-wrap gap-2">
              {task.motion_task_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-600 rounded text-sm">
                  <Link className="w-3 h-3" />
                  Motion: {task.motion_task_id}
                </span>
              )}
              {task.linear_issue_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-50 text-purple-600 rounded text-sm">
                  <Link className="w-3 h-3" />
                  Linear: {task.linear_issue_id}
                </span>
              )}
              {task.notion_task_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                  <Link className="w-3 h-3" />
                  Notion: {task.notion_task_id}
                </span>
              )}
              {task.gitlab_issue_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-orange-50 text-orange-600 rounded text-sm">
                  <Link className="w-3 h-3" />
                  GitLab: {task.gitlab_issue_id}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const NaturalLanguageEditor = ({ selectedProject, selectedTask, onApplyChanges }) => {
  const [input, setInput] = useState('');
  const [changes, setChanges] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const simulateNLProcessing = (text) => {
    // Simulate processing and generating changes
    setIsProcessing(true);
    setTimeout(() => {
      // Example changes based on simple keyword detection
      const simulatedChanges = [];

      if (text.toLowerCase().includes('high priority')) {
        simulatedChanges.push({
          type: 'project',
          field: 'priority',
          oldValue: selectedProject?.priority,
          newValue: Priority.HIGH,
          display: `priority: ${selectedProject?.priority} → HIGH`
        });
      }

      if (text.toLowerCase().includes('due next week')) {
        const nextWeek = new Date();
        nextWeek.setDate(nextWeek.getDate() + 7);
        simulatedChanges.push({
          type: 'project',
          field: 'due_date',
          oldValue: selectedProject?.due_date,
          newValue: nextWeek.toISOString().split('T')[0],
          display: `due_date: ${selectedProject?.due_date || 'None'} → ${nextWeek.toISOString().split('T')[0]}`
        });
      }

      if (text.toLowerCase().includes('assign to john')) {
        simulatedChanges.push({
          type: 'task',
          taskId: selectedTask?.id,
          field: 'assignee',
          oldValue: selectedTask?.assignee,
          newValue: 'John Smith',
          display: `assignee: ${selectedTask?.assignee || 'None'} → John Smith`
        });
      }

      setChanges(simulatedChanges);
      setIsProcessing(false);
    }, 1000);
  };

  const handleSubmit = () => {
    if (!input.trim()) return;
    simulateNLProcessing(input);
  };

  const handleApply = (change) => {
    onApplyChanges([change]);
    setChanges(changes.filter(c => c !== change));
  };

  const handleApplyAll = () => {
    onApplyChanges(changes);
    setChanges(null);
    setInput('');
  };

  const handleRejectAll = () => {
    setChanges(null);
    setInput('');
  };

  return (
    <div className="w-96 bg-gray-50 border-l border-gray-200 h-full flex flex-col">


      <div className="flex-1 flex flex-col p-4">
        <div className="mb-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe changes to make to the selected project or tasks e.g., 'Set priority to high and due date to next Friday' or 'Assign all frontend tasks to John'"
            className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isProcessing}
            className="w-full mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {isProcessing ? 'Processing...' : 'Generate Changes'}
          </button>
        </div>

        {changes && changes.length > 0 && (
          <div className="flex-1 overflow-y-auto">
            <div className="mb-3 flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Proposed Changes</h4>
              <div className="flex gap-2">
                <button
                  onClick={handleApplyAll}
                  className="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Apply All
                </button>
                <button
                  onClick={handleRejectAll}
                  className="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Reject All
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {changes.map((change, index) => (
                <div key={index} className="bg-white p-3 rounded-lg border border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-700 mb-1">
                        {change.type === 'project' ? 'Project' : `Task: ${change.taskId}`}
                      </div>
                      <div className="font-mono text-sm">
                        <span className="text-red-600">- {change.field}: {change.oldValue || 'None'}</span>
                        <br />
                        <span className="text-green-600">+ {change.field}: {change.newValue}</span>
                      </div>
                    </div>
                    <div className="flex gap-1 ml-2">
                      <button
                        onClick={() => handleApply(change)}
                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setChanges(changes.filter(c => c !== change))}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <h5 className="font-medium text-blue-900 mb-1">Example Commands:</h5>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• "Set priority to high and due next Friday"</li>
            <li>• "Assign all design tasks to Sarah"</li>
            <li>• "Mark wireframe task as complete"</li>
            <li>• "Add 2 hours to estimated time"</li>
            <li>• "Move all backlog items to active"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Main App Component
export default function ProjectTaskManager() {
  const [projects, setProjects] = useState(initialProjects);
  const [tasks, setTasks] = useState(initialTasks);
  const [selectedProject, setSelectedProject] = useState(projects[0]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isProjectCollapsed, setIsProjectCollapsed] = useState(false);

  const handleNewProject = () => {
    const newProject = {
      id: Date.now().toString(),
      name: 'New Project',
      description: '',
      status: ProjectStatus.PLANNING,
      priority: Priority.MEDIUM,
      tags: [],
      due_date: '2024-12-31',
      start_date: new Date().toISOString().split('T')[0],
      motion_project_link: null,
      linear_project_link: null,
      notion_page_link: null,
      gitlab_project_link: null
    };
    setProjects([...projects, newProject]);
    setSelectedProject(newProject);
  };

  const handleUpdateProject = (updatedProject) => {
    setProjects(projects.map(p => p.id === updatedProject.id ? updatedProject : p));
    setSelectedProject(updatedProject);
  };

  const handleUpdateTask = (updatedTask) => {
    setTasks(tasks.map(t => t.id === updatedTask.id ? updatedTask : t));
    setSelectedTask(updatedTask);
  };

  const handleApplyNLChanges = (changes) => {
    // Apply changes from NL editor
    changes.forEach(change => {
      if (change.type === 'project') {
        const updated = { ...selectedProject, [change.field]: change.newValue };
        handleUpdateProject(updated);
      } else if (change.type === 'task' && change.taskId) {
        const task = tasks.find(t => t.id === change.taskId);
        if (task) {
          const updated = { ...task, [change.field]: change.newValue };
          handleUpdateTask(updated);
        }
      }
    });
  };

  const projectTasks = tasks.filter(task => task.project_id === selectedProject?.id);

  return (
    <div className="h-screen flex bg-gray-100">
      <ProjectSidebar
        projects={projects}
        selectedProject={selectedProject}
        onSelectProject={setSelectedProject}
        onNewProject={handleNewProject}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        {selectedProject && (
          <>
            <ProjectDetails
              project={selectedProject}
              onUpdate={handleUpdateProject}
              isCollapsed={isProjectCollapsed}
              onToggleCollapse={() => setIsProjectCollapsed(!isProjectCollapsed)}
            />

            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Tasks</h3>
                <button
                  onClick={() => {
                    const newTask = {
                      id: Date.now().toString(),
                      title: 'New Task',
                      description: '',
                      project_id: selectedProject.id,
                      status: TaskStatus.TODO,
                      priority: Priority.MEDIUM,
                      parent_id: null,
                      estimated_minutes: null,
                      actual_minutes: 0,
                      dependencies: [],
                      due_date: null,
                      assignee: null,
                      tags: [],
                      labels: [],
                      motion_task_id: null,
                      linear_issue_id: null,
                      notion_task_id: null,
                      gitlab_issue_id: null,
                      metadata: {}
                    };
                    setTasks([...tasks, newTask]);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add Task
                </button>
              </div>

              <div className="grid gap-4">
                {projectTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onClick={() => setSelectedTask(task)}
                    isSelected={selectedTask?.id === task.id}
                  />
                ))}
                {projectTasks.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    No tasks yet. Create your first task to get started.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>

      <NaturalLanguageEditor
        selectedProject={selectedProject}
        selectedTask={selectedTask}
        onApplyChanges={handleApplyNLChanges}
      />

      {selectedTask && (
        <TaskDetails
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onUpdate={handleUpdateTask}
        />
      )}
    </div>
  );
}
