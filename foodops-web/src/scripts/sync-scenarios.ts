import fs from 'fs';
import path from 'path';
import yaml from 'yaml';

const scenariosDir = path.join(__dirname, '..', '..', '..', 'scenarios');
const output = path.join(__dirname, '..', 'data');
fs.mkdirSync(output, { recursive: true });

const files = fs.readdirSync(scenariosDir).filter(f => f.endsWith('.yaml'));
const scenarios = files.map(file => {
  const raw = fs.readFileSync(path.join(scenariosDir, file), 'utf8');
  const data = yaml.parse(raw);
  return { id: path.basename(file, '.yaml'), ...data };
});

fs.writeFileSync(path.join(output, 'scenarios.json'), JSON.stringify(scenarios, null, 2));
console.log(`Synchronised ${scenarios.length} scenarios`);
