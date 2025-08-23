async function getScenarios() {
  const res = await fetch('http://localhost:3000/api/trpc/scenarios', {
    headers: {
      'content-type': 'application/json',
    },
    cache: 'no-store'
  });
  const json = await res.json();
  return json.result?.data?.json ?? [];
}

export default async function ScenariosPage() {
  const scenarios = await getScenarios();
  return (
    <main className="p-4">
      <h1 className="text-xl font-bold mb-2">Scénarios</h1>
      <pre>{JSON.stringify(scenarios, null, 2)}</pre>
    </main>
  );
}
