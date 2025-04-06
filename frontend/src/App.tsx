import { ThemeProvider } from './contexts/ThemeContext';
import { TabsProvider } from './contexts/TabsContext';
import { Layout } from './components/layout/Layout';

function App() {
  return (
    <ThemeProvider>
      <TabsProvider>
        <Layout />
      </TabsProvider>
    </ThemeProvider>
  );
}

export default App;
