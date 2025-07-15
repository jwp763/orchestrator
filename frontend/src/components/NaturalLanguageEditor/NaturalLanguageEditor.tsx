import React, { useState, useEffect } from 'react';
import { Check, X, ChevronDown, AlertCircle } from 'lucide-react';
import type { Change, NaturalLanguageEditorProps } from '../../types';
import { getPlannerService } from '../../services/plannerService';
import type { ProviderInfo } from '../../types/api';
import { parseResponseToChanges } from '../../utils/patchParser';

export const NaturalLanguageEditor: React.FC<NaturalLanguageEditorProps> = ({
  selectedProject,
  selectedTask,
  onApplyChanges,
}) => {
  const [input, setInput] = useState('');
  const [changes, setChanges] = useState<Change[] | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Provider selection state
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [providerError, setProviderError] = useState<string | null>(null);
  const [showProviderDropdown, setShowProviderDropdown] = useState(false);
  
  // Fetch providers on mount
  useEffect(() => {
    const fetchProviders = async () => {
      console.log('NaturalLanguageEditor: Starting provider fetch...');
      try {
        setLoadingProviders(true);
        const service = getPlannerService();
        console.log('NaturalLanguageEditor: Got planner service:', service);
        
        const result = await service.getProviders();
        console.log('NaturalLanguageEditor: Provider fetch result:', result);
        
        if (result && result.success && result.data) {
          const providerList = result.data.providers || [];
          console.log('NaturalLanguageEditor: Setting providers:', providerList);
          setProviders(providerList);
          
          // Set default provider
          const defaultProvider = providerList.find(p => p.is_default);
          if (defaultProvider) {
            setSelectedProvider(defaultProvider.name);
          } else if (providerList.length > 0) {
            setSelectedProvider(providerList[0].name);
          }
        } else {
          const errorMsg = result?.error || 'Failed to load providers';
          console.log('NaturalLanguageEditor: Provider fetch failed:', errorMsg);
          setProviderError(errorMsg);
          setProviders([]); // Ensure providers is always an array
        }
      } catch (error) {
        console.error('NaturalLanguageEditor: Exception fetching providers:', error);
        setProviderError('Failed to connect to server');
        setProviders([]); // Ensure providers is always an array
      } finally {
        setLoadingProviders(false);
      }
    };
    
    fetchProviders();
  }, []);

  const generateProjectPlan = async (text: string) => {
    setIsProcessing(true);
    setChanges(null);
    
    try {
      const service = getPlannerService();
      
      // Build context from selected project/task
      const context: Record<string, any> = {};
      if (selectedProject) {
        context.project = {
          id: selectedProject.id,
          name: selectedProject.name,
          description: selectedProject.description,
          status: selectedProject.status,
          priority: selectedProject.priority
        };
      }
      if (selectedTask) {
        context.task = {
          id: selectedTask.id,
          title: selectedTask.title,
          description: selectedTask.description,
          status: selectedTask.status,
          priority: selectedTask.priority
        };
      }
      
      // Call the planner API
      const result = await service.generatePlan({
        idea: text,
        config: {
          provider: selectedProvider as 'openai' | 'anthropic' | 'gemini' | 'xai',
          create_milestones: true,
          max_milestones: 5,
          max_retries: 2
        },
        context
      });
      
      if (result.success && result.data) {
        // Parse the response into Change objects for display
        const parsedChanges = parseResponseToChanges(result.data);
        setChanges(parsedChanges);
      } else {
        // Show error in changes area
        setChanges([{
          type: 'error',
          field: 'error',
          oldValue: null,
          newValue: result.error || 'Generation failed',
          display: `Error: ${result.error || 'Failed to generate project plan'}`
        }]);
      }
    } catch (error) {
      console.error('Generation error:', error);
      setChanges([{
        type: 'error',
        field: 'error',
        oldValue: null,
        newValue: 'Network error',
        display: `Error: Failed to connect to server`
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSubmit = () => {
    if (!input.trim()) return;
    
    // Check if we have a valid provider selected
    if (!selectedProvider || providers.length === 0) {
      setChanges([{
        type: 'error',
        field: 'error', 
        oldValue: null,
        newValue: 'No provider selected',
        display: 'Error: Please select an AI provider first'
      }]);
      return;
    }
    
    // Check if the selected provider is available
    const provider = providers.find(p => p.name === selectedProvider);
    if (provider && !provider.is_available) {
      setChanges([{
        type: 'error',
        field: 'error',
        oldValue: null,
        newValue: 'Provider unavailable',
        display: `Error: ${provider.display_name} requires API key configuration`
      }]);
      return;
    }
    
    generateProjectPlan(input);
  };

  const handleApply = (change: Change) => {
    onApplyChanges([change]);
    setChanges(changes ? changes.filter(c => c !== change) : null);
  };

  const handleApplyAll = () => {
    if (changes) {
      // Filter out error changes
      const validChanges = changes.filter(c => c.type !== 'error');
      if (validChanges.length > 0) {
        onApplyChanges(validChanges);
        setChanges(null);
        setInput('');
      }
    }
  };

  const handleRejectAll = () => {
    setChanges(null);
    setInput('');
  };

  // Debug logging
  console.log('NaturalLanguageEditor render state:', {
    loadingProviders,
    providerError,
    providers: providers.length,
    selectedProvider,
    showProviderDropdown
  });

  try {
    return (
      <div className="w-96 bg-gray-50 border-l border-gray-200 h-full flex flex-col">
      <div className="flex-1 flex flex-col p-4">
        <div className="mb-4">
          {/* Provider Selection */}
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              AI Provider
            </label>
            {loadingProviders ? (
              <div className="flex items-center justify-center py-2 text-sm text-gray-500">
                Loading providers...
              </div>
            ) : providerError ? (
              <div className="flex items-center gap-2 p-2 bg-red-50 text-red-700 rounded-lg text-sm">
                <AlertCircle className="w-4 h-4" />
                {providerError}
              </div>
            ) : providers.length === 0 ? (
              <div className="flex items-center gap-2 p-2 bg-amber-50 text-amber-700 rounded-lg text-sm">
                <AlertCircle className="w-4 h-4" />
                No AI providers available. Using simulation mode.
              </div>
            ) : (
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowProviderDropdown(!showProviderDropdown)}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg flex items-center justify-between hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="provider-dropdown-button"
                >
                  <span className="flex items-center gap-2">
                    {selectedProvider ? (
                      <>
                        <span className="font-medium">
                          {providers.find(p => p.name === selectedProvider)?.display_name || selectedProvider}
                        </span>
                        {!providers.find(p => p.name === selectedProvider)?.is_available && (
                          <span className="text-xs text-amber-600">(No API Key)</span>
                        )}
                      </>
                    ) : (
                      <span className="text-gray-500">Select a provider</span>
                    )}
                  </span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${showProviderDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showProviderDropdown && providers.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                    {providers.map((provider) => (
                      <button
                        key={provider.name}
                        type="button"
                        onClick={() => {
                          setSelectedProvider(provider.name);
                          setShowProviderDropdown(false);
                        }}
                        className={`w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center justify-between ${
                          provider.name === selectedProvider ? 'bg-blue-50' : ''
                        }`}
                        data-testid={`provider-option-${provider.name}`}
                      >
                        <span className="flex items-center gap-2">
                          <span className="font-medium">{provider.display_name}</span>
                          {provider.is_default && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Default</span>
                          )}
                        </span>
                        {!provider.is_available && (
                          <span className="text-xs text-amber-600">No API Key</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
          
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your project idea or changes to make..."
            className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="nl-input"
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isProcessing || loadingProviders || providers.length === 0}
            className="w-full mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            data-testid="generate-changes-button"
          >
            {isProcessing ? 'Generating with AI... (this may take 10-20 seconds)' : 'Generate Changes'}
          </button>
        </div>

        {changes && changes.length > 0 && (
          <div className="flex-1 overflow-y-auto">
            <div className="mb-3 flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Proposed Changes</h4>
              {changes.some(c => c.type !== 'error') && (
                <div className="flex gap-2">
                  <button
                    onClick={handleApplyAll}
                    className="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                    data-testid="apply-all-button"
                  >
                    Apply All
                  </button>
                  <button
                    onClick={handleRejectAll}
                    className="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    data-testid="reject-all-button"
                  >
                    Reject All
                  </button>
                </div>
              )}
            </div>

            <div className="space-y-3">
              {changes.map((change, index) => (
                <div key={index} className={`p-3 rounded-lg border ${
                  change.type === 'error' ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200'
                }`} data-testid="change-item">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium mb-1">
                        {change.type === 'error' ? (
                          <span className="text-red-700 flex items-center gap-2">
                            <AlertCircle className="w-4 h-4" />
                            Error
                          </span>
                        ) : change.type === 'project' ? (
                          <span className="text-gray-700">Project</span>
                        ) : (
                          <span className="text-gray-700">Task: {change.taskId}</span>
                        )}
                      </div>
                      {change.type === 'error' ? (
                        <div className="text-sm text-red-700">{change.display}</div>
                      ) : (
                        <div className="font-mono text-sm">
                          {change.oldValue !== null && (
                            <>
                              <span className="text-red-600">- {change.field}: {change.oldValue || 'None'}</span>
                              <br />
                            </>
                          )}
                          <span className="text-green-600">+ {change.field}: {change.newValue}</span>
                        </div>
                      )}
                    </div>
                    {change.type !== 'error' && (
                      <div className="flex gap-1 ml-2">
                        <button
                          onClick={() => handleApply(change)}
                          className="p-1 text-green-600 hover:bg-green-50 rounded"
                          data-testid={`apply-change-${index}`}
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setChanges(changes.filter(c => c !== change))}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                          data-testid={`reject-change-${index}`}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    {change.type === 'error' && (
                      <div className="flex gap-1 ml-2">
                        <button
                          onClick={() => setChanges(changes.filter(c => c !== change))}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                          data-testid={`dismiss-error-${index}`}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}
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
  } catch (error) {
    console.error('NaturalLanguageEditor render error:', error);
    return (
      <div className="w-96 bg-gray-50 border-l border-gray-200 h-full p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium mb-2">Component Error</h3>
          <p className="text-red-600 text-sm">
            Failed to render Natural Language Editor
          </p>
          <details className="mt-2 text-xs text-red-700">
            <summary className="cursor-pointer">Error details</summary>
            <pre className="mt-1 p-2 bg-red-100 rounded overflow-auto">
              {error instanceof Error ? error.message : String(error)}
            </pre>
          </details>
        </div>
      </div>
    );
  }
};