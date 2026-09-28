import type { ApiErrorCode } from '../api/types';

const messages: Record<ApiErrorCode, string> = {
  not_initialized: 'Cockpit 尚未初始化。初始化会显式创建本地数据文件，不会由读取请求自动完成。',
  payload_unavailable: '该 Topic 的 Learning Payload 当前不可用。',
  unknown_topic: '找不到此 Topic，或它不在当前 Slice 的可浏览范围内。',
  invalid_payload_provenance: 'Learning Payload / provenance 校验未通过；材料已隐藏，不会生成替代内容。',
  invalid_input: '提交未通过 API 输入校验，事实未被接受。请检查必填字段与来源引用。',
  task_not_scheduled: '该任务已不属于当前 Today 计划；没有写入事实。请回到 Today 刷新。',
  duplicate_attempt: 'API 检测到重复 attempt；没有重复写入。请刷新以读取当前状态。',
  network_error: '无法连接 Cockpit API。请检查 API 服务与网络后重试。',
  api_error: 'Cockpit API 返回错误。可以重试读取；提交结果不确定时请先刷新状态，不要盲目重复提交。',
};

export function messageForApiError(code: string): string {
  return messages[code as ApiErrorCode] ?? messages.api_error;
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
  const displayMessage = message ?? (code ? messageForApiError(code) : messages.api_error);
  return (
    <div className={`notice notice--${variant}`} role={variant === 'error' ? 'alert' : 'status'}>
      {displayMessage}
    </div>
  );
}
