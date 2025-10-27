# 时间工具MCP模块

这个模块提供了时间相关的MCP工具功能，包括节假日查询、正计时器和闹钟功能。

## 功能特性

### 1. 节假日查询 (`time_utils.get_holiday_info`) ⭐ **实时API数据**
- **实时准确**: 使用在线API获取最新节假日信息
- **多种查询**: 下一个节假日、距离天数、工作日判断、一年节假日等
- **自动更新**: 无需手动维护节假日数据

## 节假日API数据源

使用 **appworlds.cn** 提供的免费节假日API：
- ✅ **实时准确**: 自动包含最新的节假日调整
- ✅ **官方数据**: 基于中国法定节假日
- ✅ **高可用性**: 稳定的在线服务
- ✅ **免费额度**: 1秒1次，日请求量≤1000次

### 2. 正计时器功能 (支持多个并发计时器)
- `time_utils.create_stopwatch` - 创建新的正计时器
- `time_utils.start_stopwatch` - 启动指定计时器
- `time_utils.pause_stopwatch` - 暂停指定计时器
- `time_utils.reset_stopwatch` - 重置指定计时器
- `time_utils.get_stopwatch_status` - 获取指定计时器状态
- `time_utils.get_all_stopwatches` - 获取所有计时器状态
- `time_utils.delete_stopwatch` - 删除指定计时器

### 3. 闹钟功能 (支持多个并发闹钟)
- `time_utils.set_alarm` - 设置闹钟时间和消息
- `time_utils.cancel_alarm` - 取消指定闹钟
- `time_utils.get_active_alarms` - 查看所有活动闹钟

## 支持的节假日

目前支持以下中国主要节假日：
- 元旦
- 春节
- 清明节
- 劳动节
- 端午节
- 中秋节
- 国庆节

## 使用示例

### 查询下一个节假日
```json
{
  "name": "time_utils.get_holiday_info",
  "arguments": {
    "holiday_type": "next"
  }
}
```
*注意：如果当前日期已过全年所有节假日，将返回"当前没有更多的节假日信息"*

### 查看距离下一个节假日还有多少天
```json
{
  "name": "time_utils.get_holiday_info",
  "arguments": {
    "holiday_type": "next_days"
  }
}
```
*注意：如果当前日期已过全年所有节假日，将返回"当前没有更多的节假日信息"*

### 判断指定日期是否为工作日
```json
{
  "name": "time_utils.get_holiday_info",
  "arguments": {
    "holiday_type": "is_workday",
    "date": "2025-01-01"
  }
}
```

### 获取一整年的节假日信息
```json
{
  "name": "time_utils.get_holiday_info",
  "arguments": {
    "holiday_type": "year",
    "year": "2025"
  }
}
```

### 创建并使用正计时器
```json
// 创建计时器
{
  "name": "time_utils.create_stopwatch",
  "arguments": {
    "name": "工作任务"
  }
}

// 启动计时器（使用返回的stopwatch_id）
{
  "name": "time_utils.start_stopwatch",
  "arguments": {
    "stopwatch_id": "stopwatch_1735718400000"
  }
}

// 查看状态
{
  "name": "time_utils.get_stopwatch_status",
  "arguments": {
    "stopwatch_id": "stopwatch_1735718400000"
  }
}
```

### 设置闹钟
```json
{
  "name": "time_utils.set_alarm",
  "arguments": {
    "alarm_time": "2025-01-01T08:00:00",
    "message": "早上好！新年快乐！"
  }
}
```

## API 参考

### time_utils.get_holiday_info
**参数：**
- `holiday_type` (string, 可选): 查询类型
  - `"upcoming"` (默认): 即将到来的节假日
  - `"all"`: 所有节假日
  - `"specific_date"`: 特定日期
- `date` (string, 可选): 当`holiday_type`为`"specific_date"`时需要，格式：YYYY-MM-DD

### 正计时器工具
所有正计时器工具都需要 `stopwatch_id` 参数来指定操作的计时器。

**time_utils.create_stopwatch**
- `name` (string, 可选): 计时器名称

**其他正计时器工具**
- `stopwatch_id` (string, 必需): 计时器ID

### time_utils.set_alarm
**参数：**
- `alarm_time` (string, 必需): 闹钟时间，ISO格式，如 "2025-01-01T08:00:00"
- `message` (string, 可选): 闹钟消息

### time_utils.cancel_alarm
**参数：**
- `alarm_id` (string, 必需): 要取消的闹钟ID

## 触发机制

### 倒计时器触发
- 执行预设的MCP工具调用
- 通过TTS语音播报执行结果

### 闹钟触发
- 通过TTS语音播报闹钟消息
- 记录触发日志

## 注意事项

1. 节假日数据目前为2025-2026年的简化版本
2. 正计时器支持多个并发实例，每个都有唯一ID
3. 闹钟使用异步任务，不会阻塞主程序
4. 所有时间都使用系统本地时间

## 架构设计

基于倒计时器的设计模式：
- **服务层**: `AlarmService` 和 `StopwatchService` 管理所有任务
- **任务层**: `AlarmTask` 和 `StopwatchTask` 表示单个任务实例
- **并发支持**: 使用asyncio和锁确保线程安全
- **生命周期管理**: 自动清理已完成的任务