import { createFixtureApiClient, type FixtureScenario } from './fixtureClient';
import { createHttpApiClient } from './httpClient';
import type { CockpitApiClient } from './contracts';

let client: CockpitApiClient | undefined;

function fixtureScenarioFromLocation(): FixtureScenario {
  if (typeof window === 'undefined') return 'ready';
  const value = new URLSearchParams(window.location.search).get('fixture');
  const allowed: FixtureScenario[] = [
    'ready',
    'not-initialized',
    'payload-unavailable',
    'invalid-provenance',
    'api-error',
    'network-error',
    'attempt-failure',
    'attempt-invalid-input',
  ];
  return allowed.includes(value as FixtureScenario) ? value as FixtureScenario : 'ready';
}

export function getCockpitApiClient(): CockpitApiClient {
  if (client) return client;
  if (import.meta.env.PUBLIC_API_MODE === 'contract-fixture') {
    client = createFixtureApiClient(fixtureScenarioFromLocation());
  } else {
    client = createHttpApiClient(import.meta.env.PUBLIC_API_BASE_URL ?? '');
  }
  return client;
}
