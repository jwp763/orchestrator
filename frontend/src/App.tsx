import { Plus } from 'lucide-react';
import { 
  ProjectSidebar, 
  ProjectDetails, 
  TaskCard, 
  TaskDetails, 
  NaturalLanguageEditor 
} from './components';
import { useProjectManagement } from './hooks';
import { mockProjects, mockTasks } from './mocks';

export default function App() {
  const {
    projects,
    tasks,
    selectedProject,
    selectedTask,
    isProjectCollapsed,
    handleProjectSelect,
    handleTaskSelect,
    handleNewProject,
    handleUpdateProject,
    handleUpdateTask,
    handleApplyChanges,
    handleToggleProjectCollapse,
    getTasksForProject,
  } = useProjectManagement(mockProjects, mockTasks);

  const currentProjectTasks = selectedProject ? getTasksForProject(selectedProject.id) : [];

  return (
    <div className="h-screen flex bg-gray-100">
      {/* Project Sidebar */}
      <ProjectSidebar
        projects={projects}
        selectedProject={selectedProject}
        onProjectSelect={handleProjectSelect}
        onAddProject={handleNewProject}
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
            <h3 className="text-lg font-semibold text-gray-900">Tasks</h3>
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
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
      <NaturalLanguageEditor
        selectedProject={selectedProject}
        selectedTask={selectedTask}
        onApplyChanges={handleApplyChanges}
      />

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