import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:4321',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'python3 -m uvicorn api:app --host 127.0.0.1 --port 8000',
      url: 'http://127.0.0.1:8000/api/learning-units/system-architect-checkin/checkin-001',
      reuseExistingServer: !process.env.CI,
      env: { PYTHONPATH: process.env.PYTHONPATH ?? '' },
      timeout: 120_000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      url: 'http://127.0.0.1:4321',
      reuseExistingServer: !process.env.CI,
      env: {
        PUBLIC_API_MODE: 'contract-fixture',
        PUBLIC_API_BASE_URL: '',
      },
      timeout: 120_000,
    },
  ],
});
