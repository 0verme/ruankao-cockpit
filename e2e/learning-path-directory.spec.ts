import { expect, test } from '@playwright/test';

const learnableUnitPath = (itemId: string) => `/learning-units/system-architect-checkin/${itemId}`;

async function expectNoViewportOverflow(page: import('@playwright/test').Page) {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
}

test('Learning Path directory preserves manifest order and supports independent multi-unit browsing', async ({ page }) => {
  const apiRequests: Array<{ method: string; url: string }> = [];
  page.on('request', (request) => {
    if (new URL(request.url()).pathname.startsWith('/api/')) {
      apiRequests.push({ method: request.method(), url: new URL(request.url()).pathname });
    }
  });

  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    const response = await page.goto('/learn');
    expect(response?.status()).toBe(200);
    await expect(page.getByRole('heading', { name: '系统架构设计师打卡学习路径' })).toBeVisible();
    await expect(page.getByRole('note')).toContainText('当前目录顺序仍在复核中');
    await expect(page.getByRole('link', { name: '学习目录' })).toHaveAttribute('aria-current', 'page');

    const entries = page.locator('.learning-path-list > li');
    await expect(entries).toHaveCount(112);
    await expect(entries.nth(0)).toContainText('第 1 节');
    await expect(entries.nth(0)).toContainText('软件工程：生命周期与基本要素');
    await expect(entries.nth(18)).toContainText('第 19 节');
    await expect(entries.nth(19)).toContainText('第 20 项');
    await expect(entries.nth(19)).toContainText('休息');
    await expect(entries.nth(19)).toContainText('非学习项');
    await expect(entries.nth(19).getByRole('link')).toHaveCount(0);
    await expect(entries.nth(20)).toContainText('第 21 节');
    await expect(entries.nth(31)).toContainText('尚未映射知识主题');
    await expect(entries.nth(111)).toContainText('第 112 节');
    await expectNoViewportOverflow(page);
  }
  await page.reload();
  await expect(page.locator('.learning-path-list > li')).toHaveCount(112);

  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto(learnableUnitPath('checkin-001'));
    const unitNavigation = page.getByRole('navigation', { name: '学习单元导航' });
    await expect(unitNavigation.getByText('← 上一节')).toHaveAttribute('aria-disabled', 'true');
    await expect(unitNavigation.getByRole('link', { name: '下一节 →' })).toHaveAttribute(
      'href', learnableUnitPath('checkin-002'),
    );
    await expectNoViewportOverflow(page);
  }

  await page.goto('/learn');
  await page.getByRole('link', { name: /第 1 节：软件工程：生命周期与基本要素/ }).click();
  await expect(page).toHaveURL(learnableUnitPath('checkin-001'));
  await expect(page.getByRole('heading', { level: 1, name: '软件工程：生命周期与基本要素' })).toBeVisible();
  const navigation = page.getByRole('navigation', { name: '学习单元导航' });
  await expect(navigation.getByText('← 上一节')).toHaveAttribute('aria-disabled', 'true');
  await expect(navigation.getByRole('link', { name: '下一节 →' })).toHaveAttribute('href', learnableUnitPath('checkin-002'));
  await page.getByRole('link', { name: '下一节 →' }).click();
  await expect(page).toHaveURL(learnableUnitPath('checkin-002'));
  await expect(page.getByRole('heading', { level: 1, name: '软件开发模型与方法（一）' })).toBeVisible();
  await page.getByRole('link', { name: '返回目录' }).click();
  await expect(page).toHaveURL('/learn');
  await expect(page.getByRole('heading', { name: '系统架构设计师打卡学习路径' })).toBeVisible();

  await page.goto(learnableUnitPath('checkin-019'));
  await expect(page.getByRole('link', { name: '下一节 →' })).toHaveAttribute('href', learnableUnitPath('checkin-021'));
  await page.getByRole('link', { name: '下一节 →' }).click();
  await expect(page).toHaveURL(learnableUnitPath('checkin-021'));
  await expect(page.getByRole('link', { name: '← 上一节' })).toHaveAttribute('href', learnableUnitPath('checkin-019'));

  await page.goto('/learn');
  await page.getByRole('link', { name: /第 32 节：可观测性：指标、日志与链路追踪/ }).click();
  await expect(page).toHaveURL(learnableUnitPath('checkin-032'));
  await expect(page.getByRole('heading', { level: 1, name: '可观测性：指标、日志与链路追踪' })).toBeVisible();
  await expect(page.getByText('尚未映射到现有知识 Topic')).toBeVisible();
  await expect(page.getByRole('link', { name: '← 上一节' })).toHaveAttribute('href', learnableUnitPath('checkin-031'));
  await expect(page.getByRole('link', { name: '下一节 →' })).toHaveAttribute('href', learnableUnitPath('checkin-033'));
  await page.reload();
  await expect(page.getByRole('heading', { level: 1, name: '可观测性：指标、日志与链路追踪' })).toBeVisible();

  await page.goto(learnableUnitPath('checkin-112'));
  await expect(page.getByRole('heading', { level: 1, name: /分片系统常见问题：事务与跨分片查询/ })).toBeVisible();
  await expect(page.getByRole('navigation', { name: '学习单元导航' }).getByText('下一节 →')).toHaveAttribute('aria-disabled', 'true');
  await expectNoViewportOverflow(page);
  expect(apiRequests.length).toBeGreaterThan(0);
  expect(apiRequests.every((request) => request.method === 'GET')).toBe(true);
  expect(apiRequests.some((request) => request.url.startsWith('/api/attempts'))).toBe(false);
});
