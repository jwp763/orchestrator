import { Plus, AlertCircle, Loader2 } from 'lucide-react';
import { 
  ProjectSidebar, 
  ProjectDetails, 
  TaskCard, 
  TaskDetails, 
  NaturalLanguageEditor 
} from './components';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useProjectManagement } from './hooks';

export default function App() {
  const {
    projects,
    tasks,
    selectedProject,
    selectedTask,
    isProjectCollapsed,
    isLoading,
    projectsLoading,
    tasksLoading,
    error,
    handleProjectSelect,
    handleTaskSelect,
    handleNewProject,
    handleUpdateProject,
    handleNewTask,
    handleUpdateTask,
    handleApplyChanges,
    handleToggleProjectCollapse,
    clearError,
    getTasksForProject,
  } = useProjectManagement();

  const currentProjectTasks = selectedProject ? getTasksForProject(selectedProject.id) : [];

  const handleAddProject = () => {
    // TODO: Open project creation modal
    // For now, create a basic project
    handleNewProject({
      name: 'New Project',
      description: 'Project created from UI',
      status: 'planning',
      priority: 'medium',
      tags: [],
    });
  };

  const handleAddTask = () => {
    if (!selectedProject) return;
    
    // TODO: Open task creation modal
    // For now, create a basic task
    handleNewTask({
      project_id: selectedProject.id,
      title: 'New Task',
      description: 'Task created from UI',
      status: 'todo',
      priority: 'medium',
      tags: [],
      sort_order: currentProjectTasks.length,
      completion_percentage: 0,
      dependencies: [],
      metadata: {},
    });
  };

  return (
    <div className="h-screen flex bg-gray-100">
      {/* Error Display */}
      {error && (
        <div className="fixed top-4 right-4 z-50 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
            <button
              onClick={clearError}
              className="ml-2 text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Global Loading Overlay */}
      {(projectsLoading && projects.length === 0) && (
        <div className="fixed inset-0 bg-black bg-opacity-25 z-40 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-lg flex items-center gap-3">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading projects...</span>
          </div>
        </div>
      )}

      {/* Project Sidebar */}
      <ProjectSidebar
        projects={projects}
        selectedProject={selectedProject}
        onProjectSelect={handleProjectSelect}
        onAddProject={handleAddProject}
        tasks={tasks}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Project Details */}
        {selectedProject && (
          <ProjectDetails
            project={selectedProject}
            onUpdate={handleUpdateProject}
            isCollapsed={isProjectCollapsed}
            onToggleCollapse={handleToggleProjectCollapse}
          />
        )}

        {/* Tasks Section */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Tasks
              {tasksLoading && (
                <Loader2 className="w-4 h-4 animate-spin inline ml-2" />
              )}
            </h3>
            <button 
              onClick={handleAddTask}
              disabled={!selectedProject || isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="w-4 h-4" />
              Add Task
            </button>
          </div>

          {currentProjectTasks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p>No tasks found for this project.</p>
              <p className="text-sm mt-2">Click "Add Task" to create your first task.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {currentProjectTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onClick={() => handleTaskSelect(task)}
                  isSelected={selectedTask?.id === task.id}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Natural Language Editor */}
      <ErrorBoundary
        fallback={
          <div className="w-96 bg-gray-50 border-l border-gray-200 h-full p-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-red-800 font-medium">Natural Language Editor Error</h3>
              <p className="text-red-600 text-sm mt-2">
                Failed to load the Natural Language Editor. Please refresh the page.
              </p>
            </div>
          </div>
        }
      >
        <NaturalLanguageEditor
          selectedProject={selectedProject}
          selectedTask={selectedTask}
          onApplyChanges={handleApplyChanges}
        />
      </ErrorBoundary>

      {/* Task Details Modal */}
      {selectedTask && (
        <TaskDetails
          task={selectedTask}
          onClose={() => handleTaskSelect(null)}
          onUpdate={handleUpdateTask}
        />
      )}
    </div>
  );
}