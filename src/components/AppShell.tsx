import type { PropsWithChildren } from 'react';
import { useCockpitApi } from '../api/context';

export function AppShell({
  children,
  activePage = 'topic',
  footerText = '页面只呈现 API 返回的 Planner、Progress 与 Review 状态；浏览器不保存学习事实。',
}: PropsWithChildren<{
  activePage?: 'today' | 'topic' | 'learning-unit';
  footerText?: string;
}>) {
  const api = useCockpitApi();
  const isFixture = api.kind === 'contract-fixture';

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <header className="site-header">
        <a className="brand" href="/" aria-label="ruankao-cockpit 首页">
          <span className="brand-mark" aria-hidden="true">R</span>
          <span>ruankao-cockpit</span>
        </a>
        <nav className="primary-nav" aria-label="主导航">
          <a href="/" aria-current={activePage === 'today' ? 'page' : undefined}>Today</a>
        </nav>
      </header>
      {isFixture && (
        <div className="fixture-banner" role="status">
          DEV FIXTURE / CONTRACT FIXTURE — 仅用于浏览器开发与契约测试，不是 production truth。
        </div>
      )}
      <main id="main-content" className="page-content" tabIndex={-1}>
        {children}
      </main>
      <footer className="site-footer">{footerText}</footer>
    </div>
  );
}
