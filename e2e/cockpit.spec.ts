import { expect, test } from '@playwright/test';

const topicPath = '/topics/ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';

async function submitIndexedAttempt(page: import('@playwright/test').Page, outcome: '答对' | '答错' = '答对') {
  await page.getByLabel('验证题来源（只选择实际使用过的题目）').selectOption('gs-comp-2024-h1-q65');
  await page.getByRole('radio', { name: outcome }).check();
  await page.getByRole('button', { name: '提交真实 attempt' }).click();
}

test('Today loads and opens the unified Topic page', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText(/DEV FIXTURE \/ CONTRACT FIXTURE/)).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Today' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '今日任务' })).toBeVisible();
  await page.getByRole('link', { name: /打开 Topic 学习体验/ }).click();
  await expect(page).toHaveURL(new RegExp(`${topicPath.replaceAll('.', '\\.')}\\?task_id=`));
  await expect(page.getByRole('heading', { name: '容器与 Serverless' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '核心知识' })).toBeVisible();
  await expect(page.getByText('Sources / Provenance')).toBeVisible();
  await expect(page.getByRole('heading', { name: '来源与证据' })).toBeVisible();
  await expect(page.locator('.source-card').first()).toContainText('Source commit');
  await expect(page.locator('.source-card').first()).toContainText('Source path');
});

test('unavailable payload is explicit and does not invent learning content', async ({ page }) => {
  await page.goto(`${topicPath}?fixture=payload-unavailable`);
  await expect(page.getByRole('heading', { name: '材料尚未整理' })).toBeVisible();
  await expect(page.getByText(/不会运行时生成或补写学习材料/)).toBeVisible();
  await expect(page.getByRole('heading', { name: '核心知识' })).toHaveCount(0);
});

test('not initialized state offers an explicit init POST action', async ({ page }) => {
  await page.goto('/?fixture=not-initialized');
  await expect(page.getByRole('heading', { name: '尚未初始化' })).toBeVisible();
  await page.getByRole('button', { name: '初始化 Cockpit' }).click();
  await expect(page.getByRole('heading', { name: '今日任务' })).toBeVisible();
});

test('API failure is distinct from unavailable and can be retried', async ({ page }) => {
  await page.goto('/?fixture=api-error');
  await expect(page.getByRole('heading', { name: 'Today 暂时不可用' })).toBeVisible();
  await expect(page.getByRole('alert')).toContainText('Cockpit API 返回错误');
  await expect(page.getByRole('button', { name: '重试读取' })).toBeVisible();
});

test('network failure has a distinct API status', async ({ page }) => {
  await page.goto('/?fixture=network-error');
  await expect(page.getByRole('heading', { name: 'Today 暂时不可用' })).toBeVisible();
  await expect(page.getByRole('alert')).toContainText('无法连接 Cockpit API');
});

test('keyboard can skip to main content and activate the Today Topic link', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: '跳到主要内容' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
  await page.getByRole('link', { name: /打开 Topic 学习体验/ }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Verification' })).toBeVisible();
});

test('320px and 390px mobile layouts do not overflow horizontally', async ({ page }) => {
  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto(topicPath);
    await expect(page.getByRole('heading', { name: '容器与 Serverless' })).toBeVisible();
    const dimensions = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      content: document.documentElement.scrollWidth,
    }));
    expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  }
});

test('document is the only vertical scroll owner and Topic survives a browser refresh', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 560 });
  await page.goto(topicPath);
  await expect(page.getByRole('heading', { name: '来源与证据' })).toBeVisible();
  const owners = await page.evaluate(() => Array.from(document.querySelectorAll<HTMLElement>('body *'))
    .filter((element) => {
      const overflowY = getComputedStyle(element).overflowY;
      return (overflowY === 'auto' || overflowY === 'scroll') && element.scrollHeight > element.clientHeight;
    }).length);
  expect(owners).toBe(0);
  await page.reload();
  await expect(page.getByRole('heading', { name: '容器与 Serverless' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '来源与证据' })).toBeVisible();
});

test('Verification success rereads server contract replay response', async ({ page }) => {
  await page.goto(`${topicPath}?task_id=contract-fixture-task-001`);
  await submitIndexedAttempt(page);
  await expect(page.getByText(/Topic 与 Today 已重新读取/)).toBeVisible();
  await expect(page.getByText('1 次验证 attempt')).toBeVisible();
  await expect(page.getByText('下次复习 2026-09-29')).toBeVisible();
  await expect(page.getByRole('button', { name: '提交真实 attempt' })).toHaveCount(0);
});

test('Verification API failure is visible and does not claim a replay success', async ({ page }) => {
  await page.goto(`${topicPath}?task_id=contract-fixture-task-001&fixture=attempt-invalid-input`);
  await submitIndexedAttempt(page);
  await expect(page.getByRole('alert')).toContainText('提交未通过 API 输入校验');
  await expect(page.getByText(/API 已接受 attempt/)).toHaveCount(0);
});
