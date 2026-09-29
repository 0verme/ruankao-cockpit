import { expect, test } from '@playwright/test';

const topicPath = '/topics/ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';

async function submitIndexedAttempt(page: import('@playwright/test').Page, outcome: '答对' | '答错' = '答对') {
  await page.getByLabel('验证题来源（只选择实际使用过的题目）').selectOption('gs-comp-2024-h1-q65');
  await page.getByLabel('实际作答时间（必填；浏览器本地时间）').fill('2026-09-27T18:00');
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
  const readableSources = page.locator('.source-list:not(.provenance-details__list)');
  await expect(readableSources.getByRole('heading', { name: /第 14 章 14\.3\.1 容器技术/ })).toBeVisible();
  await expect(readableSources.getByText('相关章节：第 4 类：云原生架构设计理论与实践')).toBeVisible();
  const disclosure = page.locator('.provenance-details');
  await expect(disclosure).not.toHaveAttribute('open', '');
  await expect(disclosure.getByText('Source commit').first()).toBeHidden();
});

test('Topic provenance stays collapsed by default, works by keyboard, and fits desktop/mobile widths', async ({ page }) => {
  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto(topicPath);
    await expect(page.getByRole('heading', { name: '来源与证据' })).toBeVisible();
    const readableSources = page.locator('.source-list:not(.provenance-details__list)');
    await expect(readableSources.getByRole('heading', { name: /第 14 章 14\.3\.1 容器技术/ })).toBeVisible();
    await expect(readableSources.getByText('相关章节：第 4 类：云原生架构设计理论与实践')).toBeVisible();

    const disclosure = page.locator('.provenance-details');
    const summary = disclosure.locator('summary');
    await expect(disclosure).not.toHaveAttribute('open', '');
    await expect(disclosure.getByText('Source path').first()).toBeHidden();
    await summary.focus();
    await page.keyboard.press('Enter');
    await expect(disclosure).toHaveAttribute('open', '');
    for (const field of ['Source ID', 'Source commit', 'Source path', 'Source value', 'Source anchor', 'Confidence', 'Question ID', 'Golden Set record']) {
      await expect(disclosure.getByText(field).first()).toBeVisible();
    }

    const dimensions = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      content: document.documentElement.scrollWidth,
    }));
    expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);

    await page.keyboard.press('Enter');
    await expect(disclosure).not.toHaveAttribute('open', '');
    await expect(disclosure.getByText('Source path').first()).toBeHidden();
  }
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
    await page.goto(`${topicPath}?task_id=contract-fixture-task-001`);
    await expect(page.getByRole('heading', { name: '容器与 Serverless' })).toBeVisible();
    await expect(page.getByLabel('实际作答时间（必填；浏览器本地时间）')).toBeVisible();
    await expect(page.getByRole('button', { name: '提交真实 attempt' })).toBeVisible();
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
  await expect(page.getByRole('alert')).toContainText('提交未通过 API 输入或来源校验');
  await expect(page.getByText(/API 已接受 attempt/)).toHaveCount(0);
});

test('Learning Unit MERGE route renders real Markdown, provenance, refresh, and mobile widths', async ({ page }) => {
  const unitPath = '/learning-units/system-architect-checkin/checkin-001';
  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto(unitPath);
    await expect(page.getByRole('heading', { level: 1, name: '软件工程：生命周期与基本要素' })).toBeVisible();
    await expect(page.getByText('第 1 节')).toBeVisible();
    await expect(page.getByText('草稿')).toBeVisible();
    await expect(page.getByText('来源待补充')).toBeVisible();
    await expect(page.getByText('软件过程与开发方法')).toBeVisible();
    await expect(page.getByRole('heading', { name: '今天学会什么' })).toBeVisible();
    await expect(page.getByText(/三要素：保留证据缺口/)).toBeVisible();
    await expect(page.getByText(/content_version:/)).toHaveCount(0);
    await expect(page.getByText(/AI explain|Prompt execution|运行时生成/)).toHaveCount(0);

    const disclosure = page.locator('.provenance-details');
    await expect(disclosure).not.toHaveAttribute('open', '');
    await expect(disclosure.getByText('Source file')).toBeHidden();
    await disclosure.locator('summary').focus();
    await page.keyboard.press('Enter');
    await expect(disclosure).toHaveAttribute('open', '');
    await expect(disclosure.getByText('Source file')).toBeVisible();

    const dimensions = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      content: document.documentElement.scrollWidth,
    }));
    expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  }
  await page.reload();
  await expect(page.getByRole('heading', { level: 1, name: '软件工程：生命周期与基本要素' })).toBeVisible();
});

test('SPLIT stays one unit and its Topic labels, table, and code fit mobile viewports', async ({ page }) => {
  for (const width of [1280, 390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto('/learning-units/system-architect-checkin/checkin-005');
    await expect(page.getByRole('heading', { level: 1, name: 'V 模型、W 模型与质量左移' })).toBeVisible();
    const mapping = page.getByRole('region', { name: '关联知识' });
    await expect(mapping.getByText('软件过程与开发方法')).toBeVisible();
    await expect(mapping.getByText('软件测试')).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible();
    await expect(page.locator('.learning-unit-markdown pre')).toBeVisible();
    await expect(page.getByRole('button', { name: /完成|已学会|打卡/ })).toHaveCount(0);
    const dimensions = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      content: document.documentElement.scrollWidth,
    }));
    expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  }
});

test('EXACT, unreviewed, and UNMAPPED content render without invented links', async ({ page }) => {
  await page.goto('/learning-units/system-architect-checkin/checkin-002');
  await expect(page.getByRole('heading', { level: 1, name: '软件开发模型与方法（一）' })).toBeVisible();
  await expect(page.getByText('内容待复核')).toBeVisible();

  await page.goto('/learning-units/system-architect-checkin/checkin-006');
  await expect(page.getByRole('heading', { level: 1, name: '基于构件的软件开发' })).toBeVisible();
  await expect(page.getByRole('region', { name: '关联知识' }).getByText('构件与组件技术')).toBeVisible();

  await page.goto('/learning-units/system-architect-checkin/checkin-032');
  await expect(page.getByRole('heading', { level: 1, name: '可观测性：指标、日志与链路追踪' })).toBeVisible();
  await expect(page.getByText('尚未映射到现有知识 Topic')).toBeVisible();
  await expect(page.getByText(/三大支柱为指标、日志、链路追踪/)).toBeVisible();
  await expect(page.getByRole('link', { name: /软件过程|软件测试|构件与组件/ })).toHaveCount(0);
});

test('NON_LEARNING has an explicit unavailable state and unknown URLs return 404', async ({ page }) => {
  await page.goto('/learning-units/system-architect-checkin/checkin-020');
  await expect(page.getByRole('heading', { name: '这不是一个学习单元' })).toBeVisible();
  await expect(page.getByRole('alert')).toContainText('不是学习单元');
  await expect(page.getByRole('heading', { name: '软件工程：生命周期与基本要素' })).toHaveCount(0);

  const response = await page.goto('/learning-units/system-architect-checkin/checkin-999');
  expect(response?.status()).toBe(404);
  await expect(page.getByRole('heading', { name: '页面不存在或不可用' })).toBeVisible();
});
