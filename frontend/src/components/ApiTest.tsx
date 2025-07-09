import React, { useState } from 'react';
import { projectService } from '../services/projectService';
import { taskService } from '../services/taskService';

const ApiTest: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleLoadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await projectService.getProjects();
      if (response.success) {
        setProjects(response.data.projects);
        setSuccess('Projects loaded successfully!');
      } else {
        setError(response.error || 'Failed to load projects');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await projectService.createProject({
        name: `Test Project ${Date.now()}`,
        description: 'A test project created from the frontend',
        created_by: 'frontend-user',
      });
      
      if (response.success) {
        setSuccess('Project created successfully!');
        handleLoadProjects(); // Reload projects
      } else {
        setError(response.error || 'Failed to create project');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await taskService.getTasks();
      if (response.success) {
        setTasks(response.data.tasks);
        setSuccess('Tasks loaded successfully!');
      } else {
        setError(response.error || 'Failed to load tasks');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    if (projects.length === 0) {
      setError('Please create a project first');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await taskService.createTask({
        project_id: projects[0].id,
        title: `Test Task ${Date.now()}`,
        description: 'A test task created from the frontend',
        created_by: 'frontend-user',
      });
      
      if (response.success) {
        setSuccess('Task created successfully!');
        handleLoadTasks(); // Reload tasks
      } else {
        setError(response.error || 'Failed to create task');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>API Integration Test</h1>
      
      {loading && <div style={{ color: 'blue' }}>Loading...</div>}
      {error && <div style={{ color: 'red', margin: '10px 0' }}>Error: {error}</div>}
      {success && <div style={{ color: 'green', margin: '10px 0' }}>Success: {success}</div>}

      <div style={{ margin: '20px 0' }}>
        <h2>Projects</h2>
        <button onClick={handleLoadProjects} disabled={loading}>
          Load Projects
        </button>
        <button onClick={handleCreateProject} disabled={loading} style={{ marginLeft: '10px' }}>
          Create Test Project
        </button>
        
        <div style={{ margin: '10px 0' }}>
          <strong>Projects ({projects.length}):</strong>
          {projects.length === 0 ? (
            <div>No projects found</div>
          ) : (
            <ul>
              {projects.map((project) => (
                <li key={project.id}>
                  <strong>{project.name}</strong> ({project.status}) - {project.description}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div style={{ margin: '20px 0' }}>
        <h2>Tasks</h2>
        <button onClick={handleLoadTasks} disabled={loading}>
          Load Tasks
        </button>
        <button onClick={handleCreateTask} disabled={loading} style={{ marginLeft: '10px' }}>
          Create Test Task
        </button>
        
        <div style={{ margin: '10px 0' }}>
          <strong>Tasks ({tasks.length}):</strong>
          {tasks.length === 0 ? (
            <div>No tasks found</div>
          ) : (
            <ul>
              {tasks.map((task) => (
                <li key={task.id}>
                  <strong>{task.title}</strong> ({task.status}) - {task.description}
                  <br />
                  <small>Project: {task.project_id}</small>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div style={{ margin: '20px 0' }}>
        <h3>Instructions:</h3>
        <ol>
          <li>Click "Load Projects" to fetch projects from the API</li>
          <li>Click "Create Test Project" to create a new project</li>
          <li>Click "Load Tasks" to fetch tasks from the API</li>
          <li>Click "Create Test Task" to create a new task (requires at least one project)</li>
        </ol>
      </div>
    </div>
  );
};

export default ApiTest;