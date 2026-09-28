import { createContext, useContext, type PropsWithChildren } from 'react';
import type { CockpitApiClient } from './contracts';
import { getCockpitApiClient } from './client';

const ApiContext = createContext<CockpitApiClient | null>(null);

export function ApiProvider({
  client,
  children,
}: PropsWithChildren<{ client: CockpitApiClient }>) {
  return <ApiContext.Provider value={client}>{children}</ApiContext.Provider>;
}

export function useCockpitApi(): CockpitApiClient {
  return useContext(ApiContext) ?? getCockpitApiClient();
}
