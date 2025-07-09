import React, { useState } from 'react';
import { Check, X } from 'lucide-react';
import type { Change, NaturalLanguageEditorProps } from '../../types';
import { Priority } from '../../types';

export const NaturalLanguageEditor: React.FC<NaturalLanguageEditorProps> = ({
  selectedProject,
  selectedTask,
  onApplyChanges,
}) => {
  const [input, setInput] = useState('');
  const [changes, setChanges] = useState<Change[] | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const simulateNLProcessing = (text: string) => {
    // Simulate processing and generating changes
    setIsProcessing(true);
    setTimeout(() => {
      // Example changes based on simple keyword detection
      const simulatedChanges: Change[] = [];

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

  const handleApply = (change: Change) => {
    onApplyChanges([change]);
    setChanges(changes ? changes.filter(c => c !== change) : null);
  };

  const handleApplyAll = () => {
    if (changes) {
      onApplyChanges(changes);
      setChanges(null);
      setInput('');
    }
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
            data-testid="nl-input"
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isProcessing}
            className="w-full mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            data-testid="generate-changes-button"
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
            </div>

            <div className="space-y-3">
              {changes.map((change, index) => (
                <div key={index} className="bg-white p-3 rounded-lg border border-gray-200" data-testid="change-item">
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