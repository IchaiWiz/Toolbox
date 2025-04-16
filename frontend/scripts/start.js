import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Récupération des arguments de la commande
const args = process.argv.slice(2);
const isDebugMode = args.includes('debug');

console.log(`\n========================================`);
console.log(`Mode: ${isDebugMode ? 'DEBUG (logs détaillés activés)' : 'NORMAL (logs minimaux)'}`);
console.log(`========================================\n`);

// Définir la variable d'environnement pour le frontend
process.env.VITE_DEBUG_MODE = isDebugMode ? 'true' : 'false';

// Lancement du frontend avec ou sans mode debug
const frontendProcess = spawn('npm', ['run', 'frontend'], {
  stdio: 'inherit',
  shell: true,
  env: { ...process.env, VITE_DEBUG_MODE: isDebugMode ? 'true' : 'false' }
});

// Lancement du backend (avec ou sans debug)
const backendScript = isDebugMode ? 'backend-debug' : 'backend';
const backendProcess = spawn('npm', ['run', backendScript], {
  stdio: 'inherit',
  shell: true
});

// Gestion de la fermeture des processus
process.on('SIGINT', () => {
  frontendProcess.kill('SIGINT');
  backendProcess.kill('SIGINT');
  process.exit();
});

frontendProcess.on('close', (code) => {
  console.log(`Le processus frontend s'est terminé avec le code ${code}`);
  backendProcess.kill();
  process.exit(code);
});

backendProcess.on('close', (code) => {
  console.log(`Le processus backend s'est terminé avec le code ${code}`);
  frontendProcess.kill();
  process.exit(code);
}); 