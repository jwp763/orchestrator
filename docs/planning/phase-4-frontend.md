# Phase 4: Frontend Interface

*Last Updated: 2025-01-11*

**Status**: 🔄 In Progress  
**Estimated Time**: 6-8 hours  
**Current Progress**: Components built, API integration pending

## Goal

Build a React-based single-page application that provides an intuitive interface for conversational project management, featuring project visualization, task hierarchies, and AI-powered chat interactions.

## Current Implementation

### Completed Components ✅

**Location**: `frontend/src/`

#### 1. Project Sidebar
**File**: `components/ProjectSidebar/ProjectSidebar.tsx`

**Features**:
- Project list with search/filter
- Status indicators
- Quick actions (create, delete)
- Responsive design
- 100% test coverage

#### 2. Task Management
**Files**: `components/TaskCard/`, `components/TaskList/`

**Features**:
- Hierarchical task display
- Drag-and-drop support (planned)
- Status badges
- Time tracking display
- Priority indicators

#### 3. Natural Language Editor
**File**: `components/NaturalLanguageEditor/`

**Features**:
- Chat-like interface
- Markdown support
- Diff preview
- Command suggestions
- History tracking

#### 4. Custom Hooks
**Location**: `hooks/`

**Implemented**:
- `useProjectManagement`: Project CRUD operations
- `useLocalStorage`: Persistent state management
- `useDebounce`: Input optimization
- `useAsync`: Async operation handling

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── common/         # Shared UI components
│   │   ├── ProjectSidebar/ # Project navigation
│   │   ├── TaskCard/       # Task display
│   │   ├── TaskList/       # Task container
│   │   ├── ProjectDetails/ # Project info
│   │   └── NaturalLanguageEditor/ # AI chat
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API client layer
│   ├── types/              # TypeScript definitions
│   ├── utils/              # Helper functions
│   └── styles/             # Global styles
├── tests/                  # Test files
└── public/                 # Static assets
```

## Remaining Tasks

### Task 4.1: API Service Layer

**Files to Create**: `src/services/`

```typescript
// src/services/api.ts
class ApiClient {
  private baseURL: string;
  
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }
  
  async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    // Handle requests with error handling
  }
}

// src/services/projectService.ts
export const projectService = {
  async list(params?: ProjectFilters): Promise<ProjectList> {
    return api.get('/api/projects', { params });
  },
  
  async create(project: ProjectCreate): Promise<Project> {
    return api.post('/api/projects', project);
  },
  
  async update(id: string, updates: ProjectUpdate): Promise<Project> {
    return api.put(`/api/projects/${id}`, updates);
  }
};
```

### Task 4.2: State Management

**Approach**: React Context + Hooks

```typescript
// src/contexts/AppContext.tsx
interface AppState {
  projects: Project[];
  selectedProject: Project | null;
  tasks: Task[];
  conversation: Message[];
  isLoading: boolean;
}

const AppContext = React.createContext<AppState>();

export const AppProvider: React.FC = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};
```

### Task 4.3: Main Application Layout

**File**: `src/App.tsx`

```typescript
function App() {
  return (
    <AppProvider>
      <div className="app-container">
        <ProjectSidebar 
          className="sidebar"
          onProjectSelect={handleProjectSelect}
        />
        
        <main className="main-content">
          <ProjectHeader project={selectedProject} />
          
          <div className="workspace">
            <TaskList 
              tasks={tasks}
              onTaskSelect={handleTaskSelect}
            />
            
            <NaturalLanguageEditor
              onSubmit={handleChatSubmit}
              patches={pendingPatches}
            />
          </div>
        </main>
      </div>
    </AppProvider>
  );
}
```

### Task 4.4: AI Chat Integration

**Enhancement to NaturalLanguageEditor**:

```typescript
const NaturalLanguageEditor: React.FC<Props> = ({ onSubmit }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [patches, setPatches] = useState<PatchSet | null>(null);
  
  const handleSubmit = async () => {
    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    
    // Call API
    const response = await agentService.chat({
      message: input,
      context: getCurrentContext()
    });
    
    // Show AI response and patches
    setMessages([...messages, userMessage, response.message]);
    setPatches(response.patches);
  };
  
  const handleApplyPatches = async () => {
    await plannerService.applyPatches(patches);
    // Refresh UI
  };
};
```

### Task 4.5: Diff Visualization

**Component**: `src/components/DiffViewer/`

```typescript
interface DiffViewerProps {
  patches: PatchSet;
  onApprove: () => void;
  onReject: () => void;
}

const DiffViewer: React.FC<DiffViewerProps> = ({ patches }) => {
  return (
    <div className="diff-viewer">
      <h3>Proposed Changes</h3>
      
      {patches.project_patches.map(patch => (
        <div className={`patch ${patch.op}`}>
          <span className="op">{patch.op}</span>
          <pre>{JSON.stringify(patch.body, null, 2)}</pre>
        </div>
      ))}
      
      {patches.task_patches.map(patch => (
        <TaskPatchView patch={patch} />
      ))}
      
      <div className="actions">
        <button onClick={onApprove}>Apply Changes</button>
        <button onClick={onReject}>Cancel</button>
      </div>
    </div>
  );
};
```

### Task 4.6: Real-time Updates

**WebSocket Integration**:

```typescript
// src/hooks/useWebSocket.ts
export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [lastMessage, setLastMessage] = useState<any>(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
      
      // Handle different message types
      switch (data.type) {
        case 'PROJECT_UPDATE':
          dispatch({ type: 'UPDATE_PROJECT', payload: data.project });
          break;
        case 'TASK_UPDATE':
          dispatch({ type: 'UPDATE_TASK', payload: data.task });
          break;
      }
    };
    
    setSocket(ws);
    return () => ws.close();
  }, [url]);
  
  return { socket, lastMessage };
};
```

## UI/UX Design Principles

### 1. Conversational Flow
- Chat-first interface
- Clear message threading
- Visual diff previews
- One-click patch application

### 2. Information Hierarchy
- Projects → Tasks → Subtasks
- Collapsible sections
- Focus mode for deep work
- Breadcrumb navigation

### 3. Responsive Design
- Mobile-friendly sidebar
- Adaptive layouts
- Touch-friendly controls
- Offline capability

### 4. Accessibility
- ARIA labels
- Keyboard navigation
- Screen reader support
- High contrast mode

## Styling Approach

### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0066CC',
        secondary: '#6B7280',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444'
      }
    }
  }
};
```

### Component Styling

```typescript
// Consistent styling patterns
<div className="
  bg-white dark:bg-gray-800 
  rounded-lg shadow-md 
  p-4 hover:shadow-lg 
  transition-shadow
">
  {/* Component content */}
</div>
```

## Testing Strategy

### Current Test Coverage: 100%

**Test Categories**:
1. **Component Tests**: Rendering and interaction
2. **Hook Tests**: State management logic
3. **Integration Tests**: API interaction
4. **E2E Tests**: Full user workflows

**Example Test**:
```typescript
describe('ProjectSidebar', () => {
  it('displays projects and handles selection', async () => {
    const mockProjects = [createMockProject()];
    const onSelect = vi.fn();
    
    render(
      <ProjectSidebar 
        projects={mockProjects}
        onProjectSelect={onSelect}
      />
    );
    
    const project = screen.getByText(mockProjects[0].name);
    await userEvent.click(project);
    
    expect(onSelect).toHaveBeenCalledWith(mockProjects[0]);
  });
});
```

## Performance Optimization

### 1. Code Splitting
```typescript
const ProjectDetails = lazy(() => 
  import('./components/ProjectDetails')
);
```

### 2. Memoization
```typescript
const MemoizedTaskList = memo(TaskList, (prev, next) => 
  prev.tasks.length === next.tasks.length &&
  prev.selectedId === next.selectedId
);
```

### 3. Virtual Scrolling
```typescript
import { FixedSizeList } from 'react-window';

const VirtualTaskList = ({ tasks }) => (
  <FixedSizeList
    height={600}
    itemCount={tasks.length}
    itemSize={80}
  >
    {({ index, style }) => (
      <TaskCard task={tasks[index]} style={style} />
    )}
  </FixedSizeList>
);
```

## Build & Deployment

### Development
```bash
npm run dev          # Start dev server
npm run test         # Run tests
npm run test:watch   # Watch mode
npm run build        # Production build
```

### Production Build
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@headlessui/react', 'tailwindcss']
        }
      }
    }
  }
});
```

## Future Enhancements

### 1. Advanced Features
- Gantt chart visualization
- Kanban board view
- Time tracking integration
- File attachments

### 2. Collaboration
- Real-time cursors
- Comments and mentions
- Activity feed
- Team presence

### 3. Mobile App
- React Native implementation
- Offline sync
- Push notifications
- Voice input

## Related Documentation

- [Frontend Testing Guide](../testing/frontend-guide.md)
- [Component Library](../reference/components.md)
- [API Integration Guide](../development/api-integration.md)