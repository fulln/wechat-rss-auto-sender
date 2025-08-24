#!/bin/bash

# systemd服务安装脚本

SERVICE_NAME="wechat-rss-sender"
SERVICE_FILE="$SERVICE_NAME.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以root权限运行
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请以root权限运行此脚本"
        echo "使用: sudo $0"
        exit 1
    fi
}

# 安装服务
install_service() {
    print_info "安装 $SERVICE_NAME systemd 服务..."
    
    # 检查服务文件是否存在
    if [ ! -f "$SCRIPT_DIR/$SERVICE_FILE" ]; then
        print_error "服务文件 $SERVICE_FILE 不存在"
        exit 1
    fi
    
    # 停止现有服务（如果正在运行）
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_info "停止现有服务..."
        systemctl stop "$SERVICE_NAME"
    fi
    
    # 复制服务文件
    cp "$SCRIPT_DIR/$SERVICE_FILE" "/etc/systemd/system/"
    
    # 重新加载systemd
    systemctl daemon-reload
    
    # 启用服务（开机自启动）
    systemctl enable "$SERVICE_NAME"
    
    print_info "服务安装完成！"
    echo ""
    print_info "可用命令："
    echo "  启动服务: sudo systemctl start $SERVICE_NAME"
    echo "  停止服务: sudo systemctl stop $SERVICE_NAME"
    echo "  重启服务: sudo systemctl restart $SERVICE_NAME"
    echo "  查看状态: sudo systemctl status $SERVICE_NAME"
    echo "  查看日志: sudo journalctl -u $SERVICE_NAME -f"
    echo "  禁用开机自启: sudo systemctl disable $SERVICE_NAME"
    echo ""
}

# 卸载服务
uninstall_service() {
    print_info "卸载 $SERVICE_NAME systemd 服务..."
    
    # 停止服务
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_info "停止服务..."
        systemctl stop "$SERVICE_NAME"
    fi
    
    # 禁用服务
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        print_info "禁用服务..."
        systemctl disable "$SERVICE_NAME"
    fi
    
    # 删除服务文件
    if [ -f "/etc/systemd/system/$SERVICE_FILE" ]; then
        rm "/etc/systemd/system/$SERVICE_FILE"
        print_info "删除服务文件"
    fi
    
    # 重新加载systemd
    systemctl daemon-reload
    
    print_info "服务卸载完成！"
}

# 显示帮助
show_help() {
    echo "systemd服务管理脚本"
    echo ""
    echo "用法: sudo $0 {install|uninstall|help}"
    echo ""
    echo "命令说明:"
    echo "  install    - 安装systemd服务"
    echo "  uninstall  - 卸载systemd服务"
    echo "  help       - 显示此帮助信息"
}

# 主函数
main() {
    case "${1:-help}" in
        "install")
            check_root
            install_service
            ;;
        "uninstall")
            check_root
            uninstall_service
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

main "$@"
