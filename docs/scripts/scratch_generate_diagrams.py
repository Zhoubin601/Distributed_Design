# -*- coding: utf-8 -*-
"""
生成课程设计报告所需的 6 张高质量架构与流程图表
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# 配置中文字体与基础参数
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = 'assets/diagrams/images'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 统一色彩方案
C_BORDER = '#2c3e50'
C_TEXT = '#1e293b'
C_CLIENT = '#e0f2fe'      # 浅天蓝
C_ACCESS = '#fef3c7'      # 浅琥珀
C_APP = '#dcfce7'         # 浅绿
C_DATA = '#f3e8ff'        # 浅紫
C_WARN = '#fee2e2'        # 浅红
C_BG = '#f8fafc'          # 背景浅灰
C_BOX_STROKE = '#64748b'

def draw_fig1():
    """图 1：系统总体逻辑架构图"""
    fig, ax = plt.subplots(figsize=(10, 6.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 背景大框
    # 1. 客户端层
    r_client = patches.FancyBboxPatch((4, 75), 92, 20, boxstyle="round,pad=1.5", 
                                      facecolor=C_CLIENT, edgecolor=C_BOX_STROKE, linewidth=1.5)
    ax.add_patch(r_client)
    ax.text(6, 91, "客户端层 (浏览器终端)", fontsize=11, fontweight='bold', color='#0369a1')

    # 客户端子节点
    box_host = patches.FancyBboxPatch((10, 78), 35, 11, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#0284c7', linewidth=1.2)
    ax.add_patch(box_host)
    ax.text(27.5, 83.5, "主持人客户端\n(地图配置 / 迷雾控制 / 权限管理)", ha='center', va='center', fontsize=9.5, color=C_TEXT)

    box_player = patches.FancyBboxPatch((55, 78), 35, 11, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#0284c7', linewidth=1.2)
    ax.add_patch(box_player)
    ax.text(72.5, 83.5, "玩家客户端 (多端接入)\n(标记协同移动 / 掷骰 / 授权视野交互)", ha='center', va='center', fontsize=9.5, color=C_TEXT)

    # 2. 接入层
    r_access = patches.FancyBboxPatch((4, 52), 92, 16, boxstyle="round,pad=1.5", 
                                      facecolor=C_ACCESS, edgecolor=C_BOX_STROKE, linewidth=1.5)
    ax.add_patch(r_access)
    ax.text(6, 64.5, "接入与协议适配层", fontsize=11, fontweight='bold', color='#b45309')

    box_rest = patches.FancyBboxPatch((10, 54.5), 35, 9, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#d97706', linewidth=1.2)
    ax.add_patch(box_rest)
    ax.text(27.5, 59, "HTTPS / REST API 网关\n(房间创建 / 加入申请 / 元数据查询)", ha='center', va='center', fontsize=9.5, color=C_TEXT)

    box_ws = patches.FancyBboxPatch((55, 54.5), 35, 9, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#d97706', linewidth=1.2)
    ax.add_patch(box_ws)
    ax.text(72.5, 59, "WebSocket 双向网关集群\n(长连接维系 / 心跳检测 / 增量事件投递)", ha='center', va='center', fontsize=9.5, color=C_TEXT)

    # 3. 应用与协作层
    r_app = patches.FancyBboxPatch((4, 25), 92, 21, boxstyle="round,pad=1.5", 
                                   facecolor=C_APP, edgecolor=C_BOX_STROKE, linewidth=1.5)
    ax.add_patch(r_app)
    ax.text(6, 42.5, "应用与房间协作服务层", fontsize=11, fontweight='bold', color='#15803d')

    box_auth = patches.FancyBboxPatch((8, 28), 24, 11, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#16a34a', linewidth=1.2)
    ax.add_patch(box_auth)
    ax.text(20, 33.5, "身份与权限校验\n(Token验证 / 角色鉴权\n迷雾视野投影过滤)", ha='center', va='center', fontsize=9, color=C_TEXT)

    box_room = patches.FancyBboxPatch((36, 28), 28, 11, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#16a34a', linewidth=1.2)
    ax.add_patch(box_room)
    ax.text(50, 33.5, "房间协作核心 (Room Coordinator)\n(单房间操作串行排队\n权威序号生成 / 版本冲突检测)", ha='center', va='center', fontsize=9, color=C_TEXT)

    box_pub = patches.FancyBboxPatch((68, 28), 24, 11, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#16a34a', linewidth=1.2)
    ax.add_patch(box_pub)
    ax.text(80, 33.5, "事件广播与分发组件\n(已持久化事件读取\n按成员权限差分广播)", ha='center', va='center', fontsize=9, color=C_TEXT)

    # 4. 数据与存储层
    r_data = patches.FancyBboxPatch((4, 2), 92, 17, boxstyle="round,pad=1.5", 
                                    facecolor=C_DATA, edgecolor=C_BOX_STROKE, linewidth=1.5)
    ax.add_patch(r_data)
    ax.text(6, 15.5, "持久化与基础设施层", fontsize=11, fontweight='bold', color='#6b21a8')

    box_pg = patches.FancyBboxPatch((8, 4.5), 36, 9.5, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#9333ea', linewidth=1.2)
    ax.add_patch(box_pg)
    ax.text(26, 9.2, "PostgreSQL 关系型权威存储\n(房间状态 / 增量事件表 / 幂等操作表 / 快照)", ha='center', va='center', fontsize=8.8, color=C_TEXT)

    box_redis = patches.FancyBboxPatch((48, 4.5), 24, 9.5, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#9333ea', linewidth=1.2)
    ax.add_patch(box_redis)
    ax.text(60, 9.2, "Redis 内存缓存集群\n(在线成员状态 / 房间节点路由\n瞬态事件通知 Pub/Sub)", ha='center', va='center', fontsize=8.8, color=C_TEXT)

    box_obj = patches.FancyBboxPatch((76, 4.5), 16, 9.5, boxstyle="round,pad=0.8", facecolor='white', edgecolor='#9333ea', linewidth=1.2)
    ax.add_patch(box_obj)
    ax.text(84, 9.2, "静态资源存储\n(系统预置地图资源\n无用户上传流程)", ha='center', va='center', fontsize=8.5, color=C_TEXT)

    # 绘制连接箭头
    arrow_kw = dict(arrowstyle="<->", color='#334155', lw=1.3, shrinkA=3, shrinkB=3)
    arrow_down = dict(arrowstyle="->", color='#334155', lw=1.3, shrinkA=3, shrinkB=3)
    
    # 客户端 <-> 接入层
    ax.annotate("", xy=(27.5, 63.5), xytext=(27.5, 78), arrowprops=arrow_kw)
    ax.annotate("", xy=(72.5, 63.5), xytext=(72.5, 78), arrowprops=arrow_kw)
    
    # 接入层 <-> 应用层
    ax.annotate("", xy=(27.5, 39), xytext=(27.5, 54.5), arrowprops=arrow_kw)
    ax.annotate("", xy=(65, 39), xytext=(72.5, 54.5), arrowprops=arrow_kw)
    
    # 应用层内部
    ax.annotate("", xy=(36, 33.5), xytext=(32, 33.5), arrowprops=dict(arrowstyle="->", color='#16a34a', lw=1.2))
    ax.annotate("", xy=(68, 33.5), xytext=(64, 33.5), arrowprops=dict(arrowstyle="->", color='#16a34a', lw=1.2))

    # 应用层 <-> 数据层
    ax.annotate("", xy=(26, 14), xytext=(40, 28), arrowprops=arrow_kw)
    ax.annotate("", xy=(60, 14), xytext=(60, 28), arrowprops=arrow_kw)
    ax.annotate("", xy=(84, 14), xytext=(80, 28), arrowprops=arrow_down)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_logical_architecture.png'), bbox_inches='tight')
    plt.close()
    print("图 1 生成成功")

def draw_fig2():
    """图 2：多房间分配与并行处理拓扑图"""
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 客户端组
    c_box = patches.FancyBboxPatch((5, 72), 90, 22, boxstyle="round,pad=1.2", facecolor=C_CLIENT, edgecolor=C_BOX_STROKE, lw=1.3)
    ax.add_patch(c_box)
    ax.text(7, 90, "并发接入的客户端集合 (约 100 个活跃房间设计假设)", fontsize=10.5, fontweight='bold', color='#0369a1')

    b1 = patches.FancyBboxPatch((8, 75), 25, 12, boxstyle="round,pad=0.5", facecolor='white', edgecolor='#0284c7', lw=1.1)
    ax.add_patch(b1)
    ax.text(20.5, 81, "房间 101 成员 (2~8人)\n[客户端 C1, C2, C3]", ha='center', va='center', fontsize=9)

    b2 = patches.FancyBboxPatch((37.5, 75), 25, 12, boxstyle="round,pad=0.5", facecolor='white', edgecolor='#0284c7', lw=1.1)
    ax.add_patch(b2)
    ax.text(50, 81, "房间 102 成员 (2~8人)\n[客户端 C4, C5]", ha='center', va='center', fontsize=9)

    b3 = patches.FancyBboxPatch((67, 75), 25, 12, boxstyle="round,pad=0.5", facecolor='white', edgecolor='#0284c7', lw=1.1)
    ax.add_patch(b3)
    ax.text(79.5, 81, "房间 201 成员 (2~8人)\n[客户端 C6, C7, C8]", ha='center', va='center', fontsize=9)

    # 接入层与路由
    gw_box = patches.FancyBboxPatch((5, 48), 90, 16, boxstyle="round,pad=1.2", facecolor=C_ACCESS, edgecolor=C_BOX_STROKE, lw=1.3)
    ax.add_patch(gw_box)
    ax.text(7, 60.5, "网关层 (无状态负载均衡与一致性会话哈希路由)", fontsize=10.5, fontweight='bold', color='#b45309')

    gw1 = patches.FancyBboxPatch((15, 50.5), 30, 9, boxstyle="round,pad=0.5", facecolor='white', edgecolor='#d97706', lw=1.1)
    ax.add_patch(gw1)
    ax.text(30, 55, "网关节点 A\n(维系长连接 / 路由会话映射)", ha='center', va='center', fontsize=9)

    gw2 = patches.FancyBboxPatch((55, 50.5), 30, 9, boxstyle="round,pad=0.5", facecolor='white', edgecolor='#d97706', lw=1.1)
    ax.add_patch(gw2)
    ax.text(70, 55, "网关节点 B\n(维系长连接 / 路由会话映射)", ha='center', va='center', fontsize=9)

    # 房间服务实例
    app_box = patches.FancyBboxPatch((5, 20), 90, 21, boxstyle="round,pad=1.2", facecolor=C_APP, edgecolor=C_BOX_STROKE, lw=1.3)
    ax.add_patch(app_box)
    ax.text(7, 37.5, "协作服务集群 (房间级权威划分，不同房间完全并行)", fontsize=10.5, fontweight='bold', color='#15803d')

    s1 = patches.FancyBboxPatch((10, 23), 36, 12.5, boxstyle="round,pad=0.6", facecolor='white', edgecolor='#16a34a', lw=1.2)
    ax.add_patch(s1)
    ax.text(28, 29.2, "房间服务实例 1 (Worker 1)\n★ 权威接管：房间 101, 房间 102\n[单房间内部操作严格串行定序]", ha='center', va='center', fontsize=9)

    s2 = patches.FancyBboxPatch((54, 23), 36, 12.5, boxstyle="round,pad=0.6", facecolor='white', edgecolor='#16a34a', lw=1.2)
    ax.add_patch(s2)
    ax.text(72, 29.2, "房间服务实例 2 (Worker 2)\n★ 权威接管：房间 201 及其他房间\n[单房间内部操作严格串行定序]", ha='center', va='center', fontsize=9)

    # 存储底座
    db_box = patches.FancyBboxPatch((5, 2), 90, 13, boxstyle="round,pad=1.2", facecolor=C_DATA, edgecolor=C_BOX_STROKE, lw=1.3)
    ax.add_patch(db_box)
    ax.text(7, 11.5, "共享权威存储层 (PostgreSQL 数据库集群 + Redis 路由表)", fontsize=10.5, fontweight='bold', color='#6b21a8')
    ax.text(50, 6, "共享数据底座：强事务保证单房间操作持久化提交，支持服务崩溃后的快照恢复与安全接管", ha='center', va='center', fontsize=9.2, color='#475569')

    # 连线
    ak = dict(arrowstyle="->", color='#475569', lw=1.2)
    ax.annotate("", xy=(25, 59.5), xytext=(20.5, 75), arrowprops=ak)
    ax.annotate("", xy=(35, 59.5), xytext=(50, 75), arrowprops=ak)
    ax.annotate("", xy=(70, 59.5), xytext=(79.5, 75), arrowprops=ak)

    ax.annotate("", xy=(28, 35.5), xytext=(30, 50.5), arrowprops=ak)
    ax.annotate("", xy=(32, 35.5), xytext=(65, 50.5), arrowprops=ak)
    ax.annotate("", xy=(72, 35.5), xytext=(70, 50.5), arrowprops=ak)

    ax.annotate("", xy=(28, 15), xytext=(28, 23), arrowprops=dict(arrowstyle="<->", color='#9333ea', lw=1.2))
    ax.annotate("", xy=(72, 15), xytext=(72, 23), arrowprops=dict(arrowstyle="<->", color='#9333ea', lw=1.2))

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_room_assignment.png'), bbox_inches='tight')
    plt.close()
    print("图 2 生成成功")

def draw_fig3():
    """图 3：移动标记的权威提交与状态传播时序图"""
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 泳道角色
    roles = [
        (12, "操作玩家客户端\n(Player A)"),
        (35, "接入网关\n(Gateway)"),
        (58, "房间协作服务\n(Room Coordinator)"),
        (80, "持久化存储\n(PostgreSQL)"),
        (94, "其他同房间成员\n(Other Players)")
    ]

    for x, name in roles:
        box = patches.FancyBboxPatch((x-6, 88), 12, 9, boxstyle="round,pad=0.3", facecolor=C_BG, edgecolor=C_BOX_STROKE, lw=1.1)
        ax.add_patch(box)
        ax.text(x, 92.5, name, ha='center', va='center', fontsize=8.5, fontweight='bold')
        ax.plot([x, x], [10, 88], color='#cbd5e1', linestyle='--', lw=1.2)

    def draw_msg(y, x1, x2, text, is_dotted=False, color='#2563eb', note=""):
        ls = '--' if is_dotted else '-'
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.3, linestyle=ls))
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y + 1.8, text, ha='center', va='bottom', fontsize=8.2, color=C_TEXT)
        if note:
            ax.text(mid_x, y - 2.2, note, ha='center', va='top', fontsize=7.5, color='#64748b', style='italic')

    # 1. 客户端提交请求
    draw_msg(80, 12, 35, "1. 提交移动请求 (token_id, pos, base_version)")
    draw_msg(73, 35, 58, "2. 转发认证请求 (附带验证后的会话身份)")

    # 房间服务自校验激活框
    act1 = patches.Rectangle((56.8, 60), 2.4, 11, facecolor='#bbf7d0', edgecolor='#16a34a', lw=1)
    ax.add_patch(act1)
    ax.text(58, 65.5, "权限核验\n版本有效性校验\n操作串行排队", ha='center', va='center', fontsize=7.5, color='#14532d')

    # 3. 提交事务
    draw_msg(55, 58, 80, "3. 开启原子事务：写入状态更新并生成递增序号 seq", color='#9333ea')
    draw_msg(47, 80, 58, "4. 事务提交成功 (Commit OK)", is_dotted=True, color='#9333ea')

    # 4. 确认响应与广播
    draw_msg(39, 58, 35, "5. 返回权威操作确认 (附带新版本号与 seq)")
    draw_msg(32, 35, 12, "6. 返回操作成功响应 (客户端转为权威确认状态)")

    # 5. 向其他成员广播
    draw_msg(24, 58, 94, "7. 经战争迷雾视野过滤后，广播增量更新事件", color='#059669',
             note="[关键原则] 隐藏信息由服务端过滤；单次广播不保证绝对送达，依赖恢复机制保底")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_token_operation_sequence.png'), bbox_inches='tight')
    plt.close()
    print("图 3 生成成功")

def draw_fig4():
    """图 4：同一标记并发移动冲突与版本处理流程图"""
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 起始输入
    p_a = patches.FancyBboxPatch((8, 82), 35, 11, boxstyle="round,pad=0.6", facecolor=C_CLIENT, edgecolor='#0284c7', lw=1.2)
    ax.add_patch(p_a)
    ax.text(25.5, 87.5, "玩家 A 请求移动标记 T\n(基准版本 base_version = 10, 目标坐标 X)", ha='center', va='center', fontsize=9)

    p_b = patches.FancyBboxPatch((57, 82), 35, 11, boxstyle="round,pad=0.6", facecolor=C_CLIENT, edgecolor='#0284c7', lw=1.2)
    ax.add_patch(p_b)
    ax.text(74.5, 87.5, "玩家 B 几乎同时请求移动标记 T\n(基准版本 base_version = 10, 目标坐标 Y)", ha='center', va='center', fontsize=9)

    # 房间服务排队与定序
    q_box = patches.FancyBboxPatch((20, 62), 60, 11, boxstyle="round,pad=0.6", facecolor=C_APP, edgecolor='#16a34a', lw=1.3)
    ax.add_patch(q_box)
    ax.text(50, 67.5, "房间服务权威排队处理机制\n(以服务端到达顺序建立排他锁/串行事务，假设玩家 A 先获得处理)", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#14532d')

    # 分支判断
    # 路径 A
    box_ok = patches.FancyBboxPatch((5, 33), 42, 18, boxstyle="round,pad=0.6", facecolor='#f0fdf4', edgecolor='#22c55e', lw=1.2)
    ax.add_patch(box_ok)
    ax.text(26, 46, "【先达请求 A 处理过程】\n1. 检查标记当前版本 == 10 (匹配)\n2. 校验玩家 A 具备该标记操控权限\n3. 更新标记位置为 X，版本自增为 11\n4. 提交持久化事务，生成房间全局序号\n5. 向全房间广播更新事件 (version: 11)", ha='left', va='center', fontsize=8.2, color='#14532d')

    # 路径 B (冲突)
    box_fail = patches.FancyBboxPatch((53, 33), 42, 18, boxstyle="round,pad=0.6", facecolor=C_WARN, edgecolor='#ef4444', lw=1.2)
    ax.add_patch(box_fail)
    ax.text(74, 46, "【后达请求 B 处理过程】\n1. 检查标记当前版本 (此时已变为 11)\n2. 对比请求 base_version (10 != 11)\n3. 判定发生并发过期修改冲突 (Conflict)\n4. 拒绝写操作，回滚临时事务\n5. 向玩家 B 显式返回 409 冲突与最新状态", ha='left', va='center', fontsize=8.2, color='#991b1b')

    # 最终结果
    res_box = patches.FancyBboxPatch((15, 6), 70, 15, boxstyle="round,pad=0.6", facecolor=C_BG, edgecolor=C_BOX_STROKE, lw=1.2)
    ax.add_patch(res_box)
    ax.text(50, 13.5, "【最终状态一致性收敛】\n• 玩家 A 客户端收到权威成功响应，标记正式就位；全房间在线成员收到位置 X 同步\n• 玩家 B 客户端捕获冲突响应，撤销本地预先拖动预览，自动拉回至位置 X 并向用户弹出提示\n• 系统无需依赖高开销的分布式互斥锁或多轮 Paxos 投票，保证状态绝对不出现静默覆盖", ha='center', va='center', fontsize=8.6, color=C_TEXT)

    # 连线
    ak = dict(arrowstyle="->", color='#475569', lw=1.2)
    ax.annotate("", xy=(35, 73), xytext=(25.5, 82), arrowprops=ak)
    ax.annotate("", xy=(65, 73), xytext=(74.5, 82), arrowprops=ak)

    ax.annotate("", xy=(26, 51), xytext=(35, 62), arrowprops=dict(arrowstyle="->", color='#16a34a', lw=1.3))
    ax.text(24, 57, "首先处理", fontsize=8, color='#16a34a', fontweight='bold')

    ax.annotate("", xy=(74, 51), xytext=(65, 62), arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.3))
    ax.text(73, 57, "后续处理", fontsize=8, color='#dc2626', fontweight='bold')

    ax.annotate("", xy=(35, 21), xytext=(26, 33), arrowprops=ak)
    ax.annotate("", xy=(65, 21), xytext=(74, 33), arrowprops=ak)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig4_concurrent_token_moves.png'), bbox_inches='tight')
    plt.close()
    print("图 4 生成成功")

def draw_fig5():
    """图 5：战争迷雾与角色权限状态投影图"""
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 服务端权威真实数据
    raw_box = patches.FancyBboxPatch((5, 45), 30, 45, boxstyle="round,pad=0.8", facecolor='#f1f5f9', edgecolor='#475569', lw=1.4)
    ax.add_patch(raw_box)
    ax.text(20, 84, "服务端权威内部状态\n(完整客观数据模型)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1e293b')
    
    items = [
        "• 预置底图整体布局及全部网格",
        "• 主持人布置的未探索战争迷雾区域",
        "• 玩家角色标记 P1, P2 (可见)",
        "• 潜藏在迷雾中的怪物标记 M1, M2",
        "• 隐藏机关与主持人私密笔记",
        "• 房间全局事件序列自增日志"
    ]
    for i, it in enumerate(items):
        ax.text(7.5, 75 - i*7, it, fontsize=8.2, color='#334155')

    # 核心投影过滤引擎
    eng_box = patches.FancyBboxPatch((42, 45), 18, 45, boxstyle="round,pad=0.8", facecolor=C_APP, edgecolor='#16a34a', lw=1.4)
    ax.add_patch(eng_box)
    ax.text(51, 67.5, "服务端权限\n与视野投影引擎\n\n(State\nProjection\nEngine)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#14532d')
    ax.text(51, 52, "执行规则：\n1. 鉴别连接者角色\n2. 依据视野多边形剪裁\n3. 剥离敏感对象属性\n4. 杜绝前端隐藏漏洞", ha='center', va='center', fontsize=7.8, color='#166534')

    # 投影输出：主持人视图
    h_box = patches.FancyBboxPatch((67, 68), 30, 24, boxstyle="round,pad=0.8", facecolor='#fef3c7', edgecolor='#d97706', lw=1.2)
    ax.add_patch(h_box)
    ax.text(82, 86, "主持人视角投影 (全知透视视图)", ha='center', va='center', fontsize=9, fontweight='bold', color='#b45309')
    h_items = [
        "(+) 完整高亮底图显示",
        "(+) 迷雾渲染为半透明蒙版",
        "(+) 查阅并控制所有标记 (P1,P2,M1,M2)",
        "(+) 拥有任意拖拽与迷雾擦除修改权限"
    ]
    for i, it in enumerate(h_items):
        ax.text(69, 79 - i*5, it, fontsize=7.8, color='#78350f')

    # 投影输出：玩家视图
    p_box = patches.FancyBboxPatch((67, 36), 30, 26, boxstyle="round,pad=0.8", facecolor='#e0f2fe', edgecolor='#0284c7', lw=1.2)
    ax.add_patch(p_box)
    ax.text(82, 56.5, "玩家视角投影 (有限授权探索视图)", ha='center', va='center', fontsize=9, fontweight='bold', color='#0369a1')
    p_items = [
        "(+) 仅接收已点亮/已探索区域的切片信息",
        "(-) 迷雾遮挡区域在服务端直接剔除 (不传数据)",
        "(-) 隐蔽怪物 M1, M2 的坐标及属性均被丢弃",
        "(+) 仅允许对自己绑定的角色标记发起移动请求",
        "(*) 彻底杜绝审查前端内存查看暗桩作弊"
    ]
    for i, it in enumerate(p_items):
        ax.text(69, 49.5 - i*4.6, it, fontsize=7.6, color='#0c4a6e')

    # 底部说明
    bot_box = patches.FancyBboxPatch((5, 5), 92, 23, boxstyle="round,pad=0.6", facecolor=C_BG, edgecolor=C_BOX_STROKE, lw=1.1)
    ax.add_patch(bot_box)
    ax.text(51, 20.5, "【分布式信息安全与权限隔离原则】", ha='center', va='center', fontsize=9, fontweight='bold', color=C_TEXT)
    bot_text = (
        "1. 零信任客户端原则：战争迷雾绝非前端 CSS 或 Canvas 的视觉遮盖，必须由服务端执行差分过滤投影。\n"
        "2. 状态发布与恢复的一致性：无论是实时 WebSocket 事件推送，还是断线重连拉取全量快照，必须调用统一投影引擎。\n"
        "3. 即使玩家通过浏览器开发者工具断点嗅探网络 WebSocket 数据包，也无法窃取迷雾遮盖下的任何隐藏要素。"
    )
    ax.text(8, 11, bot_text, fontsize=8.2, color='#475569', linespacing=1.4)

    # 箭头
    ak = dict(arrowstyle="->", color='#334155', lw=1.3)
    ax.annotate("", xy=(42, 67.5), xytext=(35, 67.5), arrowprops=ak)
    ax.annotate("", xy=(67, 80), xytext=(60, 72), arrowprops=ak)
    ax.annotate("", xy=(67, 50), xytext=(60, 63), arrowprops=ak)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig5_permission_projection.png'), bbox_inches='tight')
    plt.close()
    print("图 5 生成成功")

def draw_fig6():
    """图 6：客户端断线重连与授权状态恢复流程图"""
    fig, ax = plt.subplots(figsize=(9.8, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 1. 断网与重连
    s1 = patches.FancyBboxPatch((25, 84), 50, 11, boxstyle="round,pad=0.6", facecolor=C_CLIENT, edgecolor='#0284c7', lw=1.2)
    ax.add_patch(s1)
    ax.text(50, 89.5, "客户端检测到底层连接断开并重新建连\n(携带会话凭证、房间 ID 及本地最后确认序号 last_seq)", ha='center', va='center', fontsize=8.8)

    # 2. 鉴权与状态判定
    s2 = patches.FancyBboxPatch((25, 67), 50, 11, boxstyle="round,pad=0.6", facecolor=C_ACCESS, edgecolor='#d97706', lw=1.2)
    ax.add_patch(s2)
    ax.text(50, 72.5, "服务端重新验证身份、房间准入权限与角色合法性\n(提取当前房间权威最新序号 current_seq)", ha='center', va='center', fontsize=8.8)

    # 3. 菱形判定
    diamond = patches.Polygon([[50, 58], [75, 48], [50, 38], [25, 48]], facecolor='#fef08a', edgecolor='#ca8a04', lw=1.2)
    ax.add_patch(diamond)
    ax.text(50, 48, "落后事件跨度\n(current_seq - last_seq)\n是否在增量缓冲阈值内？", ha='center', va='center', fontsize=8.2, fontweight='bold')

    # 4. 增量分支 (左)
    box_inc = patches.FancyBboxPatch((5, 18), 40, 16, boxstyle="round,pad=0.6", facecolor='#f0fdf4', edgecolor='#22c55e', lw=1.2)
    ax.add_patch(box_inc)
    ax.text(25, 26, "【增量差分补发路径 (Delta Sync)】\n• 服务端从增量事件表中查询 (last_seq, current_seq]\n• 经当前迷雾视野过滤后打包有序下发\n• 客户端按序应用缺失事件，补齐画面变化\n• 开销小、网络消耗低，通常耗时 < 500ms", ha='center', va='center', fontsize=7.8, color='#14532d')

    # 5. 全量快照分支 (右)
    box_full = patches.FancyBboxPatch((55, 18), 40, 16, boxstyle="round,pad=0.6", facecolor='#eff6ff', edgecolor='#3b82f6', lw=1.2)
    ax.add_patch(box_full)
    ax.text(75, 26, "【全量快照重置路径 (Snapshot Reset)】\n• 适用于断线过久、事件已被归档或首次加入\n• 服务端生成当前最新授权视图基线快照\n• 客户端重置本地渲染画布，用全量状态覆盖\n• 设计目标保障普通规模房间 5 秒内恢复完成", ha='center', va='center', fontsize=7.8, color='#1e40af')

    # 6. 收敛就绪
    box_ready = patches.FancyBboxPatch((20, 2), 60, 10, boxstyle="round,pad=0.5", facecolor=C_APP, edgecolor='#16a34a', lw=1.2)
    ax.add_patch(box_ready)
    ax.text(50, 7, "同步就绪：客户端向服务端回送确认 ACK，重新转入正常实时协作监听状态", ha='center', va='center', fontsize=8.8, fontweight='bold', color='#14532d')

    # 连线
    ak = dict(arrowstyle="->", color='#475569', lw=1.2)
    ax.annotate("", xy=(50, 78), xytext=(50, 84), arrowprops=ak)
    ax.annotate("", xy=(50, 58), xytext=(50, 67), arrowprops=ak)

    ax.annotate("", xy=(25, 34), xytext=(35, 43), arrowprops=ak)
    ax.text(24, 40, "是 (轻度落后)", fontsize=8, color='#15803d', fontweight='bold')

    ax.annotate("", xy=(75, 34), xytext=(65, 43), arrowprops=ak)
    ax.text(72, 40, "否 (严重断代)", fontsize=8, color='#1d4ed8', fontweight='bold')

    ax.annotate("", xy=(38, 12), xytext=(25, 18), arrowprops=ak)
    ax.annotate("", xy=(62, 12), xytext=(75, 18), arrowprops=ak)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig6_client_reconnect.png'), bbox_inches='tight')
    plt.close()
    print("图 6 生成成功")

if __name__ == '__main__':
    draw_fig1()
    draw_fig2()
    draw_fig3()
    draw_fig4()
    draw_fig5()
    draw_fig6()
    print("所有 6 张图表生成完成！")
