import type { ApiErrorCode } from '../api/types';

export function messageForApiError(code: string): string {
  switch (code as ApiErrorCode) {
    case 'not_initialized':
      return 'Cockpit 尚未初始化。初始化会显式创建本地数据文件，不会由读取请求自动完成。';
    case 'incomplete_local_data':
      return '本地数据不完整；为避免覆盖事实，Cockpit 未自动重建。';
    case 'unknown_topic':
    case 'unknown_task':
      return '找不到此 Topic 或任务，或它不在当前可用计划中。';
    case 'unknown_learning_path':
    case 'unknown_learning_unit':
      return '找不到对应的学习路径或学习单元。';
    case 'not_a_learning_unit':
      return '该路径项不是学习单元（例如休息日），没有学习正文。';
    case 'non_active_topic':
      return '该 ID 不是可浏览的 active L3 Knowledge Topic。';
    case 'invalid_learning_payload':
    case 'invalid_source_provenance':
      return 'Learning Payload / provenance 校验未通过；材料已隐藏，不会生成替代内容。';
    case 'invalid_learning_path':
    case 'invalid_learning_unit':
    case 'invalid_learning_catalog':
      return '学习路径或 Markdown 元数据校验未通过；内容已隐藏，不会生成替代内容。';
    case 'invalid_input':
    case 'invalid_request':
    case 'invalid_timestamp':
    case 'invalid_attempt':
    case 'invalid_source_reference':
    case 'forbidden_path':
    case 'future_evidence':
    case 'target_mismatch':
      return '提交未通过 API 输入或来源校验，事实未被接受。请检查必填字段与来源引用。';
    case 'task_not_scheduled':
      return '该任务已不属于当前 Today 计划；没有写入事实。请回到 Today 刷新。';
    case 'duplicate_event':
      return 'API 检测到重复 attempt；没有重复写入。请刷新以读取当前状态。';
    case 'pending_transaction':
    case 'conflicting_transaction':
      return '本地记录事务尚未完成或与当前请求冲突。请刷新状态后再决定下一步。';
    case 'storage_error':
    case 'invalid_local_data':
    case 'invalid_catalog':
    case 'invalid_learning_catalog':
    case 'invalid_topic_experience':
    case 'invalid_planner_output':
    case 'domain_error':
      return '服务端无法安全读取本地事实或领域数据；没有用空状态替代错误。';
    case 'network_error':
      return '无法连接 Cockpit API。请检查 API 服务与网络后重试。';
    case 'api_error':
    default:
      return 'Cockpit API 返回错误。可以重试读取；提交结果不确定时请先刷新状态，不要盲目重复提交。';
  }
}

export function ApiNotice({
  code,
  message,
  variant = 'error',
}: {
  code?: string;
  message?: string;
  variant?: 'error' | 'info' | 'success';
}) {
  const displayMessage = message ?? (code ? messageForApiError(code) : messageForApiError('api_error'));
  return (
    <div className={`notice notice--${variant}`} role={variant === 'error' ? 'alert' : 'status'}>
      {displayMessage}
    </div>
  );
}
