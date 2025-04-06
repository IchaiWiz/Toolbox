import { createContext, useContext, useState, ReactNode } from 'react';

export type ToolType = 'Dashboard' | 'CopyTool' | 'BackupTool' | 'AiStructureTool' | 'AnalyseTool' | 'DuplicateDetectionTool' | 'WinMergeTool';

export interface Tab {
  id: string;
  type: ToolType;
  title: string;
  icon?: string;
  closable: boolean;
  pinned: boolean;
}

interface TabsContextType {
  tabs: Tab[];
  activeTab: string | null;
  addTab: (type: ToolType) => void;
  closeTab: (id: string) => void;
  setActiveTab: (id: string) => void;
  reorderTabs: (startIndex: number, endIndex: number) => void;
  renameTab: (id: string, newTitle: string) => void;
  togglePinTab: (id: string) => void;
  getToolInstances: (type: ToolType) => number;
  closeAllUnpinnedTabs: () => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export function TabsProvider({ children }: { children: ReactNode }) {
  // Dashboard is always present and not closable
  const [tabs, setTabs] = useState<Tab[]>([
    { id: 'dashboard', type: 'Dashboard', title: 'Dashboard', closable: false, pinned: true }
  ]);
  
  const [activeTab, setActiveTab] = useState<string | null>('dashboard');

  // Count instances of a tool type
  const getToolInstances = (type: ToolType): number => {
    return tabs.filter(tab => tab.type === type).length;
  };

  // Add a new tab, always creating a new instance
  const addTab = (type: ToolType) => {
    const instanceCount = getToolInstances(type);
    const title = instanceCount > 0 ? `${type} ${instanceCount + 1}` : type;
    
    const id = `${type.toLowerCase()}-${Date.now()}`;
    const newTab: Tab = {
      id,
      type,
      title,
      closable: type !== 'Dashboard',
      pinned: false
    };

    // Add pinned tabs first, then regular tabs
    const pinnedTabs = tabs.filter(tab => tab.pinned);
    const unpinnedTabs = tabs.filter(tab => !tab.pinned);
    
    setTabs([...pinnedTabs, newTab, ...unpinnedTabs]);
    setActiveTab(id);
  };

  // Close a tab
  const closeTab = (id: string) => {
    const tabIndex = tabs.findIndex(tab => tab.id === id);
    if (tabIndex === -1 || !tabs[tabIndex].closable) return;

    const newTabs = tabs.filter(tab => tab.id !== id);
    setTabs(newTabs);

    // If we're closing the active tab, activate another tab
    if (activeTab === id) {
      const newActiveIndex = tabIndex === 0 ? 0 : tabIndex - 1;
      setActiveTab(newTabs[newActiveIndex]?.id || null);
    }
  };

  // Close all unpinned tabs
  const closeAllUnpinnedTabs = () => {
    // Keep only pinned tabs
    const pinnedTabs = tabs.filter(tab => tab.pinned);
    setTabs(pinnedTabs);
    
    // If the active tab was closed, set the active tab to the last pinned tab
    if (!tabs.find(tab => tab.id === activeTab)?.pinned) {
      setActiveTab(pinnedTabs[pinnedTabs.length - 1]?.id || null);
    }
  };

  // Rename a tab
  const renameTab = (id: string, newTitle: string) => {
    setTabs(prevTabs => 
      prevTabs.map(tab => 
        tab.id === id ? { ...tab, title: newTitle } : tab
      )
    );
  };

  // Toggle pin status of a tab
  const togglePinTab = (id: string) => {
    // Find the tab to toggle
    const tabToToggle = tabs.find(tab => tab.id === id);
    if (!tabToToggle || tabToToggle.type === 'Dashboard') return; // Dashboard is always pinned
    
    const newPinnedState = !tabToToggle.pinned;
    
    // Create updated tabs array with new pinned state
    const updatedTabs = tabs.map(tab => 
      tab.id === id ? { ...tab, pinned: newPinnedState } : tab
    );
    
    // Reorder tabs to maintain pinned tabs at the beginning (except Dashboard which is always first)
    const dashboardTab = updatedTabs.find(tab => tab.type === 'Dashboard');
    const pinnedTabs = updatedTabs.filter(tab => tab.pinned && tab.type !== 'Dashboard');
    const unpinnedTabs = updatedTabs.filter(tab => !tab.pinned && tab.type !== 'Dashboard');
    
    setTabs([
      ...(dashboardTab ? [dashboardTab] : []),
      ...pinnedTabs,
      ...unpinnedTabs
    ]);
  };

  // Reorder tabs using drag and drop, respecting pinned status
  const reorderTabs = (startIndex: number, endIndex: number) => {
    const result = Array.from(tabs);
    const [removed] = result.splice(startIndex, 1);
    
    // Don't allow moving pinned tabs to unpinned section and vice versa
    const isPinned = removed.pinned;
    const pinnedIndices = result.map((tab, i) => tab.pinned ? i : -1).filter(i => i !== -1);
    const lastPinnedIndex = Math.max(...pinnedIndices, 0);
    
    let adjustedEndIndex = endIndex;
    
    if (isPinned && endIndex > lastPinnedIndex) {
      // Don't move pinned tab after unpinned tabs
      adjustedEndIndex = lastPinnedIndex;
    } else if (!isPinned && endIndex <= lastPinnedIndex) {
      // Don't move unpinned tab before pinned tabs
      adjustedEndIndex = lastPinnedIndex + 1;
    }
    
    result.splice(adjustedEndIndex, 0, removed);
    setTabs(result);
  };

  return (
    <TabsContext.Provider 
      value={{ 
        tabs, 
        activeTab, 
        addTab, 
        closeTab, 
        setActiveTab, 
        reorderTabs,
        renameTab,
        togglePinTab,
        getToolInstances,
        closeAllUnpinnedTabs
      }}
    >
      {children}
    </TabsContext.Provider>
  );
}

export function useTabs() {
  const context = useContext(TabsContext);
  if (context === undefined) {
    throw new Error('useTabs must be used within a TabsProvider');
  }
  return context;
} 