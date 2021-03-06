# coding:utf-8

"""
ecn 实验常用工具类
"""
import os
import re
from time import sleep
from mininet.log import info, debug
from mininet.link import Link, TCLink, TCIntf
from mininet.node import OVSSwitch
from mininet.util import pmonitor
import ecn_qdisc_helper


class ECNLink(TCLink):
    def __init__(self, node1, node2, port1=None, port2=None,
                 intf_name1=None, intf_name2=None,
                 addr1=None, addr2=None, **params):
        Link.__init__(self, node1, node2, port1=port1, port2=port2,
                      intfName1=intf_name1, intfName2=intf_name2,
                      cls1=ECNIntf,
                      cls2=ECNIntf,
                      addr1=addr1, addr2=addr2,
                      params1=params,
                      params2=params)


class ECNIntf(TCIntf):
    def change_queue_len(self, tx_queue_len=200):
        # LOG.debug("  调整 %s 网络 队列长度 txqueuelen " )
        ecn_qdisc_helper.os_popen("sudo ip link set txqueuelen %s dev %s" % (tx_queue_len, self.name))
        # print " 检查设置: ifconfig | grep txqueuelen"

    def default_config(self, bw=50, queue_len=100):
        self.change_queue_len()  # 设置默认队列大小
        ecn_qdisc_helper.port_default_config(self.name, bw=bw, tx_queue_len=queue_len)

    def change_latency(self, delay):
        ecn_qdisc_helper.handle_change_netem(self.name, delay=delay)
        pass

    def change_red(self, bw=10, minmax="min 30000 max 35000 avpkt 1500"):
        ecn_qdisc_helper.handle_change_red(self.name, bw=bw, minmax=minmax)
        # pass
        # def config(self, **params):
        #    pass
        # super(TCIntf, self).config(params)


def base_setup_queue_and_latency(network, bw=50, queue_len=200, latency=50, ecn=True,
                                 redminmax="min 30000 max 35000 avpkt 1500"):
    """
    队列和延时的基础设置
    设置网卡的 queue 和 filter 状态, 包括带宽, qlen, 延时, red ecn 策略等
    检测 change_latency 接口的 netem 状态:
      watch -n 0.1 tc -s -d qdisc show dev s3-eth2 / s4-eth2
    检测 change_red 接口的 red 状态:
      watch -n 0.2 tc -s qdisc show dev s1-eth3 / s2-eth3

    :param network:
    :param bw:
    :param queue_len:
    :param latency:
    :param ecn:
    :param redminmax:
    :return:
    """
    info("* setup_queue_and_filter() ... \n")
    latency = str(latency) + "ms"
    for sw in network.switches:
        assert isinstance(sw, OVSSwitch)
        for p in sw.ports:  # 修改所有的 ECNIntf
            if isinstance(p, ECNIntf):
                debug(type(p), p.name, p.bwParamMax, p.params, "\n")
                p.default_config(bw=bw, queue_len=queue_len)

        for intf1, intf2 in network.topo.get_link_intfs(network, "s3", "s4"):
            debug("change latency %s %s to %s" % (intf1, intf2, latency))
            intf1.change_latency(latency)
            intf2.change_latency(latency)
        if ecn:
            for intf1, intf2 in network.topo.get_link_intfs(network, "s1", "s3"):
                debug("change red %s %s to %s" % (intf1, intf2, "red"))
                intf1.change_red(bw=bw, minmax=redminmax)
                intf2.change_red(bw=bw, minmax=redminmax)


def dump_result(results):
    """
    打印测试结果
    :param results:
    :return:
    """
    fmt = '%s \n%s\n!!!'

    print(fmt % ('-测试name ', ' 测试result-'))

    for param in sorted(results.keys()):
        entries = results[param]
        # for e in entries:
        print(fmt % (param, entries))
        # print("!!!")  # 分割符


def mesure_ping_and_netperf(network, round_count=1, round_duration=5,
                            ping_interval=1.0, ping=True, netperf=True,
                            ovs_helper=False, qmin=50000,
                            ecn_tcp_flag=False, ovs_helper_wait=10
                            ):
    """
    h1 执行 ping 测试延时
    h2 执行 netperf 测试带宽利用率
    :param qmin:          queue min 监控大小
    :param ovs_helper:  使用 ovs_helper.py 控制 ecn
    :param ecn_tcp_flag : 使用ecn tcp 或 ip 控制
    :param network: mininet class
    :param round_count:    循环次数
    :param round_duration: 循环时间每轮
    :param ping_interval:  ping包采样间隔
    :param ping:        ping测试开关
    :param netperf:     netperf测试开关
    :param ovs_helper_wait:       ovs_helper_wait 时延, 让helper / netperf 的启动时间覆盖整个实验运行
    :return:
    """
    result = ""
    h1 = network.get("h1")
    h2 = network.get("h2")
    s1 = network.get("s1")
    popens = {}

    # 运行时间 ovs_helper > netperf > ping
    ping_cmd = "ping -c%s -i%s h3 " % (int(round_duration / ping_interval), ping_interval)
    netperf_cmd = "netperf -H h3 -l %s " % str(round_duration + ovs_helper_wait / 2)  # 附加wait秒时延, 考虑大于 ping 时延
    if ecn_tcp_flag:
        ecn_sub_cmd = "ecn_tcp"
    else:
        ecn_sub_cmd = "ecn_ip"
    ovs_openflow_cmd = "/opt/mininet/cuc/ecn_ovs_helper.py start %s %s %s" \
                       % (ecn_sub_cmd, qmin, round_duration + ovs_helper_wait)  # 附加wait秒时延, 考虑 netperf 启动
    # rr_cmd = "netperf -H h3 -l %s -t TCPRR " % round_duration
    # cmds = "%s;\n%s;\n%s" % (output_cmd, rr_cmd, ping_cmd)

    sleep(3)  # wait 2 second to reach tcp max output

    # 启动顺序 ovs_helper > netperf > ping
    for r in range(round_count):
        print ("*** ROUND %s" % r)
        if ovs_helper:  # ovs helper 优先
            for h in [s1]:
                this_cmd = "<%s>: popen cmd: %s \n" % (h.name, ovs_openflow_cmd)
                info(this_cmd)
                result += this_cmd
                popens[h] = h.popen(ovs_openflow_cmd)
        if netperf:
            for h in [h2]:  # 背景流量优先
                this_cmd = "<%s>: popen cmd: %s \n" % (h.name, netperf_cmd)
                info(this_cmd)
                result += this_cmd
                popens[h] = h.popen(netperf_cmd)
        if ping:
            for h in [h1]:  # 最后运行ping
                this_cmd = "<%s>: popen cmd: %s \n" % (h.name, ping_cmd)
                info(this_cmd)
                result += this_cmd
                popens[h] = h.popen(ping_cmd)

        log_line_count = 0
        # Monitor them and print output
        # 在 pmoniter中运行的程序,  print 结果会直接回显在屏幕上
        #    而 info / debug 结果则需要在 result 中得到回显
        for host, line in pmonitor(popens):
            if host:
                log_line_count += 1
                if line.find("icmp_seq") != -1:  # debug ping output
                    debug("<%s>: %s\n" % (host.name, line.strip()))  # suppressed ping output to debug level
                    if (log_line_count % (5 / ping_interval)) == 0:  # every 5 second print line 便于在 info 模式下观察
                        info("<%s>: %s\n" % (host.name, line.strip()))
                elif line.find("debug") != -1:  # debug ecn helper output
                    debug("<%s>: %s\n" % (host.name, line.strip()))
                else:
                    info("<%s>: %s\n" % (host.name, line.strip()))
                    result += "<%s>: %s\n" % (host.name, line.strip())

    return result


def print_mininet_objs(network):
    """
    打印 mininet 网络对象
    :param network:
    :return:
    """
    print "* mininet hosts"
    for host in network.hosts:
        print type(host)
    # for host in net.intf: print type(host)
    print "* mininet switchs"
    for sw in network.switches:
        assert isinstance(sw, OVSSwitch)
        for p in sw.ports:
            if isinstance(p, TCIntf):
                print type(p), p.name, p.bwParamMax, p.params
            else:
                print type(p), p.name
    print "* mininet links"
    for li in network.links:
        assert isinstance(li, TCLink)
        # for p in [li.intf1 , li.intf2]:
        print type(li.intf1), li.intf1.name, "<->", li.intf2.name

    print "* gethostbyname"
    print network.getNodeByName("h1").name

    print "* config and get link status"
    for srcIntf, dstIntf in network.topo.get_link_intfs(network, "s3", "s4"):
        print srcIntf.name, "<->", dstIntf.name
