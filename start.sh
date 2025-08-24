#!/bin/bash

# 微信RSS新闻推送服务启动脚本
# 支持后台运行、日志记录、进程管理等功能

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="wechat-rss-sender"
PYTHON_SCRIPT="${SCRIPT_DIR}/run.py"
PID_FILE="${SCRIPT_DIR}/.${SERVICE_NAME}.pid"
LOG_FILE="${SCRIPT_DIR}/logs/${SERVICE_NAME}.log"
ERROR_LOG="${SCRIPT_DIR}/logs/${SERVICE_NAME}_error.log"
ENV_FILE="${SCRIPT_DIR}/.env"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 创建日志目录
mkdir -p "${SCRIPT_DIR}/logs"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境文件
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "环境配置文件 .env 不存在!"
        print_info "请复制 env.example 到 .env 并配置相关参数"
        exit 1
    fi
}

# 检查Python依赖
check_dependencies() {
    print_info "检查Python依赖..."
    
    # 检查是否有虚拟环境
    if [ -d "${SCRIPT_DIR}/venv" ]; then
        source "${SCRIPT_DIR}/venv/bin/activate"
        print_info "使用虚拟环境: ${SCRIPT_DIR}/venv"
    elif [ -d "${SCRIPT_DIR}/.venv" ]; then
        source "${SCRIPT_DIR}/.venv/bin/activate"
        print_info "使用虚拟环境: ${SCRIPT_DIR}/.venv"
    else
        print_warning "未找到虚拟环境，使用系统Python"
    fi
    
    # 检查关键依赖（跳过Windows专用的wxauto）
    python3 -c "import feedparser, requests, schedule, openai" 2>/dev/null
    if [ $? -ne 0 ]; then
        print_error "Python依赖不完整"
        print_info "请运行以下命令安装依赖:"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            print_info "  pip install -r requirements-windows.txt"
        else
            print_info "  pip install -r requirements-linux.txt"
        fi
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 获取进程ID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        echo ""
    fi
}

# 检查服务是否运行
is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 启动服务
start_service() {
    print_info "启动 $SERVICE_NAME 服务..."
    
    # 检查是否已经运行
    if is_running; then
        local pid=$(get_pid)
        print_warning "服务已经在运行中 (PID: $pid)"
        return 1
    fi
    
    # 检查环境和依赖
    check_env
    check_dependencies
    
    # 切换到脚本目录
    cd "$SCRIPT_DIR"
    
    # 启动服务
    nohup python3 "$PYTHON_SCRIPT" > "$LOG_FILE" 2> "$ERROR_LOG" &
    local pid=$!
    
    # 等待一下确认启动成功
    sleep 2
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "$pid" > "$PID_FILE"
        print_success "服务启动成功 (PID: $pid)"
        print_info "日志文件: $LOG_FILE"
        print_info "错误日志: $ERROR_LOG"
        print_info "使用 './start.sh status' 查看状态"
        print_info "使用 './start.sh logs' 查看日志"
    else
        print_error "服务启动失败"
        print_info "错误信息:"
        cat "$ERROR_LOG"
        exit 1
    fi
}

# 停止服务
stop_service() {
    print_info "停止 $SERVICE_NAME 服务..."
    
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        print_warning "服务未运行"
        return 1
    fi
    
    if ! kill -0 "$pid" 2>/dev/null; then
        print_warning "进程 $pid 不存在，清理PID文件"
        rm -f "$PID_FILE"
        return 1
    fi
    
    # 发送TERM信号
    kill -TERM "$pid" 2>/dev/null
    
    # 等待进程结束
    local count=0
    while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
        print_info "等待进程结束... ($count/10)"
    done
    
    # 如果进程仍在运行，强制杀死
    if kill -0 "$pid" 2>/dev/null; then
        print_warning "进程未正常结束，强制终止"
        kill -KILL "$pid" 2>/dev/null
        sleep 1
    fi
    
    # 清理PID文件
    rm -f "$PID_FILE"
    print_success "服务已停止"
}

# 重启服务
restart_service() {
    print_info "重启 $SERVICE_NAME 服务..."
    stop_service
    sleep 2
    start_service
}

# 查看服务状态
show_status() {
    print_info "检查 $SERVICE_NAME 服务状态..."
    
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        print_warning "服务未运行"
        return 1
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        print_success "服务正在运行 (PID: $pid)"
        
        # 显示进程信息
        echo ""
        print_info "进程信息:"
        ps -p "$pid" -o pid,ppid,cmd,%cpu,%mem,etime --no-headers
        
        # 显示日志文件大小
        if [ -f "$LOG_FILE" ]; then
            local log_size=$(du -h "$LOG_FILE" | cut -f1)
            print_info "日志文件大小: $log_size"
        fi
        
        if [ -f "$ERROR_LOG" ]; then
            local error_size=$(du -h "$ERROR_LOG" | cut -f1)
            print_info "错误日志大小: $error_size"
        fi
    else
        print_error "PID文件存在但进程不存在，清理PID文件"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 查看日志
show_logs() {
    local lines=${2:-50}
    
    case "${1:-normal}" in
        "error")
            if [ -f "$ERROR_LOG" ]; then
                print_info "错误日志 (最后 $lines 行):"
                tail -n "$lines" "$ERROR_LOG"
            else
                print_warning "错误日志文件不存在"
            fi
            ;;
        "follow")
            if [ -f "$LOG_FILE" ]; then
                print_info "实时跟踪日志 (按 Ctrl+C 退出):"
                tail -f "$LOG_FILE"
            else
                print_warning "日志文件不存在"
            fi
            ;;
        *)
            if [ -f "$LOG_FILE" ]; then
                print_info "普通日志 (最后 $lines 行):"
                tail -n "$lines" "$LOG_FILE"
            else
                print_warning "日志文件不存在"
            fi
            ;;
    esac
}

# 清理日志
clean_logs() {
    print_info "清理日志文件..."
    
    if [ -f "$LOG_FILE" ]; then
        > "$LOG_FILE"
        print_success "已清理普通日志"
    fi
    
    if [ -f "$ERROR_LOG" ]; then
        > "$ERROR_LOG"
        print_success "已清理错误日志"
    fi
}

# 显示帮助信息
show_help() {
    echo "微信RSS新闻推送服务管理脚本"
    echo ""
    echo "用法: $0 {start|stop|restart|status|logs|clean|help}"
    echo ""
    echo "命令说明:"
    echo "  start    - 启动服务"
    echo "  stop     - 停止服务"
    echo "  restart  - 重启服务"
    echo "  status   - 查看服务状态"
    echo "  logs     - 查看日志"
    echo "    logs [error|follow] [行数] - 查看错误日志或实时跟踪"
    echo "  clean    - 清理日志文件"
    echo "  help     - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start              # 启动服务"
    echo "  $0 logs follow        # 实时查看日志"
    echo "  $0 logs error 100     # 查看最后100行错误日志"
}

# 主函数
main() {
    case "${1:-help}" in
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2" "$3"
            ;;
        "clean")
            clean_logs
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
