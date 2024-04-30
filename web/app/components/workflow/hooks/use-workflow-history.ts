import {
  useCallback,
  useEffect,
  useRef,
} from 'react'
import { debounce } from 'lodash-es'
import {
  useStoreApi,
} from 'reactflow'
import { useWorkflowHistoryStore } from '../workflow-history-store'

/**
 * All supported Events that create a new history state.
 * Current limitations:
 * - InputChange events in Node Panels do not trigger state changes.
 * - Resizing UI elements does not trigger state changes.
 */
export enum WorkflowHistoryEvent {
  NodeTitleChange = 'NodeTitleChange',
  NodeDescriptionChange = 'NodeDescriptionChange',
  NodeDragStop = 'NodeDragStop',
  NodeChange = 'NodeChange',
  NodeConnect = 'NodeConnect',
  NodeAdd = 'NodeAdd',
  NodePaste = 'NodePaste',
  NodeDelete = 'NodeDelete',
  EdgeDelete = 'EdgeDelete',
  EdgeDeleteByDeleteBranch = 'EdgeDeleteByDeleteBranch',
}

export const useWorkflowHistory = () => {
  const store = useStoreApi()
  const workflowHistoryStore = useWorkflowHistoryStore()

  // Some events may be triggered multiple times in a short period of time.
  // We debounce the history state update to avoid creating multiple history states
  // with minimal changes.
  const saveStateToHistoryRef = useRef(debounce(() => {
    workflowHistoryStore.setState({
      nodes: store.getState().getNodes(),
      edges: store.getState().edges,
    })
  }, 500))

  useEffect(() => {
    const currentSaveStateToHistory = saveStateToHistoryRef.current

    return () => {
      // Cancel the debounced function if the component is unmounted
      currentSaveStateToHistory.cancel()
    }
  }, [])

  const saveStateToHistory = useCallback((event: WorkflowHistoryEvent) => {
    switch (event) {
      case WorkflowHistoryEvent.NodeTitleChange:
      case WorkflowHistoryEvent.NodeDescriptionChange:
      case WorkflowHistoryEvent.NodeDragStop:
      case WorkflowHistoryEvent.NodeChange:
      case WorkflowHistoryEvent.NodeConnect:
      case WorkflowHistoryEvent.NodeAdd:
      case WorkflowHistoryEvent.NodePaste:
      case WorkflowHistoryEvent.NodeDelete:
      case WorkflowHistoryEvent.EdgeDelete:
      case WorkflowHistoryEvent.EdgeDeleteByDeleteBranch:
        saveStateToHistoryRef.current()
        break
      default:
        // We do not create a history state for every event.
        // Some events of reactflow may change things the user would not want to undo/redo.
        // For example: UI state changes like selecting a node.
        break
    }
  }, [])

  return {
    store,
    saveStateToHistory,
  }
}
